const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export type ChatSource = {
  title: string;
  name: string;
  url: string;
  license: string;
  content_owner?: string;
  licence_url?: string;
  retrieved_at?: string;
  source_updated_at?: string;
  notice?: string;
};

export type ChatResponse = {
  answer: string;
  sources: ChatSource[];
};

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
  } catch {
    throw new Error(
      'Kunne ikke kontakte den lokale Outwise-serveren. Kontroller at backend kjører.',
    );
  }

  if (!response.ok) {
    let detail = `Backend returnerte status ${response.status}.`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === 'string' && body.detail.length > 0) {
        detail = body.detail;
      }
    } catch {
      // Keep the status-based fallback if the backend did not return JSON.
    }
    throw new Error(detail);
  }

  const body = (await response.json()) as ChatResponse;
  if (
    typeof body.answer !== 'string' ||
    body.answer.length === 0 ||
    !Array.isArray(body.sources)
  ) {
    throw new Error('Backend returned an invalid response');
  }

  return body;
}
