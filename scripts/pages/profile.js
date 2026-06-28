import { state } from '../state.js';
import { auth } from '../auth.js';

export function renderProfile() {
    const loggedOut = document.getElementById('profile-logged-out');
    const loggedIn = document.getElementById('profile-logged-in');

    if (state.user) {
      loggedOut.classList.add('hidden');
      loggedIn.classList.remove('hidden');
      document.getElementById('profile-email').textContent = state.user.email || '회원';
      const statusEl = document.getElementById('profile-status');
      if (statusEl) statusEl.textContent = state.user.user_type === 'MEMBER' ? '회원 계정' : '게스트 계정';
      document.getElementById('btn-logout')?.addEventListener('click', async () => {
        try {
          await auth.logout();
          window.app.showToast('로그아웃했습니다. 새 게스트 세션을 시작합니다.', 'success');
          renderProfile();
        } catch (error) {
          await window.app.showError(error, {
            title: '로그아웃 실패',
            method: error?.method || 'POST',
            path: error?.path || '/api/auth/logout'
          });
        }
      });
    } else {
      loggedOut.classList.remove('hidden');
      loggedIn.classList.add('hidden');
    }
    
}
