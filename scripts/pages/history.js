import { state, updateState } from '../state.js';
import { api } from '../api.js';
import { createCard, renderHistoryCard } from '../restaurant-cards.js';

export async function renderHistory() {
  const listContainer = document.getElementById('history-list');
  listContainer.innerHTML = '<div class="card text-center empty-state-sm">기록을 불러오는 중입니다...</div>';

  const result = await api.getSearchLogs(state.userId);
  const logs = result.search_logs || [];
  updateState('history', logs);

  if (logs.length === 0) {
    listContainer.innerHTML = '<div class="card text-center empty-state-md">아직 추천 기록이 없어요.</div>';
    return;
  }

  listContainer.innerHTML = '';
  logs.forEach(item => {
    const card = createCard(renderHistoryCard(item), 'compact');
    listContainer.appendChild(card);
  });

  listContainer.querySelectorAll('.history-detail-btn').forEach(btn => {
    btn.addEventListener('click', async (event) => {
      try {
        const searchLogId = event.currentTarget.dataset.id;
        const detail = await api.getRecommendationDetail(searchLogId);
        updateState('currentSearchLogId', searchLogId);
        updateState('currentRestaurants', (detail.recommendations || []).map(item => item.restaurant).filter(Boolean));
        updateState('recommendationResult', {
          menuName: detail.recommendations?.[0]?.restaurant?.name || '저장된 추천',
          reason: detail.recommendations?.[0]?.ai_reason || '저장된 추천 결과입니다.',
          fullData: {
            search_log_id: searchLogId,
            query: detail.search?.emotion_state,
            weather_context: detail.weather_context,
            recommendations: detail.recommendations || [],
            meta: { result_count: detail.recommendations?.length || 0 }
          }
        });
        window.app.navigate('results');
      } catch (error) {
        await window.app.showError(error, {
          title: '추천 기록 조회 실패',
          method: error?.method || 'GET',
          path: error?.path || `/api/recommendations/${event.currentTarget.dataset.id}`
        });
      }
    });
  });
}