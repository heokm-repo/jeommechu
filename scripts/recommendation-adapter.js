function splitChipContexts(moodChips) {
  const [emotion, ...contexts] = moodChips.filter(Boolean);
  return {
    emotionState: emotion || contexts.join(', ') || '점심 추천',
    contexts
  };
}

export function buildRecommendationPayload(location, moodText, moodChips = [], userId) {
  const text = (moodText || '').trim();
  const chipInfo = splitChipContexts(moodChips);
  const emotionState = text || chipInfo.emotionState;
  const payload = {
    user_id: userId,
    emotion_state: emotionState,
    search_context: text,
    contexts: chipInfo.contexts,
    address: location.address,
    radius: Number(location.radius || 1500),
    size: 10
  };

  if (location.lat != null && location.lng != null) {
    payload.latitude = location.lat;
    payload.longitude = location.lng;
  }

  return payload;
}

export function recommendationResultFromResponse(data) {
  if (data.recommendations && data.recommendations.length > 0) {
    const topHit = data.recommendations[0];
    return {
      menuName: `${data.query || topHit.restaurant.category || '추천 메뉴'} (${topHit.restaurant.name})`,
      reason: topHit.ai_reason,
      fullData: data
    };
  }

  return {
    menuName: '조건에 맞는 식당을 찾지 못했어요',
    reason: '검색 반경을 넓히거나 다른 감정/상황으로 다시 추천을 받아보세요.',
    fullData: data
  };
}