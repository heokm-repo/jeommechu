import { auth } from '../auth.js';

export function renderLogin() {
    document.getElementById('login-form')?.addEventListener('submit', async (event) => {
      event.preventDefault();
      window.app.showLoader();
      try {
        await auth.login(document.getElementById('login-email').value, document.getElementById('login-password').value);
        window.app.showToast('로그인했습니다.', 'success');
        window.app.navigate('profile');
      } catch (error) {
        await window.app.showError(error, {
          title: '로그인 실패',
          method: error?.method || 'POST',
          path: error?.path || '/api/auth/login'
        });
      } finally {
        window.app.hideLoader();
      }
    });
    
}
