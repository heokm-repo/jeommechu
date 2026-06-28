// app.js
// Master Router and Application Initializer

import { hydrateState, updateState } from './scripts/state.js';
import { api } from './scripts/api.js';
import { auth } from './scripts/auth.js';
import { render } from './scripts/render.js';

function normalizeError(error, context = {}) {
  return {
    title: context.title || '오류가 발생했습니다',
    message: error?.message || String(error),
    status: error?.status ?? context.status ?? null,
    method: error?.method || context.method || null,
    path: error?.path || context.path || null,
    detail: error?.detail || context.detail || '',
    body: error?.body || null,
    route: context.route || null,
    timestamp: new Date().toISOString()
  };
}

const app = {
  contentDiv: document.getElementById('app-content'),
  navButtons: document.querySelectorAll('.nav-btn'),
  loader: document.getElementById('global-loader'),
  toastContainer: document.getElementById('toast-container'),

  routes: [
    'home',
    'results',
    'restaurants',
    'favorites',
    'history',
    'profile',
    'login',
    'signup',
    'error'
  ],

  async init() {
    hydrateState();
    this.setupNavigation();

    try {
      await auth.ensureGuest();
    } catch (error) {
      await this.showError(error, {
        title: '게스트 사용자 생성 실패',
        method: 'POST',
        path: '/api/users/guest'
      });
      return;
    }

    try {
      const config = await api.getConfig();
      if (!config.kakaoApiKey) {
        throw new Error('KAKAO_JS_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요.');
      }
      await this.loadKakaoMapScript(config.kakaoApiKey);
    } catch (error) {
      await this.showError(error, {
        title: '지도 설정 오류',
        method: error?.method || 'GET',
        path: error?.path || '/api/config'
      });
      return;
    }

    this.navigate('home');
  },

  setupNavigation() {
    this.navButtons.forEach(btn => {
      btn.addEventListener('click', (event) => {
        const link = event.currentTarget.dataset.link;
        this.navigate(link);
      });
    });

    const logo = document.querySelector('.logo');
    if (logo) {
      logo.addEventListener('click', () => this.navigate('home'));
    }

    document.body.addEventListener('click', (event) => {
      const target = event.target.closest('[data-navigate]');
      if (!target) return;
      event.preventDefault();
      this.navigate(target.dataset.navigate);
    });
  },

  async navigate(route) {
    if (!this.routes.includes(route)) {
      await this.showError(new Error(`알 수 없는 화면입니다: ${route}`), {
        title: '라우팅 오류',
        route
      });
      return;
    }

    this.showLoader();

    try {
      const path = `/pages/${route}.html`;
      const response = await fetch(path);
      if (!response.ok) {
        const error = new Error(`화면 파일을 불러오지 못했습니다: ${route}`);
        error.status = response.status;
        error.path = path;
        throw error;
      }

      this.contentDiv.innerHTML = await response.text();

      this.navButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.link === route);
      });

      if (route !== 'error') {
        updateState('error', null);
      }

      if (render[route] && typeof render[route] === 'function') {
        await render[route]();
      }
    } catch (error) {
      console.error('Navigation error:', error);
      updateState('error', normalizeError(error, {
        title: '화면 처리 오류',
        route,
        path: error?.path || `/pages/${route}.html`
      }));

      if (route !== 'error') {
        await this.navigate('error');
      }
    } finally {
      this.hideLoader();
    }
  },

  async showError(error, context = {}) {
    console.error(context.title || 'Application error', error);
    updateState('error', normalizeError(error, context));
    await this.navigate('error');
  },

  loadKakaoMapScript(apiKey) {
    return new Promise((resolve, reject) => {
      if (window.kakao && window.kakao.maps) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`;
      script.onload = () => {
        window.kakao.maps.load(resolve);
      };
      script.onerror = () => {
        reject(new Error('Kakao Map SDK를 불러오지 못했습니다. JavaScript 키와 도메인 등록 상태를 확인하세요.'));
      };
      document.head.appendChild(script);
    });
  },

  showLoader() {
    this.loader.classList.remove('hidden');
  },

  hideLoader() {
    this.loader.classList.add('hidden');
  },

  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    this.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('toast-hiding');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
};

window.app = app;

document.addEventListener('DOMContentLoaded', () => {
  app.init();
});
