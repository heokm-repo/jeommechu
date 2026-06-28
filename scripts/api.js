// api.js
// Backend endpoint facade.

import { ApiError, postJson, request } from './http-client.js';
import {
  buildRecommendationPayload,
  recommendationResultFromResponse
} from './recommendation-adapter.js';

export { ApiError };

function userIdQuery(userId) {
  return `user_id=${encodeURIComponent(userId)}`;
}

export const api = {
  async getConfig() {
    const data = await request('/api/config');
    return {
      kakaoApiKey: data.kakao_js_api_key || ''
    };
  },

  async createGuestUser() {
    return postJson('/api/users/guest');
  },

  async signup(email, password, userId) {
    return postJson('/api/auth/signup', { email, password, user_id: userId });
  },

  async login(email, password) {
    return postJson('/api/auth/login', { email, password });
  },

  async logout() {
    return postJson('/api/auth/logout');
  },

  async getRecommendation(location, moodText, moodChips = [], userId) {
    const payload = buildRecommendationPayload(location, moodText, moodChips, userId);
    const data = await postJson('/api/recommendations/search', payload);
    return recommendationResultFromResponse(data);
  },

  async getFavorites(userId) {
    if (!userId) return { favorites: [] };
    return request(`/api/favorites?${userIdQuery(userId)}`);
  },

  async addFavorite(userId, restaurantId, searchLogId = null) {
    return postJson('/api/favorites', {
      user_id: userId,
      restaurant_id: restaurantId,
      search_log_id: searchLogId
    });
  },

  async removeFavorite(userId, restaurantId) {
    return request(`/api/favorites/${encodeURIComponent(restaurantId)}?${userIdQuery(userId)}`, {
      method: 'DELETE'
    });
  },

  async getSearchLogs(userId) {
    if (!userId) return { search_logs: [] };
    return request(`/api/search-logs?${userIdQuery(userId)}`);
  },

  async getRecommendationDetail(searchLogId) {
    return request(`/api/recommendations/${encodeURIComponent(searchLogId)}`);
  },

  async addVisit(payload) {
    return postJson('/api/visits', payload);
  },

  async getVisits(userId) {
    if (!userId) return { visits: [] };
    return request(`/api/visits?${userIdQuery(userId)}`);
  },

  async addRecommendationFeedback(searchLogId, payload) {
    return postJson(`/api/recommendations/${encodeURIComponent(searchLogId)}/feedback`, payload);
  },

  async saveRegion(region) {
    return postJson('/api/regions', region);
  }
};