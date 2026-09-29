const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

type ChatResponse = {
  answer: string;
};

export async function sendChatMessage(message: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`);
  }

  const body = (await response.json()) as ChatResponse;
  if (typeof body.answer !== 'string' || body.answer.length === 0) {
    throw new Error('Backend returned an invalid response');
  }

  return body.answer;
}
