import { escapeHtml, formatDistance } from './render-utils.js';

export function favoriteRestaurantFromRow(row) {
  return {
    id: row.restaurant_id,
    name: row.name,
    category: row.category,
    phone: row.phone,
    address: row.address,
    road_address: row.road_address,
    latitude: row.latitude,
    longitude: row.longitude,
    place_url: row.place_url,
    distance: row.distance
  };
}

export function renderRestaurantCard(restaurant, isFav) {
  const distance = formatDistance(restaurant.distance);
  const meta = [restaurant.address || restaurant.road_address, distance].filter(Boolean).join(' · ');
  const favoriteClass = isFav ? 'favorite-active' : 'favorite-idle';
  const iconClass = isFav ? ' symbol-filled' : '';
  return `
    <div>
      <div class="restaurant-card-title-row">
        <h4 class="restaurant-card-title">${escapeHtml(restaurant.name)}</h4>
        ${restaurant.category ? `<span class="restaurant-category-badge">${escapeHtml(restaurant.category)}</span>` : ''}
      </div>
      <p class="restaurant-card-meta">${escapeHtml(meta || '주소 정보 없음')}</p>
      <div class="restaurant-card-actions">
        ${restaurant.place_url ? `<a href="${escapeHtml(restaurant.place_url)}" target="_blank" rel="noreferrer" class="restaurant-card-link">카카오맵</a>` : ''}
        <button type="button" class="visit-btn restaurant-card-action" data-id="${escapeHtml(restaurant.id)}">방문 기록</button>
      </div>
    </div>
    <button class="btn-icon fav-btn ${favoriteClass}" data-id="${escapeHtml(restaurant.id)}" aria-label="찜하기">
      <span class="material-symbols-rounded${iconClass}">favorite</span>
    </button>
  `;
}

export function createCard(html, variant = 'default') {
  const card = document.createElement('div');
  const classes = {
    default: 'card card-tight',
    compact: 'card card-tight',
    restaurantRow: 'card card-row'
  };
  card.className = classes[variant] || classes.default;
  card.innerHTML = html;
  return card;
}

export function renderFavoriteCard(restaurant) {
  return `
    <div>
      <h4 class="favorite-card-title">${escapeHtml(restaurant.name)}</h4>
      <p class="favorite-card-meta">${escapeHtml(restaurant.address || restaurant.road_address || '')}</p>
      ${restaurant.place_url ? `<a href="${escapeHtml(restaurant.place_url)}" target="_blank" rel="noreferrer" class="favorite-card-link">카카오맵</a>` : ''}
    </div>
    <button class="btn-icon fav-btn favorite-active" data-id="${escapeHtml(restaurant.id)}" aria-label="찜 취소">
      <span class="material-symbols-rounded symbol-filled">favorite</span>
    </button>
  `;
}

export function renderHistoryCard(item) {
  const createdAt = item.created_at ? new Date(item.created_at).toLocaleString() : '';
  return `
    <div class="history-card-header">
      <span class="history-card-emotion">${escapeHtml(item.emotion_state)}</span>
      <span class="history-card-time">${escapeHtml(createdAt)}</span>
    </div>
    <p class="history-card-context">${escapeHtml(item.search_context || item.address_text || '추천 검색')}</p>
    <div class="history-card-footer">
      <span class="history-card-top">${escapeHtml(item.top_restaurant_name || `${item.recommendation_count}곳 추천`)}</span>
      <button type="button" class="history-detail-btn" data-id="${escapeHtml(item.id)}">다시 보기</button>
    </div>
  `;
}