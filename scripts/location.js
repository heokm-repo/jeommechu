export function normalizeDongName(dong) {
  return dong ? dong.replace(/(제)?[\d·~-]+동$/, '동') : dong;
}

export function regionAddress(region) {
  const sido = region.region_1depth_name;
  const sigungu = region.region_2depth_name;
  const dong = normalizeDongName(region.region_3depth_name);
  const fullAddress = [sido, sigungu, dong].filter(Boolean).join(' ');

  return {
    sido,
    sigungu,
    dong,
    fullAddress
  };
}

export function hasBrowserGeolocation() {
  return typeof navigator !== 'undefined' && Boolean(navigator.geolocation);
}

export function requestCurrentPosition() {
  return new Promise((resolve, reject) => {
    if (!hasBrowserGeolocation()) {
      const error = new Error('GEOLOCATION_UNAVAILABLE');
      error.code = 'GEOLOCATION_UNAVAILABLE';
      reject(error);
      return;
    }

    navigator.geolocation.getCurrentPosition(resolve, reject);
  });
}

export function hasKakaoGeocoder() {
  return typeof window !== 'undefined' && Boolean(window.kakao?.maps?.services?.Geocoder);
}

export function resolveKakaoRegionCode(lat, lng) {
  return new Promise((resolve, reject) => {
    if (!hasKakaoGeocoder()) {
      const error = new Error('KAKAO_GEOCODER_UNAVAILABLE');
      error.code = 'KAKAO_GEOCODER_UNAVAILABLE';
      reject(error);
      return;
    }

    const geocoder = new window.kakao.maps.services.Geocoder();
    geocoder.coord2RegionCode(lng, lat, (result, status) => {
      if (status === window.kakao.maps.services.Status.OK) {
        const regions = Array.isArray(result) ? result : [];
        const region = regions.find(item => item.region_type === 'H') || regions[0];
        if (region) {
          resolve(region);
          return;
        }
      }

      const error = new Error('KAKAO_REGION_NOT_FOUND');
      error.code = 'KAKAO_REGION_NOT_FOUND';
      error.status = status;
      reject(error);
    });
  });
}