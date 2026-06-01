import { describe, it, expect, beforeEach } from 'vitest';
import {
  renderMessages,
  showError,
  clearError,
  setTypingVisible,
  setSendDisabled,
  setInputDisabled,
} from './chatUi.js';

describe('chatUi', () => {
  let container;
  let errorEl;
  let typingEl;
  let sendBtn;
  let inputEl;

  beforeEach(() => {
    document.body.innerHTML = `
      <div id="chat-messages"></div>
      <p id="chat-error" hidden></p>
      <p id="chat-typing" hidden>Digitando...</p>
      <button id="chat-send" type="button">Enviar</button>
      <input id="chat-input" type="text" />
    `;
    container = document.getElementById('chat-messages');
    errorEl = document.getElementById('chat-error');
    typingEl = document.getElementById('chat-typing');
    sendBtn = document.getElementById('chat-send');
    inputEl = document.getElementById('chat-input');
  });

  it('renderMessages creates N elements with user/bot classes', () => {
    renderMessages(container, [
      { role: 'bot', text: 'Olá' },
      { role: 'user', text: 'Oi' },
    ]);
    const items = container.querySelectorAll('.chat-message');
    expect(items).toHaveLength(2);
    expect(items[0].classList.contains('chat-message--bot')).toBe(true);
    expect(items[1].classList.contains('chat-message--user')).toBe(true);
    expect(items[0].querySelector('.chat-message-content').textContent).toBe('Olá');
    expect(items[1].textContent).toBe('Oi');
  });

  it('bot messages use parseMarkdown; user messages use textContent', () => {
    const parseMarkdown = (text) => `<p>${text}</p>`;
    renderMessages(container, [
      { role: 'bot', text: 'Resposta' },
      { role: 'user', text: '<b>usuário</b>' },
    ], parseMarkdown);
    const items = container.querySelectorAll('.chat-message');
    // Bot: innerHTML do content definido pelo parseMarkdown
    expect(items[0].querySelector('.chat-message-content').innerHTML).toBe('<p>Resposta</p>');
    // Usuário: textContent escapado (sem HTML)
    expect(items[1].innerHTML).toBe('&lt;b&gt;usuário&lt;/b&gt;');
  });

  it('bot messages have a copy button', () => {
    renderMessages(container, [{ role: 'bot', text: 'Texto' }]);
    const copyBtn = container.querySelector('.chat-copy-btn');
    expect(copyBtn).not.toBeNull();
    expect(copyBtn.getAttribute('aria-label')).toBe('Copiar mensagem');
  });

  it('copy button writes to clipboard and shows copied state', async () => {
    const written = [];
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: (text) => { written.push(text); return Promise.resolve(); } },
      configurable: true,
    });

    renderMessages(container, [{ role: 'bot', text: 'Copiar isso' }]);
    const copyBtn = container.querySelector('.chat-copy-btn');
    await copyBtn.dispatchEvent(new Event('click'));
    // aguarda a Promise do clipboard
    await Promise.resolve();

    expect(written[0]).toBe('Copiar isso');
    expect(copyBtn.getAttribute('aria-label')).toBe('Copiado!');
    expect(copyBtn.classList.contains('chat-copy-btn--copied')).toBe(true);
  });

  it('user messages do not have a copy button', () => {
    renderMessages(container, [{ role: 'user', text: 'Oi' }]);
    expect(container.querySelector('.chat-copy-btn')).toBeNull();
  });

  it('showError displays text and clears with clearError', () => {
    showError(errorEl, 'Mensagem de erro');
    expect(errorEl.hidden).toBe(false);
    expect(errorEl.textContent).toBe('Mensagem de erro');
    clearError(errorEl);
    expect(errorEl.hidden).toBe(true);
    expect(errorEl.textContent).toBe('');
  });

  it('setTypingVisible toggles visibility', () => {
    setTypingVisible(typingEl, true);
    expect(typingEl.hidden).toBe(false);
    setTypingVisible(typingEl, false);
    expect(typingEl.hidden).toBe(true);
  });

  it('setSendDisabled toggles button disabled state', () => {
    setSendDisabled(sendBtn, true);
    expect(sendBtn.disabled).toBe(true);
    setSendDisabled(sendBtn, false);
    expect(sendBtn.disabled).toBe(false);
  });

  it('setInputDisabled toggles input disabled state', () => {
    setInputDisabled(inputEl, true);
    expect(inputEl.disabled).toBe(true);
    setInputDisabled(inputEl, false);
    expect(inputEl.disabled).toBe(false);
  });
});
