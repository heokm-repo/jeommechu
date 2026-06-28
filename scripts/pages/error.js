import { state } from '../state.js';

function showElement(element) {
  element?.classList.add('is-visible');
}

export function renderError() {
  const error = state.error || {
    title: '오류 정보가 없습니다',
    message: '현재 표시할 오류 정보가 없습니다.',
    timestamp: new Date().toISOString()
  };

  const titleEl = document.getElementById('error-title');
  const messageEl = document.getElementById('error-message');
  const statusRow = document.getElementById('error-status-row');
  const statusEl = document.getElementById('error-status');
  const pathRow = document.getElementById('error-path-row');
  const pathEl = document.getElementById('error-path');
  const timeRow = document.getElementById('error-time-row');
  const timeEl = document.getElementById('error-time');
  const detailWrap = document.getElementById('error-detail-wrap');
  const detailEl = document.getElementById('error-detail');

  titleEl.textContent = error.title || '오류가 발생했습니다';
  messageEl.textContent = error.message || '요청을 처리하는 중 문제가 발생했습니다.';

  if (error.status) {
    showElement(statusRow);
    statusEl.textContent = String(error.status);
  }

  if (error.path || error.method) {
    showElement(pathRow);
    pathEl.textContent = [error.method, error.path].filter(Boolean).join(' ');
  }

  if (error.timestamp) {
    showElement(timeRow);
    timeEl.textContent = new Date(error.timestamp).toLocaleString();
  }

  const detailParts = [];
  if (error.detail) detailParts.push(error.detail);
  if (error.body) detailParts.push(JSON.stringify(error.body, null, 2));
  if (detailParts.length > 0) {
    showElement(detailWrap);
    detailEl.textContent = detailParts.join('\n\n');
  }

  document.getElementById('btn-error-back')?.addEventListener('click', () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.app.navigate('home');
    }
  });
}