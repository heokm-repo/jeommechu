import { state, updateState } from './state.js';
import { api } from './api.js';
import { auth } from './auth.js';

function updateRecommendationLocation(center) {
  if (center?.latitude == null || center?.longitude == null) return;

  updateState('location', {
    ...state.location,
    lat: Number(center.latitude),
    lng: Number(center.longitude),
    address: center.address_text || state.location.address
  });
}

function applyRecommendationResult(result) {
  const fullData = result.fullData || {};

  if (fullData.user_id && fullData.user_id !== state.userId) {
    updateState('userId', fullData.user_id);
  }

  updateRecommendationLocation(fullData.center);
  updateState('recommendationResult', result);
  updateState('currentSearchLogId', fullData.search_log_id || null);
  updateState('currentRestaurants', fullData.recommendations?.map(item => item.restaurant) || []);
}

export async function submitRecommendation(moodText, moodChips) {
  await auth.ensureGuest();
  window.app.showLoader();

  try {
    const result = await api.getRecommendation(state.location, moodText, moodChips, state.userId);
    applyRecommendationResult(result);
    window.app.navigate('results');
  } catch (error) {
    await window.app.showError(error, {
      title: '추천 요청 실패',
      method: error?.method || 'POST',
      path: error?.path || '/api/recommendations/search'
    });
  } finally {
    window.app.hideLoader();
  }
}