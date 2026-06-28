export function requireKakaoMaps() {
  if (!window.kakao || !window.kakao.maps) {
    throw new Error('Kakao Map SDK가 준비되지 않았습니다. 지도 JavaScript 키와 도메인 등록 상태를 확인하세요.');
  }
}

export function hasCoordinates(item) {
  return item?.latitude != null && item?.longitude != null;
}

export function renderStaticRestaurantMap(container, restaurant, placeholder) {
  if (!hasCoordinates(restaurant)) {
    if (placeholder) placeholder.textContent = '위치 정보가 없는 매장입니다.';
    return false;
  }

  if (!window.kakao?.maps?.StaticMap) {
    return false;
  }

  const position = new window.kakao.maps.LatLng(restaurant.latitude, restaurant.longitude);
  container.innerHTML = '';
  new window.kakao.maps.StaticMap(container, {
    center: position,
    level: 3,
    marker: { position }
  });
  return true;
}

export function renderRestaurantMarkersMap(mapContainer, mapPlaceholder, restaurants, center) {
  if (restaurants.length === 0) return null;

  requireKakaoMaps();

  const centerRestaurant = restaurants.find(hasCoordinates);
  const centerLat = center?.lat ?? centerRestaurant?.latitude;
  const centerLng = center?.lng ?? centerRestaurant?.longitude;

  if (centerLat == null || centerLng == null) {
    return null;
  }

  if (mapPlaceholder) mapPlaceholder.classList.add('hidden');

  const map = new window.kakao.maps.Map(mapContainer, {
    center: new window.kakao.maps.LatLng(centerLat, centerLng),
    level: 4
  });

  restaurants.forEach(restaurant => {
    if (!hasCoordinates(restaurant)) return;
    new window.kakao.maps.Marker({
      position: new window.kakao.maps.LatLng(restaurant.latitude, restaurant.longitude)
    }).setMap(map);
  });

  return map;
}
