// Shared rendering helpers for route controllers.

import { normalizeDongName } from './location.js';

export const REGION_DATA = {
  "서울특별시": {
    "강남구": ["역삼동", "삼성동", "대치동", "논현동", "압구정동"],
    "서초구": ["서초동", "반포동", "방배동", "양재동"],
    "송파구": ["잠실동", "가락동", "문정동", "방이동"],
    "마포구": ["서교동", "합정동", "망원동", "상암동"]
  },
  "경기도": {
    "수원시 장안구": ["정자동", "율전동", "조원동", "연무동"],
    "성남시 분당구": ["삼평동", "서현동", "야탑동", "정자동"],
    "고양시 일산동구": ["장항동", "마두동", "백석동", "식사동"],
    "용인시 수지구": ["풍덕천동", "죽전동", "동천동", "상현동"]
  },
  "인천광역시": {
    "남동구": ["구월동", "간석동", "만수동", "서창동"],
    "연수구": ["송도동", "동춘동", "연수동", "옥련동"],
    "부평구": ["부평동", "산곡동", "삼산동", "청천동"],
    "서구": ["청라동", "검암동", "연희동", "당하동"]
  }
};

export function parseAddressString(addressStr) {
  if (!addressStr) return null;
  const parts = addressStr.split(' ').map(p => p.trim()).filter(Boolean);
  if (parts.length < 3) return null;

  let sido = parts[0];
  if (sido === '서울') sido = '서울특별시';
  if (sido === '경기') sido = '경기도';
  if (sido === '인천') sido = '인천광역시';

  const dong = normalizeDongName(parts[parts.length - 1]);
  const sigungu = parts.slice(1, parts.length - 1).join(' ');

  return { sido, sigungu, dong };
}

export function setSelectOption(selectEl, value, label) {
  if (!selectEl) return;
  let option = Array.from(selectEl.options).find(opt => opt.value === value);
  if (!option) {
    option = document.createElement('option');
    option.value = value;
    option.textContent = label || value;
    selectEl.appendChild(option);
  }
  selectEl.value = value;
}

export function populateSelect(selectEl, options, selectedValue) {
  if (!selectEl) return;
  selectEl.innerHTML = '';

  options.forEach(optVal => {
    const option = document.createElement('option');
    option.value = optVal;
    option.textContent = optVal;
    selectEl.appendChild(option);
  });

  if (selectedValue && !options.includes(selectedValue)) {
    const option = document.createElement('option');
    option.value = selectedValue;
    option.textContent = selectedValue;
    selectEl.appendChild(option);
  }

  if (selectedValue) {
    selectEl.value = selectedValue;
  }
}

export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function formatDistance(distance) {
  const meters = Number(distance);
  if (!Number.isFinite(meters)) return '';
  return meters >= 1000 ? `${(meters / 1000).toFixed(1)}km` : `${Math.round(meters)}m`;
}

export function selectedAddress(sidoSelect, sigunguSelect, dongSelect) {
  return [sidoSelect?.value, sigunguSelect?.value, dongSelect?.value].filter(Boolean).join(' ');
}