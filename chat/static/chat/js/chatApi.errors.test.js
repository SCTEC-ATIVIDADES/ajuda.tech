/**
 * Testes de tratamento de erro para chatApi.postChat.
 *
 * Os testes em chatApi.test.js cobrem o caminho feliz (HTTP 200).
 * Este arquivo cobre os caminhos de erro ausentes no arquivo original:
 *   - HTTP não-ok (4xx/5xx)
 *   - Falha de rede (fetch rejeita)
 *   - Contrato da constante CHAT_ENDPOINT
 *   - postChatMock retorna formato esperado
 */

import { describe, it, expect, vi } from 'vitest';
import { postChat, postChatMock, CHAT_ENDPOINT } from './chatApi.js';

// ─── CHAT_ENDPOINT ────────────────────────────────────────────────────────────

describe('CHAT_ENDPOINT', () => {
  it('aponta para o endpoint correto do backend', () => {
    expect(CHAT_ENDPOINT).toBe('/chat/send/');
  });
});

// ─── postChat — tratamento de erros HTTP ──────────────────────────────────────

describe('postChat — erros HTTP', () => {
  it('lança erro quando response.ok é false (ex: HTTP 400)', async () => {
    const fetchFn = vi.fn().mockResolvedValue({ ok: false, status: 400 });

    await expect(postChat('oi', 'session-1', { fetchFn })).rejects.toThrow();
  });

  it('lança erro quando response.ok é false (ex: HTTP 429)', async () => {
    const fetchFn = vi.fn().mockResolvedValue({ ok: false, status: 429 });

    await expect(postChat('oi', 'session-1', { fetchFn })).rejects.toThrow();
  });

  it('lança erro quando response.ok é false (ex: HTTP 503)', async () => {
    const fetchFn = vi.fn().mockResolvedValue({ ok: false, status: 503 });

    await expect(postChat('oi', 'session-1', { fetchFn })).rejects.toThrow();
  });

  it('mensagem de erro é amigável e em português', async () => {
    const fetchFn = vi.fn().mockResolvedValue({ ok: false, status: 503 });

    await expect(postChat('oi', 'session-1', { fetchFn })).rejects.toThrow(
      /falha|erro|mensagem/i,
    );
  });
});

// ─── postChat — falha de rede ─────────────────────────────────────────────────

describe('postChat — falha de rede', () => {
  it('propaga o erro quando o fetch lança (sem rede)', async () => {
    const fetchFn = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(postChat('oi', 'session-1', { fetchFn })).rejects.toThrow();
  });
});

// ─── postChat — serialização do corpo ─────────────────────────────────────────

describe('postChat — corpo da requisição', () => {
  it('serializa session_id no corpo mesmo quando null', async () => {
    const fetchFn = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'ok' }),
    });

    await postChat('oi', null, { fetchFn });

    const body = JSON.parse(fetchFn.mock.calls[0][1].body);
    expect(body).toHaveProperty('session_id', null);
  });

  it('serializa message e session_id no corpo', async () => {
    const fetchFn = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'ok' }),
    });

    await postChat('texto do usuário', 'abc-123', { fetchFn });

    const body = JSON.parse(fetchFn.mock.calls[0][1].body);
    expect(body.message).toBe('texto do usuário');
    expect(body.session_id).toBe('abc-123');
  });
});

// ─── postChatMock ─────────────────────────────────────────────────────────────

describe('postChatMock', () => {
  it('retorna objeto com chave message', async () => {
    const result = await postChatMock('qualquer coisa');
    expect(result).toHaveProperty('message');
  });

  it('message é uma string não-vazia', async () => {
    const result = await postChatMock('qualquer coisa');
    expect(typeof result.message).toBe('string');
    expect(result.message.length).toBeGreaterThan(0);
  });

  it('não depende do conteúdo da mensagem enviada', async () => {
    const r1 = await postChatMock('a');
    const r2 = await postChatMock('b');
    expect(r1.message).toBe(r2.message);
  });
});
