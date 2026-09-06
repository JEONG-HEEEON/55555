# 시계열 데이터 AI 분석 챗봇

## 1. 서비스 소개
대전 지점 일별 기온(시계열) 데이터를 저장·분석하고, 그 요약 정보를 GPT의 시스템 프롬프트에
주입해 "내 데이터에 대해 자연스럽게 대화"할 수 있게 해주는 웹 서비스입니다.
데이터를 추가/수정/삭제(CRUD)하면 요약과 대화 답변에 즉시 반영됩니다.

## 2. 기술 스택
- Backend: FastAPI, Pydantic, firebase-admin (Firestore), openai SDK
- Frontend: HTML / CSS / JavaScript (바닐라, Chart.js CDN만 사용)
- DB: Firebase Firestore
- 배포: Vercel 단일 프로젝트 (프론트 = 정적 호스팅, 백엔드 = Python 서버리스 함수)
  - 대안으로 Render(백엔드) + Vercel(프론트엔드) 분리 배포도 가능 (6-2 참고)

## 3. 배포 URL
| 항목 | 주소 |
|---|---|
| 프론트엔드 | (Vercel 배포 후 이 자리에 채워주세요) |
| 백엔드 API | `{Vercel URL}/api` (같은 도메인) |
| Swagger UI | `{Vercel URL}/docs` |

## 4. 로컬 실행 방법

### 4-1. 백엔드
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # 값 채워넣기
uvicorn app.main:app --reload
# http://localhost:8000/docs 에서 Swagger 확인
```

샘플 데이터(대전 기온 200일치)를 Firestore에 넣고 싶다면:
```bash
python seed_data.py
```

### 4-2. 프론트엔드
프레임워크/빌드도구 없이 정적 파일이라, 아래 중 하나면 충분합니다.
```bash
cd frontend
python3 -m http.server 5500
# http://localhost:5500 접속
```
`config.js`는 접속 호스트가 localhost/127.0.0.1이면 자동으로 `http://localhost:8000`을 쓰고,
배포 환경에서는 같은 오리진(상대경로 `/api/...`)을 씁니다. 따로 수정할 필요가 없습니다.

## 5. 환경 변수 (최소 세트)
| 변수명 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 키 |
| `OPENAI_MODEL` | 사용할 모델 (기본 gpt-4o-mini) |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase 서비스 계정 키 JSON 전체를 문자열로 |
| `ALLOWED_ORIGINS` | 프론트 배포 주소(CORS 허용, 콤마로 구분) |

## 6. 배포 가이드 (그대로 따라하면 됩니다)

### 6-1. Firebase
1. https://console.firebase.google.com 에서 프로젝트 생성 → Firestore Database 사용 설정(테스트 모드로 시작).
2. 프로젝트 설정 > 서비스 계정 > "새 비공개 키 생성"으로 JSON 다운로드.
3. 이 JSON 내용 전체를 한 줄 문자열로 만들어 `FIREBASE_SERVICE_ACCOUNT_JSON`에 붙여넣기.

### 6-2. Render (백엔드)
1. GitHub에 이 저장소를 push.
2. Render → New → Web Service → 저장소 연결.
3. Root Directory: `backend`, Build Command: `pip install -r requirements.txt`,
   Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment 탭에 위 4개 환경변수 등록 후 배포.
5. **무료 티어 콜드스타트 안내**: 일정 시간 요청이 없으면 서버가 슬립 상태가 되어
   첫 요청에 10~50초가량 지연될 수 있습니다. 프론트에서는 로딩 표시("AI가 답변을
   작성하는 중...")로 이를 안내하고 있습니다.

### 6-3. Vercel (프론트 + 백엔드 한 번에) — 권장

저장소 루트에 배포 설정이 이미 들어 있어, 저장소만 연결하면 바로 배포됩니다.

| 파일 | 역할 |
|---|---|
| `vercel.json` | `frontend/`를 정적 루트로 서빙하고, `/api/*`·`/docs`·`/openapi.json`을 Python 함수로 라우팅 |
| `api/index.py` | Vercel용 진입점. `backend/app/main.py`의 FastAPI `app`을 그대로 재사용 |
| `requirements.txt` (루트) | 서버리스 함수 의존성 (로컬 개발은 `backend/requirements.txt` 사용) |

**배포 순서**
1. https://vercel.com 로그인 → **Add New… > Project** → 이 GitHub 저장소를 Import.
2. **Root Directory는 저장소 루트 그대로 둡니다** (`frontend`로 바꾸지 마세요 —
   `vercel.json`이 이미 `outputDirectory: "frontend"`로 지정합니다).
   Framework Preset은 `Other`, Build Command는 비워둡니다.
3. **Environment Variables**에 아래를 등록합니다 (5장 표 참고).
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` (사용 중인 경우에만)
   - `OPENAI_MODEL`
   - `FIREBASE_SERVICE_ACCOUNT_JSON` — 서비스 계정 JSON **전체를 한 줄로**
   - `ALLOWED_ORIGINS` — 프론트와 API가 같은 도메인이라 CORS는 사실상 필요 없지만,
     외부에서 API를 호출할 계획이면 해당 주소를 넣습니다.
4. **Deploy**를 누릅니다.
5. 배포 후 확인:
   - `https://{프로젝트}.vercel.app/` → 챗봇 화면
   - `https://{프로젝트}.vercel.app/docs` → Swagger UI
   - `https://{프로젝트}.vercel.app/api/data` → 데이터 목록 JSON

**알아둘 점**
- 환경변수를 나중에 추가/수정하면 **Redeploy를 해야** 반영됩니다.
- `firebase-admin`(grpcio 포함)이 무거워 콜드스타트 시 첫 요청이 몇 초 걸릴 수 있습니다.
- OpenAI 응답이 길어질 수 있어 함수 `maxDuration`을 60초로 잡아두었습니다
  (Hobby 플랜 상한). 그보다 오래 걸리면 타임아웃됩니다.
- 서버리스 함수는 요청마다 초기화될 수 있어 로컬 파일에 상태를 저장하면 안 됩니다.
  이 프로젝트는 상태를 전부 Firestore에 두므로 문제 없습니다.

### 6-4. (대안) Render 백엔드 + Vercel 프론트 분리 배포
6-2로 백엔드를 Render에 올린 뒤, `frontend/index.html`의 `config.js` 로드 **앞**에
아래 한 줄을 넣으면 프론트가 Render 백엔드를 바라봅니다.
```html
<script>window.API_BASE_URL = "https://your-backend.onrender.com";</script>
```
이 경우 Render의 `ALLOWED_ORIGINS`에 Vercel 주소를 반드시 추가해야 합니다.

## 7. 제출 스크린샷 체크리스트
- [ ] 데이터 요약이 보이는 채팅 화면 (질문 + 답변 포함)
- [ ] 데이터 관리 화면 (추가/수정/삭제 중 최소 1개 동작)
- [ ] 대화 기록 화면 (불러오기 동작)

## 8. 보너스 과제 구현 내역

### 8-1. Function Calling (도구 호출)
`POST /api/chat` 처리 중 GPT에게 `get_data_statistics`라는 도구를 제공합니다
(`backend/app/services/openai_service.py`의 `TOOLS`). 사용자가 "표준편차", "이동평균",
"더 자세히" 등 심화 통계를 물으면 GPT가 스스로 이 도구를 호출하고, 백엔드는
`compute_statistics()` 결과를 도구 응답(role: "tool")으로 GPT에 돌려준 뒤 최종 답변을
받습니다.

**호출 흐름**
```
사용자 질문
  → GPT가 판단: 추가 통계가 필요한가?
     ├─ 아니오 → 바로 답변 생성
     └─ 예 → get_data_statistics 도구 호출
              → 백엔드가 Firestore에서 통계 계산 후 결과 반환
              → GPT가 결과를 반영해 최종 답변 생성
```
멀티채널(MCP Server/GPT Actions) 연동은 이번 제출 범위에서는 스키마 설계까지만
포함했으며, 실제 외부 채널 연결은 시간 관계상 진행하지 않았습니다.

### 8-2. 통계 확장
`GET /api/data/statistics`에서 기존 요약(period/count/metrics/trend)에 더해
표준편차(`std_dev`)와 최근 7개 이동평균(`moving_average_7`)을 추가 제공합니다.

### 8-3. 시각화
프론트엔드에 Chart.js(CDN)로 값 추이 라인 차트를 추가했습니다 (`trendChart`).

### 8-4. 데이터 내보내기
데이터 관리 패널의 "CSV 내보내기" / "JSON 내보내기" 버튼으로 전체 데이터를
다운로드할 수 있습니다.

### 8-5. 다크 모드
우측 상단 🌙 버튼으로 다크/라이트 모드를 전환하며, 선택값은 브라우저에 저장되어
다음 방문 시에도 유지됩니다.
