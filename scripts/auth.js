// auth.js
// Authentication helpers backed by the API server

import { state, updateState } from './state.js';
import { api } from './api.js';

export const auth = {
  async ensureGuest() {
    const result = await api.createGuestUser();
    if (state.user && state.userId !== result.user_id) {
      updateState('user', null);
    }
    updateState('userId', result.user_id);
    return result.user_id;
  },

  async login(email, password) {
    const result = await api.login(email, password);
    updateState('user', result.user);
    updateState('userId', result.user.id);
    return result.user;
  },

  async signup(email, password) {
    const result = await api.signup(email, password, state.userId);
    updateState('user', result.user);
    updateState('userId', result.user.id);
    return result.user;
  },

  async logout() {
    await api.logout();
    updateState('user', null);
    updateState('userId', null);
    return this.ensureGuest();
  }
};

