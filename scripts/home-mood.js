import { state, updateState } from './state.js';
import { submitRecommendation } from './recommendation-actions.js';

function setupTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (event) => {
      const targetTab = event.currentTarget.dataset.tab;
      document.querySelectorAll('.tab-btn').forEach(item => {
        item.classList.toggle('active', item === event.currentTarget);
      });
      document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('hidden', content.id !== `tab-${targetTab}`);
      });
    });
  });
}

function selectedMoodChips() {
  return Array.from(document.querySelectorAll('.chip-group .chip.selected')).map(item => item.dataset.value);
}

function setupMoodChips(moodChips) {
  moodChips.forEach(chip => {
    if (state.currentSearch.moodChips.includes(chip.dataset.value)) chip.classList.add('selected');

    chip.addEventListener('click', (event) => {
      const clickedChip = event.currentTarget;
      clickedChip.closest('.chip-group')?.querySelectorAll('.chip').forEach(item => {
        if (item !== clickedChip) item.classList.remove('selected');
      });
      clickedChip.classList.toggle('selected');
      updateState('currentSearch', { ...state.currentSearch, moodChips: selectedMoodChips() });
    });
  });
}

function setupMoodText(moodText) {
  if (state.currentSearch.moodText && moodText) moodText.value = state.currentSearch.moodText;

  moodText?.addEventListener('input', (event) => {
    updateState('currentSearch', { ...state.currentSearch, moodText: event.target.value });
  });
}

function setupRecommendationButtons(btnRecommendText, btnRecommendChips, moodText) {
  btnRecommendText?.addEventListener('click', async () => {
    const textVal = moodText?.value.trim() || '';
    if (!textVal) {
      window.app.showToast('기분이나 상황을 입력해 주세요.', 'info');
      return;
    }
    await submitRecommendation(textVal, []);
  });

  btnRecommendChips?.addEventListener('click', async () => {
    const chips = selectedMoodChips();
    if (chips.length === 0) {
      window.app.showToast('태그를 하나 이상 선택해 주세요.', 'info');
      return;
    }
    await submitRecommendation('', chips);
  });
}

export function setupHomeMoodControls({ moodChips, moodText, btnRecommendText, btnRecommendChips }) {
  setupTabs();
  setupMoodText(moodText);
  setupMoodChips(moodChips);
  setupRecommendationButtons(btnRecommendText, btnRecommendChips, moodText);
}