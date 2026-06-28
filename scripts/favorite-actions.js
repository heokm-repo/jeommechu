import { state, updateState } from './state.js';
import { api } from './api.js';
import { auth } from './auth.js';
import { favoriteRestaurantFromRow } from './restaurant-cards.js';

export function isFavorite(restaurantId) {
  return state.favorites.some(favorite => favorite.id === restaurantId);
}

export function setFavoriteButtonState(button, favorite) {
  if (!button) return;
  const icon = button.querySelector('.material-symbols-rounded');
  button.classList.toggle('favorite-active', favorite);
  button.classList.toggle('favorite-idle', !favorite);
  if (icon) icon.classList.toggle('symbol-filled', favorite);
}

export async function refreshFavorites() {
  const result = await api.getFavorites(state.userId);
  const favorites = (result.favorites || []).map(favoriteRestaurantFromRow);
  updateState('favorites', favorites);
  return favorites;
}

export async function removeFavoriteById(restaurantId) {
  await auth.ensureGuest();
  await api.removeFavorite(state.userId, restaurantId);
  updateState('favorites', state.favorites.filter(item => item.id !== restaurantId));
  window.app.showToast('찜을 취소했습니다.');
}

export async function toggleFavorite(restaurant, searchLogId = state.currentSearchLogId) {
  await auth.ensureGuest();

  if (isFavorite(restaurant.id)) {
    await removeFavoriteById(restaurant.id);
    return false;
  }

  await api.addFavorite(state.userId, restaurant.id, searchLogId);
  updateState('favorites', [...state.favorites, restaurant]);
  window.app.showToast('찜 목록에 추가했습니다.');
  return true;
}