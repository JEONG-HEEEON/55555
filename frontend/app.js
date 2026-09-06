// ---------- 공통 유틸 ----------
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "요청 실패");
  }
  if (res.status === 204) return null;
  return res.json();
}

let currentConversationId = null;
let trendChart = null;

// ---------- 데이터 요약 + 차트 ----------
async function loadSummary() {
  const box = document.getElementById("summaryBox");
  try {
    const summary = await apiFetch("/api/data/summary");
    box.textContent =
      `기간: ${summary.period}\n` +
      `개수: ${summary.count}개\n` +
      `평균: ${summary.metrics.average} / 최대: ${summary.metrics.max} / 최소: ${summary.metrics.min}\n` +
      `트렌드: ${summary.trend}`;
  } catch (e) {
    box.textContent = "요약 정보를 불러오지 못했습니다: " + e.message;
  }
}

async function loadChart() {
  try {
    const items = await apiFetch("/api/data");
    const ctx = document.getElementById("trendChart");
    const labels = items.map((i) => i.date);
    const values = items.map((i) => i.value);

    if (trendChart) trendChart.destroy();
    trendChart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{ label: "값 추이", data: values, borderColor: "#3b6df0", tension: 0.3, pointRadius: 0 }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { ticks: { maxTicksLimit: 6 } } },
      },
    });
  } catch (e) {
    console.error("차트 로드 실패", e);
  }
}

// ---------- 데이터 관리 (CRUD) ----------
async function loadDataList() {
  const list = document.getElementById("dataList");
  list.innerHTML = "";
  const items = await apiFetch("/api/data");
  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${item.date} · ${item.value}${item.memo ? " · " + item.memo : ""}</span>
      <span class="row-actions">
        <button data-action="edit" data-id="${item.id}" data-value="${item.value}">✏️</button>
        <button data-action="delete" data-id="${item.id}">🗑️</button>
      </span>`;
    list.appendChild(li);
  });
}

document.getElementById("dataForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const date = document.getElementById("dataDate").value;
  const value = parseFloat(document.getElementById("dataValue").value);
  const memo = document.getElementById("dataMemo").value || null;

  await apiFetch("/api/data", { method: "POST", body: JSON.stringify({ date, value, memo }) });
  e.target.reset();
  await refreshDataViews();
});

document.getElementById("dataList").addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const id = btn.dataset.id;

  if (btn.dataset.action === "delete") {
    if (!confirm("이 데이터를 삭제할까요?")) return;
    await apiFetch(`/api/data/${id}`, { method: "DELETE" });
    await refreshDataViews();
  }

  if (btn.dataset.action === "edit") {
    const newValue = prompt("새 값을 입력하세요:", btn.dataset.value);
    if (newValue === null) return;
    await apiFetch(`/api/data/${id}`, {
      method: "PUT",
      body: JSON.stringify({ value: parseFloat(newValue) }),
    });
    await refreshDataViews();
  }
});

async function refreshDataViews() {
  await Promise.all([loadDataList(), loadSummary(), loadChart()]);
}

// ---------- 보너스: 내보내기 (CSV/JSON) ----------
function downloadFile(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

document.getElementById("exportCsvBtn").addEventListener("click", async () => {
  const items = await apiFetch("/api/data");
  const header = "date,value,memo\n";
  const rows = items.map((i) => `${i.date},${i.value},${i.memo || ""}`).join("\n");
  downloadFile("data_export.csv", header + rows, "text/csv");
});

document.getElementById("exportJsonBtn").addEventListener("click", async () => {
  const items = await apiFetch("/api/data");
  downloadFile("data_export.json", JSON.stringify(items, null, 2), "application/json");
});

// ---------- 대화 기록 ----------
async function loadConversationList() {
  const list = document.getElementById("conversationList");
  list.innerHTML = "";
  const conversations = await apiFetch("/api/conversations");
  conversations.forEach((conv) => {
    const li = document.createElement("li");
    li.textContent = `${conv.title} (${conv.message_count})`;
    li.addEventListener("click", () => loadConversation(conv.id));
    list.appendChild(li);
  });
}

async function loadConversation(id) {
  const detail = await apiFetch(`/api/conversations/${id}`);
  currentConversationId = detail.id;
  const chatWindow = document.getElementById("chatWindow");
  chatWindow.innerHTML = "";
  detail.messages.forEach((m) => appendBubble(m.role, m.content));
}

// ---------- 채팅 ----------
function appendBubble(role, content) {
  const chatWindow = document.getElementById("chatWindow");
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role === "user" ? "user" : "ai"}`;
  bubble.textContent = content;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

document.getElementById("chatForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;

  appendBubble("user", message);
  input.value = "";
  document.getElementById("loadingIndicator").classList.remove("hidden");

  try {
    const res = await apiFetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: currentConversationId }),
    });
    currentConversationId = res.conversation_id;
    appendBubble("assistant", res.reply);
    await loadConversationList();
  } catch (err) {
    appendBubble("assistant", "⚠️ 오류가 발생했습니다: " + err.message);
  } finally {
    document.getElementById("loadingIndicator").classList.add("hidden");
  }
});

// ---------- 보너스: 다크모드 ----------
document.getElementById("darkModeToggle").addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem("darkMode", document.body.classList.contains("dark"));
});
if (localStorage.getItem("darkMode") === "true") {
  document.body.classList.add("dark");
}

// ---------- 초기 로드 ----------
refreshDataViews();
loadConversationList();
