export const CHAT_ENDPOINT = '/send/';

const MOCK_RESPONSE =
  'Obrigado! Em breve conectaremos ao assistente. Por enquanto, continue me contando o que você precisa.';

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Obter CSRF token do Django
function getCsrfToken() {
  const name = 'csrftoken=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookies = decodedCookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length);
    }
  }
  return null;
}

export async function postChat(message, sessionId, { fetchFn = fetch } = {}) {
  const csrfToken = getCsrfToken();
  const headers = {
    'Content-Type': 'application/json',
  };
  if (csrfToken) {
    headers['X-CSRFToken'] = csrfToken;
  }

  const response = await fetchFn(CHAT_ENDPOINT, {
    method: 'POST',
    headers,
    body: JSON.stringify({ message, session_id: sessionId }),
    credentials: 'include',
  });

  if (!response.ok) {
    let errorMsg = 'Falha ao enviar mensagem';
    let failedMessage = null;
    try {
      const errorData = await response.json();
      if (errorData.error) errorMsg = errorData.error;
      if (errorData.failed_message) failedMessage = errorData.failed_message;
    } catch (_) {
      // ignora erros de parse — usa mensagem genérica
    }
    const err = new Error(errorMsg);
    if (failedMessage) err.failedMessage = failedMessage;
    throw err;
  }

  return response.json();
}

export async function postChatMock(_message) {
  await delay(100);
  return { message: MOCK_RESPONSE };
}
