import { state, updateState } from '../state.js';
import { api } from '../api.js';
import { formatDistance } from '../render-utils.js';
import {
  isFavorite,
  refreshFavorites,
  setFavoriteButtonState,
  toggleFavorite
} from '../favorite-actions.js';
import { renderStaticRestaurantMap } from '../kakao-map.js';

function bindTopRestaurantFavorite(button, restaurant) {
  if (!button) return;

  const boundButton = button.cloneNode(true);
  button.parentNode.replaceChild(boundButton, button);
  setFavoriteButtonState(boundButton, isFavorite(restaurant.id));

  boundButton.addEventListener('click', async () => {
    try {
      const favorite = await toggleFavorite(restaurant);
      setFavoriteButtonState(boundButton, favorite);
    } catch (error) {
      await window.app.showError(error, {
        title: '찜 처리 실패',
        method: error?.method || 'POST',
        path: error?.path || '/api/favorites'
      });
    }
  });
}

function renderTopRestaurantMap(restaurant) {
  const mapContainer = document.getElementById('res-map-container');
  const placeholder = document.getElementById('res-map-placeholder');
  if (mapContainer) renderStaticRestaurantMap(mapContainer, restaurant, placeholder);
}

function renderWeatherInfo(element, weatherContext) {
  if (!element) return;

  const summary = String(weatherContext || '').trim();
  if (!summary) {
    element.textContent = '';
    element.classList.add('hidden');
    return;
  }

  element.textContent = `현재 날씨 · ${summary}`;
  element.classList.remove('hidden');
}

export async function renderResults() {
  const menuName = document.getElementById('result-menu-name');
  const reason = document.getElementById('result-reason');
  const meta = document.getElementById('result-meta');
  const weather = document.getElementById('result-weather');
  const feedbackWrap = document.getElementById('result-feedback');
  const resCard = document.getElementById('result-restaurant-card');

  if (state.recommendationResult) {
    const fullData = state.recommendationResult.fullData || {};
    menuName.textContent = state.recommendationResult.menuName;
    reason.textContent = state.recommendationResult.reason;
    if (meta) {
      const count = fullData.meta?.result_count ?? fullData.recommendations?.length ?? 0;
      meta.textContent = `${fullData.query || '추천 검색어'} · ${count}곳 검색됨`;
    }
    renderWeatherInfo(weather, fullData.weather_context);

    updateState('currentSearchLogId', fullData.search_log_id || state.currentSearchLogId);
    const currentRestList = fullData.recommendations?.map(item => item.restaurant) || [];
    updateState('currentRestaurants', currentRestList);

    const topRestaurant = currentRestList[0];
    if (topRestaurant) {
      resCard?.classList.remove('hidden');
      document.getElementById('res-name').textContent = topRestaurant.name;
      const distance = formatDistance(topRestaurant.distance);
      const metaText = [topRestaurant.category, topRestaurant.address || topRestaurant.road_address, distance].filter(Boolean).join(' · ');
      document.getElementById('res-meta').textContent = metaText;

      try {
        await refreshFavorites();
      } catch (err) {
        console.warn('Failed to refresh favorites', err);
      }

      bindTopRestaurantFavorite(document.getElementById('res-fav-btn'), topRestaurant);
      renderTopRestaurantMap(topRestaurant);
    } else {
      resCard?.classList.add('hidden');
    }
  } else {
    menuName.textContent = '아직 추천 결과가 없어요';
    reason.textContent = '홈에서 기분과 위치를 입력하고 추천을 받아보세요.';
    if (meta) meta.textContent = '';
    renderWeatherInfo(weather, '');
    updateState('currentRestaurants', []);
    resCard?.classList.add('hidden');
  }

  feedbackWrap?.querySelectorAll('[data-feedback-rating]').forEach(button => {
    button.addEventListener('click', async (event) => {
      if (!state.currentSearchLogId) return;
      try {
        await api.addRecommendationFeedback(state.currentSearchLogId, {
          user_id: state.userId,
          rating: Number(event.currentTarget.dataset.feedbackRating),
          comment: event.currentTarget.dataset.feedbackComment || ''
        });
        window.app.showToast('피드백을 저장했습니다.', 'success');
      } catch (error) {
        await window.app.showError(error, {
          title: '피드백 저장 실패',
          method: error?.method || 'POST',
          path: error?.path || `/api/recommendations/${state.currentSearchLogId}/feedback`
        });
      }
    });
  });
}