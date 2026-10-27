import { createServer } from 'node:http';
import { readFile, realpath, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, extname, isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';

const mime = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2',
  '.ttf': 'font/ttf', '.map': 'application/json; charset=utf-8',
};

function inside(root, path) {
  const suffix = relative(root, path);
  return suffix !== '..' && !suffix.startsWith('../') && !suffix.startsWith('..\\') && !isAbsolute(suffix);
}

// Only the exported frontend is served. There is deliberately no API proxy.
export function createDemoServer(webRoot) {
  const root = resolve(webRoot);
  return createServer(async (request, response) => {
    response.setHeader('X-Content-Type-Options', 'nosniff');
    function fail(status, message) {
      response.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end(request.method === 'HEAD' ? undefined : message);
    }
    if (!['GET', 'HEAD'].includes(request.method)) {
      response.setHeader('Allow', 'GET, HEAD');
      return fail(405, 'This is a saved-answer demo. No model or API is running.');
    }
    try {
      const url = new URL(request.url, 'http://127.0.0.1');
      const pathname = decodeURIComponent(url.pathname);
      if (pathname.includes('\0')) return fail(400, 'Invalid path.');
      if (pathname === '/api' || pathname.startsWith('/api/')) {
        return fail(404, 'This is a saved-answer demo. Start start-outwise.ps1 for the actual local model.');
      }
      const index = pathname === '/' || pathname === '/index.html';
      if (index && (url.searchParams.get('demo') !== '1' || url.searchParams.get('replay') !== '1')) {
        response.writeHead(302, { Location: '/?demo=1&replay=1' });
        return response.end();
      }
      const target = resolve(root, index ? 'index.html' : `.${pathname}`);
      if (!inside(root, target)) return fail(403, 'Path outside demo export.');
      // Check symlinks too, so a linked file cannot expose repository content.
      const actual = await realpath(target);
      if (!inside(await realpath(root), actual)) return fail(403, 'Path outside demo export.');
      if (!(await stat(actual)).isFile()) return fail(404, 'File not found.');
      const body = request.method === 'HEAD' ? undefined : await readFile(actual);
      response.writeHead(200, {
        'Content-Type': mime[extname(actual).toLowerCase()] || 'application/octet-stream',
        'Cache-Control': 'no-cache',
      });
      response.end(body);
    } catch (error) {
      if (error instanceof URIError || error instanceof TypeError) return fail(400, 'Invalid URL.');
      if (['ENOENT', 'ENOTDIR', 'EISDIR'].includes(error.code)) return fail(404, 'File not found.');
      console.error('Demo request failed:', error.message);
      fail(500, 'Unable to read the local demo export.');
    }
  });
}

function main() {
  const args = process.argv.slice(2);
  const port = args.length === 0 ? 8080 : args.length === 2 && args[0] === '--port' ? Number(args[1]) : NaN;
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Usage: node scripts/serve-demo.mjs [--port 8080]');
  const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '../frontend');
  const expo = resolve(frontend, 'node_modules/expo/bin/cli');
  if (!existsSync(expo)) throw new Error('Install frontend dependencies first: pnpm --dir frontend install --frozen-lockfile');
  console.log('Building the local demo from current frontend source...');
  const build = spawnSync(process.execPath, [expo, 'export', '--platform', 'web'], {
    cwd: frontend, stdio: 'inherit',
    env: { ...process.env, EXPO_OFFLINE: '1', EXPO_NO_TELEMETRY: '1' },
  });
  if (build.error) throw build.error;
  if (build.status !== 0) throw new Error('Frontend build failed. The demo was not started.');
  const server = createDemoServer(resolve(frontend, 'dist'));
  server.on('error', error => {
    console.error(error.code === 'EADDRINUSE' ? `Port ${port} is in use. Try another port: .\\scripts\\start-demo.ps1 -Port 8081` : error.message);
    process.exitCode = 1;
  });
  server.listen(port, '127.0.0.1', () => {
    console.log(`Outwise saved-answer demo: http://127.0.0.1:${port}/?demo=1`);
    console.log('No Python, model or backend is running. Keep this terminal open; press Ctrl+C to stop.');
  });
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.close());
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try { main(); } catch (error) { console.error(error.message); process.exitCode = 1; }
}
