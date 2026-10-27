import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createDemoServer } from './serve-demo.mjs';

test('standalone replay serves exported files and blocks model/API requests', async t => {
  const temporary = await mkdtemp(join(tmpdir(), 'outwise-demo-'));
  const web = join(temporary, 'dist');
  await mkdir(web);
  await writeFile(join(web, 'index.html'), '<!doctype html><title>Outwise demo</title>');
  await writeFile(join(web, 'app.js'), 'console.log("demo")');
  await writeFile(join(temporary, 'private.txt'), 'must not be served');
  const server = createDemoServer(web);
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  const base = `http://127.0.0.1:${server.address().port}`;
  t.after(async () => { await new Promise(resolve => server.close(resolve)); await rm(temporary, { recursive: true, force: true }); });

  const redirect = await fetch(base, { redirect: 'manual' });
  assert.equal(redirect.status, 302);
  assert.equal(redirect.headers.get('location'), '/?demo=1&replay=1');
  const page = await fetch(`${base}/?demo=1&replay=1`);
  assert.equal(page.status, 200);
  assert.match(await page.text(), /Outwise demo/);
  const script = await fetch(`${base}/app.js`);
  assert.equal(script.headers.get('content-type'), 'text/javascript; charset=utf-8');
  assert.equal(script.headers.get('x-content-type-options'), 'nosniff');
  assert.equal((await fetch(`${base}/app.js`, { method: 'HEAD' })).status, 200);
  assert.equal((await fetch(`${base}/api/status`)).status, 404);
  assert.equal((await fetch(`${base}/api/chat`, { method: 'POST', body: '{}' })).status, 405);
  assert.equal((await fetch(`${base}/missing.js`)).status, 404);
  assert.equal((await fetch(`${base}/..%2fprivate.txt`)).status, 403);
  assert.equal((await fetch(`${base}/%00`)).status, 400);
  assert.equal((await fetch(`${base}/%ZZ`)).status, 400);
});
