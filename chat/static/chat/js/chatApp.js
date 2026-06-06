import { marked } from 'marked';
import DOMPurify from 'dompurify';
import {
  validateMessage,
  createInitialState,
  appendMessage,
  resetConversation,
} from './chatState.js';
import { postChat, postChatMock } from './chatApi.js';

marked.use({ gfm: true, breaks: true });

function parseMarkdown(text) {
  // Garante espaço ao redor de marcadores bold/italic quando adjacentes a chars de palavra,
  // evitando que marked junte palavras como "texto**negrito**outra" → "textonegritooutra".
  const normalized = text
    .replace(/(\w)(\*{1,3}[^*])/g, '$1 $2')
    .replace(/([^*]\*{1,3})(\w)/g, '$1 $2');
  return DOMPurify.sanitize(marked.parse(normalized));
}
import {
  renderMessages,
  showError,
  clearError,
  setTypingVisible,
  setSendDisabled,
  setInputDisabled,
} from './chatUi.js';
import { initTheme } from './chatTheme.js';

const USE_MOCK = false;

export function initChatApp(root = document) {
  initTheme(root.getElementById('chat-theme-toggle'), { document: root });

  const messagesEl = root.getElementById('chat-messages');
  const inputEl = root.getElementById('chat-input');
  const sendBtn = root.getElementById('chat-send');
  const errorEl = root.getElementById('chat-error');
  const typingEl = root.getElementById('chat-typing');
  const newBtn = root.getElementById('chat-new');

  let state = createInitialState();

  function refresh() {
    renderMessages(messagesEl, state.messages, parseMarkdown);
  }

  async function handleSend() {
    const text = inputEl.value;
    const validation = validateMessage(text);

    if (!validation.valid) {
      showError(errorEl, validation.error);
      return;
    }

    clearError(errorEl);
    const userText = text.trim();
    inputEl.value = '';

    state = appendMessage(state, { role: 'user', text: userText });
    refresh();

    setTypingVisible(typingEl, true);
    setSendDisabled(sendBtn, true);
    setInputDisabled(inputEl, true);

    try {
      const response = USE_MOCK
        ? await postChatMock(userText)
        : await postChat(userText, null);
      state = appendMessage(state, { role: 'bot', text: response.reply });
      refresh();
    } catch (err) {
      // Se o servidor retornou a mensagem que falhou, marca a última mensagem do usuário equivalente como 'failed'
      if (err && err.failedMessage) {
        for (let i = state.messages.length - 1; i >= 0; i--) {
          const m = state.messages[i];
          if (m.role === 'user' && m.text === err.failedMessage) {
            state.messages[i] = { ...m, status: 'failed' };
            break;
          }
        }
        refresh();
        showError(errorEl, err.message || 'Não foi possível obter resposta. Tente reenviar.');
      } else {
        showError(errorEl, err.message || 'Não foi possível obter resposta. Tente novamente.');
      }
    } finally {
      setTypingVisible(typingEl, false);
      setSendDisabled(sendBtn, false);
      setInputDisabled(inputEl, false);
      inputEl.focus();
    }
  }

  function handleNewConversation() {
    state = resetConversation();
    clearError(errorEl);
    setTypingVisible(typingEl, false);
    inputEl.value = '';
    refresh();
    inputEl.focus();
  }

  sendBtn.addEventListener('click', handleSend);
  newBtn.addEventListener('click', handleNewConversation);

  // Escuta cliques em botões de Reenviar (renderizados dinamicamente)
  messagesEl.addEventListener('click', async (ev) => {
    const btn = ev.target.closest && ev.target.closest('.chat-resend-btn');
    if (!btn) return;
    const text = btn.dataset.text;
    if (!text) return;

    // Ao clicar, remove hint de erro
    clearError(errorEl);

    // Ao clicar, remove hint de erro
    clearError(errorEl);

    // marca o estado 'sending' na mensagem para que o render exiba 'Enviando...'
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const m = state.messages[i];
      if (m.role === 'user' && m.status === 'failed' && m.text === text) {
        state.messages[i] = { ...m, status: 'sending' };
        break;
      }
    }
    // mostra o indicador de escrita e desabilita entrada/enviar enquanto espera
    setTypingVisible(typingEl, true);
    setSendDisabled(sendBtn, true);
    setInputDisabled(inputEl, true);

    refresh();

    try {
      const response = USE_MOCK ? await postChatMock(text) : await postChat(text, null);
      // Remove status da mensagem enviada (enviar marcada como sucedida)
      for (let i = state.messages.length - 1; i >= 0; i--) {
        const m = state.messages[i];
        if (m.role === 'user' && (m.status === 'failed' || m.status === 'sending') && m.text === text) {
          state.messages[i] = { role: 'user', text: text };
          break;
        }
      }
      state = appendMessage(state, { role: 'bot', text: response.reply });
      refresh();
      clearError(errorEl);
    } catch (err) {
      // marca como failed novamente e mostra erro
      for (let i = state.messages.length - 1; i >= 0; i--) {
        const m = state.messages[i];
        if (m.role === 'user' && (m.status === 'failed' || m.status === 'sending') && m.text === text) {
          state.messages[i] = { ...m, status: 'failed' };
          break;
        }
      }
      refresh();
      showError(errorEl, err.message || 'Falha ao reenviar. Tente novamente.');
    } finally {
      // restaura estados da UI
      setTypingVisible(typingEl, false);
      setSendDisabled(sendBtn, false);
      setInputDisabled(inputEl, false);
    }
  });

  inputEl.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  });

  refresh();
  inputEl.focus();
}

if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => initChatApp(document));
}
