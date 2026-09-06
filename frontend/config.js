// 프론트엔드와 백엔드(FastAPI)를 같은 Vercel 프로젝트에 배포하므로,
// 배포 환경에서는 같은 오리진("")을 써서 fetch("/api/data") 처럼 상대경로로 호출한다.
// 로컬에서는 프론트(Live Server 등)와 백엔드(uvicorn :8000)가 분리돼 있어 절대주소를 쓴다.
// 백엔드를 별도 도메인(예: Render)에 두려면 index.html 에서
// window.API_BASE_URL = "https://your-backend.onrender.com" 을 미리 지정하면 된다.
const LOCAL_HOSTS = ["localhost", "127.0.0.1", ""];

const API_BASE_URL =
  window.API_BASE_URL ??
  (LOCAL_HOSTS.includes(location.hostname) ? "http://localhost:8000" : "");
