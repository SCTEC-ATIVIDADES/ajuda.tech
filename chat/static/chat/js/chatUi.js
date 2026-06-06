
const COPY_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
const CHECK_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>`;
const RELOAD_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 1 1-3.4-6.6"/><path d="M21 3v6h-6"/></svg>`;

function createCopyButton(getText) {
  const btn = document.createElement('button');
  btn.className = 'chat-copy-btn';
  btn.setAttribute('aria-label', 'Copiar mensagem');
  btn.type = 'button';
  btn.innerHTML = COPY_ICON;

  btn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(getText());
      btn.innerHTML = CHECK_ICON;
      btn.classList.add('chat-copy-btn--copied');
      btn.setAttribute('aria-label', 'Copiado!');
      setTimeout(() => {
        btn.innerHTML = COPY_ICON;
        btn.classList.remove('chat-copy-btn--copied');
        btn.setAttribute('aria-label', 'Copiar mensagem');
      }, 2000);
    } catch {
      // clipboard API indisponível — falha silenciosa
    }
  });

  return btn;
const COPY_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
const CHECK_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
const SHARE_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>`;

function createMessageActions(contentEl) {
  const wrapper = document.createElement('div');
  wrapper.className = 'chat-message-actions';

  const copyBtn = document.createElement('button');
  copyBtn.type = 'button';
  copyBtn.className = 'chat-copy-btn';
  copyBtn.setAttribute('aria-label', 'Copiar mensagem');
  copyBtn.title = 'Copiar mensagem';
  copyBtn.innerHTML = COPY_ICON;

  copyBtn.addEventListener('click', async () => {
    const text = contentEl.innerText ?? contentEl.textContent;
    try {
      await navigator.clipboard.writeText(text);
      copyBtn.innerHTML = CHECK_ICON;
      copyBtn.setAttribute('aria-label', 'Copiado!');
      copyBtn.title = 'Copiado!';
      copyBtn.classList.add('chat-copy-btn--copied');
      setTimeout(() => {
        copyBtn.innerHTML = COPY_ICON;
        copyBtn.setAttribute('aria-label', 'Copiar mensagem');
        copyBtn.title = 'Copiar mensagem';
        copyBtn.classList.remove('chat-copy-btn--copied');
      }, 2000);
    } catch {
      // clipboard API indisponível
    }
  });

  wrapper.appendChild(copyBtn);

  if (typeof navigator !== 'undefined' && navigator.share) {
    const shareBtn = document.createElement('button');
    shareBtn.type = 'button';
    shareBtn.className = 'chat-share-btn';
    shareBtn.setAttribute('aria-label', 'Compartilhar mensagem');
    shareBtn.title = 'Compartilhar mensagem';
    shareBtn.innerHTML = SHARE_ICON;
    shareBtn.addEventListener('click', () => {
      const text = contentEl.innerText ?? contentEl.textContent;
      navigator.share({ text }).catch(() => {});
    });
    wrapper.appendChild(shareBtn);
  }

  return wrapper;

}

export function renderMessages(container, messages, parseMarkdown = (text) => text) {
  container.innerHTML = '';
  for (const msg of messages) {
    const wrapper = document.createElement('div');
    wrapper.className = `chat-message-wrapper chat-message-wrapper--${msg.role}`;

    const el = document.createElement('div');
    el.className = `chat-message chat-message--${msg.role}`;
    if (msg.role === 'bot') {
      const contentEl = document.createElement('div');
      contentEl.className = 'chat-message-content';
      contentEl.innerHTML = parseMarkdown(msg.text);
      el.appendChild(contentEl);
      el.appendChild(createMessageActions(contentEl));
    } else {
      el.textContent = msg.text;
    }

    wrapper.appendChild(el);
    wrapper.appendChild(createCopyButton(() => el.textContent));

    // Se a mensagem do usuário estiver com status 'failed', exibe botão de Reenviar
    if (msg.role === 'user' && msg.status === 'failed') {
      const resendBtn = document.createElement('button');
      resendBtn.className = 'chat-resend-btn';
      resendBtn.type = 'button';
      resendBtn.setAttribute('aria-label', 'Reenviar mensagem');
      // ícone de reload + texto
      resendBtn.innerHTML = RELOAD_ICON + '<span class="chat-resend-text">Reenviar</span>';
      // armazena o texto para que o app possa tratar o clique
      resendBtn.dataset.text = msg.text;
      wrapper.appendChild(resendBtn);
    }

    // Se está em processo de envio (resend), exibe botão desabilitado com texto 'Enviando...'
    if (msg.role === 'user' && msg.status === 'sending') {
      const sendingBtn = document.createElement('button');
      sendingBtn.className = 'chat-resend-btn';
      sendingBtn.type = 'button';
      sendingBtn.disabled = true;
      sendingBtn.setAttribute('aria-label', 'Enviando mensagem');
      sendingBtn.innerHTML = RELOAD_ICON + '<span class="chat-resend-text">Enviando...</span>';
      wrapper.appendChild(sendingBtn);
    }

    container.appendChild(wrapper);
  }
}

export function showError(el, text) {
  el.textContent = text;
  el.hidden = false;
}

export function clearError(el) {
  el.textContent = '';
  el.hidden = true;
}

export function setTypingVisible(el, visible) {
  el.hidden = !visible;
}

export function setSendDisabled(button, disabled) {
  button.disabled = disabled;
}

export function setInputDisabled(input, disabled) {
  input.disabled = disabled;
}
