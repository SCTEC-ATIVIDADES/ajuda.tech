/**
 * Testes de borda para chatUi.
 *
 * chatUi.test.js (branch fontend) cobre os casos principais.
 * Este arquivo cobre os casos ausentes:
 *   - renderMessages com lista vazia
 *   - renderMessages limpa conteúdo anterior
 *   - Prevenção de XSS via textContent
 *   - showError com chamadas consecutivas
 *   - clearError idempotente
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { renderMessages, showError, clearError } from './chatUi.js';

describe('renderMessages — casos de borda', () => {
  let container;

  beforeEach(() => {
    container = document.createElement('div');
  });

  it('limpa o container quando a lista é vazia', () => {
    container.innerHTML = '<div class="chat-message">antigo</div>';
    renderMessages(container, []);
    expect(container.children).toHaveLength(0);
  });

  it('substitui mensagens anteriores, não acumula', () => {
    renderMessages(container, [{ role: 'bot', text: 'primeira vez' }]);
    renderMessages(container, [{ role: 'user', text: 'segunda vez' }]);

    expect(container.querySelectorAll('.chat-message')).toHaveLength(1);
    expect(container.textContent).toBe('segunda vez');
  });

  it('renderiza uma única mensagem corretamente com content e botão de cópia', () => {
    renderMessages(container, [{ role: 'bot', text: 'só uma' }]);
    expect(container.querySelectorAll('.chat-message')).toHaveLength(1);
    expect(container.querySelector('.chat-message-content')).not.toBeNull();
    expect(container.querySelector('.chat-copy-btn')).not.toBeNull();
  });

  it('escapa HTML — não injeta tags maliciosas (prevenção de XSS)', () => {
    renderMessages(container, [
      { role: 'user', text: '<script>alert("xss")</script>' },
    ]);

    const msg = container.querySelector('.chat-message');
    // textContent deve retornar o texto literal, não o script executado
    expect(msg.textContent).toBe('<script>alert("xss")</script>');
    // O innerHTML não deve conter um elemento <script> real
    expect(container.querySelector('script')).toBeNull();
  });

  it('escapa atributos HTML injetados via texto', () => {
    renderMessages(container, [
      { role: 'user', text: '" onmouseover="alert(1)' },
    ]);

    const msg = container.querySelector('.chat-message');
    expect(msg.textContent).toContain('onmouseover');
    expect(msg.getAttribute('onmouseover')).toBeNull();
  });
});

// ─── showError — casos de borda ───────────────────────────────────────────────

describe('showError — casos de borda', () => {
  let errorEl;

  beforeEach(() => {
    errorEl = document.createElement('p');
    errorEl.hidden = true;
  });

  it('sobrescreve mensagem anterior ao chamar duas vezes', () => {
    showError(errorEl, 'primeiro erro');
    showError(errorEl, 'segundo erro');
    expect(errorEl.textContent).toBe('segundo erro');
    expect(errorEl.hidden).toBe(false);
  });
});

// ─── clearError — idempotência ────────────────────────────────────────────────

describe('clearError — idempotência', () => {
  let errorEl;

  beforeEach(() => {
    errorEl = document.createElement('p');
    errorEl.hidden = true;
    errorEl.textContent = '';
  });

  it('não lança erro ao chamar clearError quando já está oculto', () => {
    expect(() => clearError(errorEl)).not.toThrow();
    expect(errorEl.hidden).toBe(true);
  });

  it('chamar clearError duas vezes não causa estado inconsistente', () => {
    clearError(errorEl);
    clearError(errorEl);
    expect(errorEl.hidden).toBe(true);
    expect(errorEl.textContent).toBe('');
  });
});
