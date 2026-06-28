// render.js
// Route renderer registry.

import { renderHome } from './pages/home.js';
import { renderResults } from './pages/results.js';
import { renderRestaurants } from './pages/restaurants.js';
import { renderFavorites } from './pages/favorites.js';
import { renderHistory } from './pages/history.js';
import { renderProfile } from './pages/profile.js';
import { renderLogin } from './pages/login.js';
import { renderSignup } from './pages/signup.js';
import { renderError } from './pages/error.js';

export const render = {
  home: renderHome,
  results: renderResults,
  restaurants: renderRestaurants,
  favorites: renderFavorites,
  history: renderHistory,
  profile: renderProfile,
  login: renderLogin,
  signup: renderSignup,
  error: renderError
};