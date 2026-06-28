import { state } from '../state.js';
import { createCard, renderFavoriteCard } from '../restaurant-cards.js';
import { refreshFavorites, removeFavoriteById } from '../favorite-actions.js';

export async function renderFavorites() {
  const listContainer = document.getElementById('favorites-list');
  await refreshFavorites();

  if (state.favorites.length === 0) {
    listContainer.innerHTML = '<div class="card text-center empty-state">아직 찜한 맛집이 없어요.</div>';
    return;
  }

  listContainer.innerHTML = '';
  state.favorites.forEach(restaurant => {
    const card = createCard(renderFavoriteCard(restaurant), 'restaurantRow');
    listContainer.appendChild(card);
  });

  listContainer.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', async (event) => {
      const id = event.currentTarget.dataset.id;
      try {
        await removeFavoriteById(id);
        await renderFavorites();
      } catch (error) {
        await window.app.showError(error, {
          title: '찜 삭제 실패',
          method: error?.method || 'DELETE',
          path: error?.path || `/api/favorites/${id}`
        });
      }
    });
  });
}