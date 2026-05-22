/**
 * Testes de integração para chatApp.initChatApp.
 *
 * chatApp.js orquestra todos os módulos (state, api, ui, theme).
 * Estes testes verificam o comportamento end-to-end visível ao usuário
 * sem depender de rede — postChatMock é substituído por um stub síncrono.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Intercepta chatApi antes de qualquer import — Vitest hoist automaticamente.
// chatApp.js usa USE_MOCK=false, portanto postChat é sempre chamado em produção/testes.
vi.mock('./chatApi.js', () => ({
  CHAT_ENDPOINT: '/chat/send/',
  postChat: vi.fn().mockResolvedValue({ reply: 'Resposta do assistente' }),
  postChatMock: vi.fn().mockResolvedValue({ reply: 'Resposta do assistente' }),
}));

import { initChatApp } from './chatApp.js';
import { postChat } from './chatApi.js';

// ─── Helpers ──────────────────────────────────────────────────────────────────

const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

const DOM = `
  <button id="chat-theme-toggle" aria-label="Ativar modo escuro"></button>
  <div id="chat-messages"></div>
  <textarea id="chat-input"></textarea>
  <button id="chat-send">Enviar</button>
  <p id="chat-error" hidden></p>
  <p id="chat-typing" hidden>Digitando...</p>
  <button id="chat-new">Nova conversa</button>
`;

// ─── Setup ────────────────────────────────────────────────────────────────────

beforeEach(() => {
  document.body.innerHTML = DOM;
  vi.clearAllMocks();
});

// ─── Inicialização ────────────────────────────────────────────────────────────

describe('inicialização', () => {
  it('exibe mensagem de boas-vindas do Herbert ao abrir o chat', () => {
    initChatApp(document);
    const msgs = document.querySelectorAll('.chat-message');
    expect(msgs).toHaveLength(1);
    expect(msgs[0].textContent).toContain('Herbert');
  });

  it('mensagem de boas-vindas tem classe de bot', () => {
    initChatApp(document);
    expect(document.querySelector('.chat-message--bot')).not.toBeNull();
  });
});

// ─── Validação de mensagem vazia ──────────────────────────────────────────────

describe('mensagem vazia', () => {
  it('exibe erro amigável ao tentar enviar mensagem vazia', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = '';
    document.getElementById('chat-send').click();

    const errorEl = document.getElementById('chat-error');
    expect(errorEl.hidden).toBe(false);
    expect(errorEl.textContent.length).toBeGreaterThan(0);
  });

  it('mensagem de erro não usa jargão técnico', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = '';
    document.getElementById('chat-send').click();

    const errorText = document.getElementById('chat-error').textContent;
    expect(errorText).not.toMatch(/RAM|SSD|processador|GPU/i);
  });

  it('não chama a API ao enviar mensagem vazia', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = '';
    document.getElementById('chat-send').click();

    expect(postChat).not.toHaveBeenCalled();
  });
});

// ─── Envio de mensagem válida (comportamento síncrono) ────────────────────────

describe('envio de mensagem válida — síncrono', () => {
  it('adiciona mensagem do usuário ao chat imediatamente', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'Quero um notebook para estudar';
    document.getElementById('chat-send').click();

    const userMsgs = document.querySelectorAll('.chat-message--user');
    expect(userMsgs).toHaveLength(1);
    expect(userMsgs[0].textContent).toBe('Quero um notebook para estudar');
  });

  it('limpa o campo de texto após envio', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'Preciso de um PC';
    document.getElementById('chat-send').click();

    expect(document.getElementById('chat-input').value).toBe('');
  });

  it('limpa o erro ao enviar mensagem válida após erro anterior', () => {
    initChatApp(document);
    const input = document.getElementById('chat-input');
    const errorEl = document.getElementById('chat-error');

    input.value = '';
    document.getElementById('chat-send').click();
    expect(errorEl.hidden).toBe(false);

    input.value = 'Preciso de um computador';
    document.getElementById('chat-send').click();
    expect(errorEl.hidden).toBe(true);
  });

  it('exibe indicador de digitando enquanto aguarda a resposta', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'Preciso de um computador';
    document.getElementById('chat-send').click();

    expect(document.getElementById('chat-typing').hidden).toBe(false);
  });

  it('desabilita o botão enviar enquanto aguarda resposta', () => {
    initChatApp(document);
    const sendBtn = document.getElementById('chat-send');
    document.getElementById('chat-input').value = 'Preciso de um computador';
    sendBtn.click();

    expect(sendBtn.disabled).toBe(true);
  });
});

// ─── Envio de mensagem válida (comportamento assíncrono) ──────────────────────

describe('envio de mensagem válida — assíncrono', () => {
  it('adiciona resposta do assistente após a API resolver', async () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'Preciso de um computador';
    document.getElementById('chat-send').click();

    await flushPromises();

    const botMsgs = document.querySelectorAll('.chat-message--bot');
    expect(botMsgs.length).toBeGreaterThan(1); // boas-vindas + resposta
  });

  it('oculta indicador de digitando após receber resposta', async () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'Preciso de um computador';
    document.getElementById('chat-send').click();

    await flushPromises();

    expect(document.getElementById('chat-typing').hidden).toBe(true);
  });

  it('reabilita o botão enviar após receber resposta', async () => {
    initChatApp(document);
    const sendBtn = document.getElementById('chat-send');
    document.getElementById('chat-input').value = 'Preciso de um computador';
    sendBtn.click();

    await flushPromises();

    expect(sendBtn.disabled).toBe(false);
  });
});

// ─── Envio via teclado ────────────────────────────────────────────────────────

describe('envio via teclado', () => {
  it('Enter envia a mensagem', () => {
    initChatApp(document);
    const input = document.getElementById('chat-input');

    input.value = '';
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));

    // Mensagem vazia gera erro — confirma que Enter acionou o envio
    expect(document.getElementById('chat-error').hidden).toBe(false);
  });

  it('Shift+Enter não envia a mensagem', () => {
    initChatApp(document);
    const input = document.getElementById('chat-input');

    input.value = '';
    input.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Enter', shiftKey: true, bubbles: true }),
    );

    expect(document.getElementById('chat-error').hidden).toBe(true);
  });
});

// ─── Nova conversa ────────────────────────────────────────────────────────────

describe('botão Nova conversa', () => {
  it('restaura apenas a mensagem de boas-vindas', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'Quero um notebook';
    document.getElementById('chat-send').click();

    document.getElementById('chat-new').click();

    const msgs = document.querySelectorAll('.chat-message');
    expect(msgs).toHaveLength(1);
    expect(msgs[0].textContent).toContain('Herbert');
  });

  it('limpa o campo de texto', () => {
    initChatApp(document);
    document.getElementById('chat-input').value = 'texto pendente';
    document.getElementById('chat-new').click();

    expect(document.getElementById('chat-input').value).toBe('');
  });

  it('limpa o erro visível', () => {
    initChatApp(document);
    const input = document.getElementById('chat-input');

    input.value = '';
    document.getElementById('chat-send').click();
    expect(document.getElementById('chat-error').hidden).toBe(false);

    document.getElementById('chat-new').click();
    expect(document.getElementById('chat-error').hidden).toBe(true);
  });
});

// ─── Comportamento ausente (especificação pendente) ───────────────────────────

describe('tratamento de erro da API', () => {
  it.todo(
    'exibe mensagem de erro ao usuário quando a API retorna falha ' +
      '— chatApp.js não tem catch no handleSend, apenas finally',
  );
});
