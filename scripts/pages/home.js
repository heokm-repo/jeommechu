import { setupHomeLocationControls } from '../home-location.js';
import { setupHomeMoodControls } from '../home-mood.js';

function homeElements() {
  return {
    moodChips: document.querySelectorAll('.chip-group .chip'),
    btnRecommendText: document.getElementById('btn-recommend-text'),
    btnRecommendChips: document.getElementById('btn-recommend-chips'),
    moodText: document.getElementById('mood-text'),
    btnCurrentLocation: document.getElementById('btn-current-location'),
    radiusSelect: document.getElementById('radius-select'),
    sidoSelect: document.getElementById('location-sido'),
    sigunguSelect: document.getElementById('location-sigungu'),
    dongSelect: document.getElementById('location-dong')
  };
}

export function renderHome() {
  const elements = homeElements();
  setupHomeLocationControls(elements);
  setupHomeMoodControls(elements);
}