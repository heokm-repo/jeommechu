import { state, updateState } from './state.js';
import { api } from './api.js';
import {
  hasBrowserGeolocation,
  regionAddress,
  requestCurrentPosition,
  resolveKakaoRegionCode
} from './location.js';
import {
  REGION_DATA,
  parseAddressString,
  populateSelect,
  selectedAddress,
  setSelectOption
} from './render-utils.js';

function setupRadiusSelect(radiusSelect) {
  if (!radiusSelect) return;

  radiusSelect.value = String(state.location.radius || 1000);
  radiusSelect.addEventListener('change', () => {
    updateState('location', { ...state.location, radius: Number(radiusSelect.value) });
  });
}

function setupAddressDropdowns({ sidoSelect, sigunguSelect, dongSelect }) {
  const updateAddressState = () => {
    updateState('location', {
      ...state.location,
      address: selectedAddress(sidoSelect, sigunguSelect, dongSelect),
      lat: null,
      lng: null
    });
  };

  const handleSidoChange = () => {
    const selectedSido = sidoSelect.value;
    const sigungus = Object.keys(REGION_DATA[selectedSido] || {});
    const defaultSigungu = sigungus[0] || '';

    populateSelect(sigunguSelect, sigungus, defaultSigungu);

    const dongs = REGION_DATA[selectedSido]?.[defaultSigungu] || [];
    const defaultDong = dongs[0] || '';
    populateSelect(dongSelect, dongs, defaultDong);

    updateAddressState();
  };

  const handleSigunguChange = () => {
    const selectedSido = sidoSelect.value;
    const selectedSigungu = sigunguSelect.value;
    const dongs = REGION_DATA[selectedSido]?.[selectedSigungu] || [];
    const defaultDong = dongs[0] || '';

    populateSelect(dongSelect, dongs, defaultDong);

    updateAddressState();
  };

  if (!sidoSelect || !sigunguSelect || !dongSelect) {
    if (!state.location.address) updateAddressState();
    return;
  }

  sidoSelect.addEventListener('change', handleSidoChange);
  sigunguSelect.addEventListener('change', handleSigunguChange);
  dongSelect.addEventListener('change', updateAddressState);

  const parsed = parseAddressString(state.location.address);
  if (!parsed) {
    handleSidoChange();
    return;
  }

  setSelectOption(sidoSelect, parsed.sido);
  populateSelect(sigunguSelect, Object.keys(REGION_DATA[parsed.sido] || {}), parsed.sigungu);
  populateSelect(dongSelect, REGION_DATA[parsed.sido]?.[parsed.sigungu] || [], parsed.dong);
}

function applyCoordinateLocation(lat, lng, address = '') {
  updateState('location', {
    ...state.location,
    lat,
    lng,
    address
  });
}

function applyRegionToDropdowns({ sidoSelect, sigunguSelect, dongSelect }, sido, sigungu, dong) {
  setSelectOption(sidoSelect, sido);
  populateSelect(sigunguSelect, Object.keys(REGION_DATA[sido] || {}), sigungu);
  populateSelect(dongSelect, REGION_DATA[sido]?.[sigungu] || [], dong);
}

function showCurrentLocationResolveError(message, detail = '') {
  return window.app.showError(new Error(message), {
    title: '현재 위치 변환 오류',
    detail
  });
}

function applyResolvedRegion(region, lat, lng, addressElements) {
  const { sido, sigungu, dong, fullAddress } = regionAddress(region);

  applyRegionToDropdowns(addressElements, sido, sigungu, dong);
  applyCoordinateLocation(lat, lng, fullAddress);

  api.saveRegion({ sido, sigungu, dong }).catch(err => {
    console.warn('Failed to save region to database:', err);
  });

  window.app.showToast(`현재 위치(${fullAddress})를 적용했습니다.`, 'success');
}

async function applyCurrentLocation(addressElements) {
  if (!hasBrowserGeolocation()) {
    await window.app.showError(new Error('이 브라우저에서는 현재 위치를 사용할 수 없습니다.'), { title: '현재 위치 오류' });
    return;
  }

  window.app.showLoader();

  try {
    const position = await requestCurrentPosition();
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const region = await resolveKakaoRegionCode(lat, lng);
    applyResolvedRegion(region, lat, lng, addressElements);
  } catch (error) {
    if (error?.code === 'KAKAO_GEOCODER_UNAVAILABLE') {
      await showCurrentLocationResolveError(
        '현재 위치를 주소로 변환할 수 없습니다.',
        'Kakao Geocoder가 준비되지 않았습니다. Kakao JavaScript 키와 services 라이브러리 로드 상태를 확인하세요.'
      );
      return;
    }

    if (error?.code === 'KAKAO_REGION_NOT_FOUND') {
      await showCurrentLocationResolveError(
        '현재 위치를 행정동으로 변환하지 못했습니다.',
        `Kakao Geocoder status: ${error.status}`
      );
      return;
    }

    await window.app.showError(new Error('현재 위치를 가져오지 못했습니다.'), {
      title: '위치 권한 오류',
      detail: error.message || `Geolocation error code: ${error.code}`
    });
  } finally {
    window.app.hideLoader();
  }
}

function setupCurrentLocationButton(btnCurrentLocation, addressElements) {
  btnCurrentLocation?.addEventListener('click', () => {
    void applyCurrentLocation(addressElements);
  });
}

export function setupHomeLocationControls(elements) {
  setupRadiusSelect(elements.radiusSelect);
  setupAddressDropdowns(elements);
  setupCurrentLocationButton(elements.btnCurrentLocation, elements);
}