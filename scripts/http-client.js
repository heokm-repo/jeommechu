export class ApiError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = details.status ?? null;
    this.method = details.method ?? null;
    this.path = details.path ?? null;
    this.detail = details.detail ?? '';
    this.body = details.body ?? null;
  }
}

export async function request(path, options = {}) {
  const method = options.method || 'GET';
  let response;

  try {
    response = await fetch(path, {
      ...options,
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
  } catch (error) {
    throw new ApiError('서버에 연결하지 못했습니다.', {
      method,
      path,
      detail: error.message
    });
  }

  const text = await response.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (error) {
      data = { raw: text };
    }
  }

  if (!response.ok) {
    throw new ApiError(data.error || data.message || `요청 실패 (${response.status})`, {
      status: response.status,
      method,
      path,
      detail: data.detail || data.raw || '',
      body: data
    });
  }

  return data;
}

export function postJson(path, payload = {}) {
  return request(path, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}