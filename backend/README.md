# Jeommechu Backend

사용자 상태 입력 -> Gemini 검색어 생성 -> Kakao Local API 실시간 검색 -> 추천 결과 저장 흐름을 기준으로 한 MVP 백엔드입니다. 런타임 DB는 MySQL 8.x 전용입니다.

## 핵심 흐름

1. 사용자가 감정, 상황, 지역/현재 위치, 검색 반경을 보냅니다.
2. Gemini가 Kakao Local API에 넣을 음식 카테고리/검색어를 생성합니다.
3. 백엔드는 해당 검색어와 위치/반경으로 Kakao Local API를 실시간 호출합니다.
4. 음식점 이름, 카테고리, 주소, 거리, 좌표, Kakao 장소 URL을 응답으로 보냅니다.
5. DB에는 검색 기록, AI 생성 검색어, Kakao 음식점 스냅샷, 추천 결과를 저장합니다.
6. 찜, 방문, 피드백 같은 사용자 행동 데이터도 DB에 저장합니다.

DB에 저장된 음식점 스냅샷은 기록/분석/사용자 행동 연결용입니다. 추천 검색의 1차 원천은 Kakao Local API입니다.

## 오류 정책

외부 API 키 누락, Kakao/Gemini 호출 실패, Gemini JSON 검증 실패가 발생하면 rule-based/mock/fallback 추천을 만들지 않습니다. API는 오류 JSON을 반환하고, 프론트는 `pages/error.html`에서 상태 코드, 요청 경로, 메시지, 상세 응답을 표시합니다.

## Run

`.env`에 MySQL과 API 키를 설정합니다.

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=jeommechu
DB_USER=root
DB_PASSWORD=your-mysql-password
KAKAO_REST_API_KEY=your-kakao-rest-api-key
KAKAO_JS_API_KEY=your-kakao-js-api-key
GEMINI_API_KEY=your-gemini-api-key
METEO_API_KEY=your-weather-api-key
```

서버 시작 시 `backend/schema.mysql.sql`을 MySQL에 적용합니다.

```powershell
cd C:\Users\meat\workspace\점메추\jeommechu-mvp
python backend\server.py
```

## Main Endpoint

### `POST /api/recommendations/search`

프론트의 추천 버튼이 호출하는 메인 API입니다.

```json
{
  "user_id": "optional-existing-user-id",
  "emotion_state": "스트레스",
  "search_context": "회의가 길어서 매운 국물이 먹고 싶다",
  "contexts": ["혼밥", "빠르게"],
  "address": "서울 강남구 역삼동",
  "radius": 1500,
  "size": 10
}
```

현재 위치 기반:

```json
{
  "emotion_state": "더위",
  "search_context": "덥고 가볍게 먹고 싶다",
  "latitude": 37.4953,
  "longitude": 127.0330,
  "radius": 1000,
  "size": 10
}
```

## Supporting Endpoints

- `GET /api/health`: 서버 상태 확인
- `GET /api/config`: Kakao JavaScript 키 조회
- `POST /api/users/guest`: 게스트 사용자 생성
- `POST /api/auth/signup`: 이메일 회원가입, 기존 게스트 `user_id` 전달 시 회원으로 승격
- `POST /api/auth/login`: 이메일 로그인
- `POST /api/auth/logout`: 로그아웃
- `POST /api/favorites`: 찜 저장
- `GET /api/favorites?user_id=...`: 찜 조회
- `DELETE /api/favorites/{restaurant_id}?user_id=...`: 찜 삭제
- `GET /api/search-logs?user_id=...`: 추천 기록 조회
- `GET /api/recommendations/{search_log_id}`: 저장된 검색 추천 결과 조회
- `POST /api/visits`: 방문 기록 저장
- `GET /api/visits?user_id=...`: 방문 기록 조회
- `POST /api/recommendations/{search_log_id}/feedback`: 추천 피드백 저장

## Kakao Local API

사용 API:

- 주소 검색: `GET https://dapi.kakao.com/v2/local/search/address.json`
- 키워드 장소 검색: `GET https://dapi.kakao.com/v2/local/search/keyword.json`
- 카테고리 장소 검색: `GET https://dapi.kakao.com/v2/local/search/category.json`

인증 헤더:

```http
Authorization: KakaoAK ${KAKAO_REST_API_KEY}
```
