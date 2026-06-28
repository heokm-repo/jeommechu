# 점메추 MVP

점메추는 사용자의 감정, 상황, 위치를 받아 Gemini가 Kakao Local API 검색어를 만들고, Kakao 실시간 검색 결과를 기반으로 주변 맛집을 추천하는 모바일 우선 웹앱입니다.

## 실행

MySQL과 API 키를 `.env`에 설정한 뒤 백엔드 서버를 실행합니다. 서버가 정적 프론트 파일도 함께 제공합니다.

```powershell
python backend\server.py
```

브라우저에서 아래 주소를 엽니다.

```text
http://127.0.0.1:8000
```

## 필수 환경 변수

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

## MVP 범위

- 게스트 사용자 생성과 localStorage 세션 유지
- 감정/상황/지역/반경 기반 추천 요청
- Gemini 기반 Kakao 검색어 생성
- Kakao Local API 실시간 음식점 검색
- 추천 결과, 식당 스냅샷, 검색 기록 저장
- 찜, 추천 기록, 방문 기록, 피드백 저장
- 회원가입/로그인과 게스트 기록 승계
- API/SDK/설정 오류를 `error.html`에서 상세 표시

외부 API 실패 시 rule-based/mock/fallback 추천을 만들지 않습니다. 실패 원인은 에러 화면에서 상태 코드, 요청 경로, 메시지, 상세 응답으로 확인합니다.
