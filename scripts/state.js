// state.js
// Centralized state management for the application

export const state = {
  user: null,
  userId: null,
  error: null,
  location: {
    address: '서울특별시 강남구 역삼동',
    radius: 1000,
    lat: null,
    lng: null
  },
  currentSearch: {
    moodText: '',
    moodChips: []
  },
  recommendationResult: null,
  currentSearchLogId: null,
  currentRestaurants: [],
  favorites: [],
  history: []
};

const STORAGE_KEY = 'jeommechu.state.v1';

export function hydrateState() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    if (stored.user) state.user = stored.user;
    if (stored.userId) state.userId = stored.userId;
    if (stored.error) state.error = stored.error;
    if (stored.location) state.location = { ...state.location, ...stored.location };
    if (stored.currentSearch) state.currentSearch = { ...state.currentSearch, ...stored.currentSearch };
    if (stored.recommendationResult) state.recommendationResult = stored.recommendationResult;
    if (stored.currentSearchLogId) state.currentSearchLogId = stored.currentSearchLogId;
    if (Array.isArray(stored.currentRestaurants)) state.currentRestaurants = stored.currentRestaurants;
    if (Array.isArray(stored.favorites)) state.favorites = stored.favorites;
    if (Array.isArray(stored.history)) state.history = stored.history;
  } catch (error) {
    console.warn('Failed to hydrate persisted state', error);
  }
}

export function persistState() {
  const snapshot = {
    user: state.user,
    userId: state.userId,
    error: state.error,
    location: state.location,
    currentSearch: state.currentSearch,
    recommendationResult: state.recommendationResult,
    currentSearchLogId: state.currentSearchLogId,
    currentRestaurants: state.currentRestaurants,
    favorites: state.favorites,
    history: state.history
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
}

export function updateState(key, value) {
  state[key] = value;
  persistState();
}
