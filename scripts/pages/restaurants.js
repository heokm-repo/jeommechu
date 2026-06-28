import { state } from '../state.js';
import { api } from '../api.js';
import { auth } from '../auth.js';
import { createCard, renderRestaurantCard } from '../restaurant-cards.js';
import { refreshFavorites, toggleFavorite } from '../favorite-actions.js';
import { renderRestaurantMarkersMap } from '../kakao-map.js';

export async function renderRestaurants() {
  const mapContainer = document.getElementById('map-container');
  const mapPlaceholder = document.getElementById('map-placeholder');
  const listContainer = document.getElementById('restaurant-list');
  const restaurants = state.currentRestaurants || [];

  await refreshFavorites();
  renderRestaurantMarkersMap(mapContainer, mapPlaceholder, restaurants, {
    lat: state.location.lat,
    lng: state.location.lng
  });

  listContainer.innerHTML = '';
  if (restaurants.length === 0) {
    listContainer.innerHTML = '<p class="text-center empty-list-message">추천된 맛집이 없습니다.</p>';
    return;
  }

  restaurants.forEach(restaurant => {
    const isFav = state.favorites.some(favorite => favorite.id === restaurant.id);
    const card = createCard(renderRestaurantCard(restaurant, isFav), 'restaurantRow');
    listContainer.appendChild(card);
  });

  listContainer.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', async (event) => {
      const restaurant = restaurants.find(item => item.id === event.currentTarget.dataset.id);
      if (!restaurant) return;

      try {
        await toggleFavorite(restaurant);
        await renderRestaurants();
      } catch (error) {
        await window.app.showError(error, {
          title: '찜 처리 실패',
          method: error?.method || 'POST',
          path: error?.path || '/api/favorites'
        });
      }
    });
  });

  listContainer.querySelectorAll('.visit-btn').forEach(btn => {
    btn.addEventListener('click', async (event) => {
      try {
        await auth.ensureGuest();
        await api.addVisit({
          user_id: state.userId,
          restaurant_id: event.currentTarget.dataset.id,
          search_log_id: state.currentSearchLogId
        });
        window.app.showToast('방문 기록을 저장했습니다.', 'success');
      } catch (error) {
        await window.app.showError(error, {
          title: '방문 기록 저장 실패',
          method: error?.method || 'POST',
          path: error?.path || '/api/visits'
        });
      }
    });
  });
}