import { auth } from '../auth.js';

export function renderSignup() {
    document.getElementById('signup-form')?.addEventListener('submit', async (event) => {
      event.preventDefault();
      const pass = document.getElementById('signup-password').value;
      const confirm = document.getElementById('signup-password-confirm').value;
      if (pass !== confirm) {
        window.app.showToast('비밀번호가 일치하지 않습니다.', 'error');
        return;
      }
      window.app.showLoader();
      try {
        await auth.signup(document.getElementById('signup-email').value, pass);
        window.app.showToast('회원가입이 완료되었습니다.', 'success');
        window.app.navigate('profile');
      } catch (error) {
        await window.app.showError(error, {
          title: '회원가입 실패',
          method: error?.method || 'POST',
          path: error?.path || '/api/auth/signup'
        });
      } finally {
        window.app.hideLoader();
      }
    });
    
}
