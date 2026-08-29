import { describe, it, expect, vi } from 'vitest';
import { postChat, postChatMock, CHAT_ENDPOINT } from './chatApi.js';

describe('postChat', () => {
  it('posts to the agent endpoint with JSON body', async () => {
    const fetchFn = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ reply: 'Resposta da IA' }),
    });

    const result = await postChat('olá', 'session-123', { fetchFn });

    expect(fetchFn).toHaveBeenCalledWith(CHAT_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'olá', session_id: 'session-123' }),
      credentials: 'include',
    });
    expect(result).toEqual({ reply: 'Resposta da IA' });
  });
});

describe('postChatMock', () => {
  it('returns stub response without network', async () => {
    const result = await postChatMock('olá');
    expect(result.reply).toBeTruthy();
    expect(typeof result.reply).toBe('string');
  });
});
