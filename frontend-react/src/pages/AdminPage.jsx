import { useEffect, useMemo, useState } from "react";
import { Intro } from "../components/Intro";
import { RecordList } from "../components/RecordList";
import {
  getAdminStats,
  getChatLogs,
  getFeedback,
  getUnanswered,
  getVisits,
  reloadKnowledge,
  uploadKnowledge,
} from "../services/api";

const TOKEN_KEY = "ai_customer_service_admin_token";

export function AdminPage() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");
  const [tokenInput, setTokenInput] = useState(token);
  const [stats, setStats] = useState(null);
  const [chatLogs, setChatLogs] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [unanswered, setUnanswered] = useState([]);
  const [visits, setVisits] = useState([]);
  const [knowledgeFile, setKnowledgeFile] = useState(null);
  const [knowledgeStatus, setKnowledgeStatus] = useState("");
  const [error, setError] = useState("");

  async function loadAdmin(activeToken = token) {
    if (!activeToken) return;
    setError("");
    try {
      const [statsData, logsData, feedbackData, unansweredData, visitsData] = await Promise.all([
        getAdminStats(activeToken),
        getChatLogs(activeToken),
        getFeedback(activeToken),
        getUnanswered(activeToken),
        getVisits(activeToken),
      ]);
      setStats(statsData);
      setChatLogs(logsData.items || []);
      setFeedback(feedbackData.items || []);
      setUnanswered(unansweredData.items || []);
      setVisits(visitsData.items || []);
    } catch {
      setStats(null);
      setChatLogs([]);
      setFeedback([]);
      setUnanswered([]);
      setVisits([]);
      setError("管理 token 無效，或後端 API 尚未啟動。");
    }
  }

  useEffect(() => {
    loadAdmin(token);
  }, []);

  function login(event) {
    event.preventDefault();
    const value = tokenInput.trim();
    localStorage.setItem(TOKEN_KEY, value);
    setToken(value);
    loadAdmin(value);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken("");
    setTokenInput("");
    setStats(null);
    setChatLogs([]);
    setFeedback([]);
    setUnanswered([]);
    setVisits([]);
    setKnowledgeStatus("");
    setError("");
  }

  async function handleReload() {
    setKnowledgeStatus("重新載入知識庫中...");
    try {
      const result = await reloadKnowledge(token);
      setKnowledgeStatus(`已重新載入，chunk 數量：${result.chunk_count}`);
    } catch {
      setKnowledgeStatus("重新載入失敗，請確認 token 與後端 API。");
    }
  }

  async function handleUpload(event) {
    event.preventDefault();
    if (!knowledgeFile) {
      setKnowledgeStatus("請先選擇 TXT 知識庫檔案。");
      return;
    }
    setKnowledgeStatus("上傳並重建知識庫中...");
    try {
      const result = await uploadKnowledge(token, knowledgeFile);
      setKnowledgeStatus(`已上傳 ${result.filename}，chunk 數量：${result.chunk_count}`);
      await loadAdmin(token);
    } catch {
      setKnowledgeStatus("上傳失敗，僅支援非空白的 .txt 檔案。");
    }
  }

  const statCards = useMemo(
    () => [
      ["總瀏覽次數", stats?.visit_count ?? 0],
      ["不重複訪客", stats?.unique_visitor_count ?? 0],
      ["重複瀏覽次數", stats?.repeat_visit_count ?? 0],
      ["重複訪客數", stats?.repeat_visitor_count ?? 0],
      ["問答次數", stats?.chat_count ?? 0],
      ["CAG 快取命中", stats?.cag_count ?? 0],
      ["RAG 問答", stats?.rag_count ?? 0],
      ["Memory 使用", stats?.memory_count ?? 0],
      ["LLM 使用", stats?.llm_count ?? 0],
      ["回饋總數", stats?.feedback_count ?? 0],
      ["有幫助", stats?.helpful_count ?? 0],
      ["沒幫助", stats?.not_helpful_count ?? 0],
      ["有幫助比例", `${stats?.helpful_rate ?? 0}%`],
      ["無法回答", stats?.unanswered_count ?? 0],
    ],
    [stats],
  );

  return (
    <>
      <Intro eyebrow="工作人員後台" title="服務成效與知識庫管理">
        追蹤瀏覽人數、重複瀏覽、問答紀錄、使用者回饋與無法回答問題，並管理客服知識庫。
      </Intro>

      <section className="chat-panel admin-login">
        <form className="chat-form" onSubmit={login}>
          <label htmlFor="adminToken">管理 Token</label>
          <input
            id="adminToken"
            type="password"
            value={tokenInput}
            onChange={(event) => setTokenInput(event.target.value)}
            placeholder="預設開發 token：dev-admin-token"
          />
          <div className="feedback-actions">
            <button type="submit">登入後台</button>
            {token && <button type="button" onClick={logout}>登出</button>}
          </div>
        </form>
        {error && <p className="feedback-status">{error}</p>}
      </section>

      {token && stats && (
        <>
          <section className="chat-panel knowledge-tools">
            <div className="admin-section-heading">
              <span>Knowledge Base</span>
              <h2>知識庫管理</h2>
              <p>更新 TXT 知識庫後，系統會重新建立檢索資料，讓 AI 回答使用最新內容。</p>
            </div>
            <form className="chat-form" onSubmit={handleUpload}>
              <label htmlFor="knowledgeFile">上傳新的 TXT 知識庫</label>
              <input
                id="knowledgeFile"
                type="file"
                accept=".txt,text/plain"
                onChange={(event) => setKnowledgeFile(event.target.files?.[0] || null)}
              />
              <div className="feedback-actions">
                <button type="submit">上傳並重建</button>
                <button type="button" onClick={handleReload}>重新載入目前知識庫</button>
              </div>
            </form>
            {knowledgeStatus && <p className="feedback-status">{knowledgeStatus}</p>}
          </section>

          <section className="metric-grid">
            {statCards.map(([label, value]) => (
              <article className="metric-card" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </article>
            ))}
          </section>

          <section className="admin-grid">
            <AdminCard title="瀏覽紀錄">
              <VisitList rows={visits} />
            </AdminCard>
            <AdminCard title="無法回答">
              <RecordList rows={unanswered} emptyText="目前沒有無法回答問題。" />
            </AdminCard>
            <AdminCard title="使用者回饋">
              <FeedbackList rows={feedback} />
            </AdminCard>
            <AdminCard title="最新問答紀錄">
              <RecordList rows={chatLogs} emptyText="目前沒有問答紀錄。" />
            </AdminCard>
          </section>
        </>
      )}
    </>
  );
}

function AdminCard({ title, children }) {
  return <article><h2>{title}</h2>{children}</article>;
}

function formatTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("zh-TW", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function shortId(value = "") {
  return value ? value.slice(0, 8) : "unknown";
}

function FeedbackList({ rows }) {
  if (!rows.length) return <p>目前沒有回饋。</p>;
  return (
    <div className="record-list">
      {rows.map((row) => (
        <div className="record-item feedback-record" key={row.id}>
          <strong>{row.helpful ? "有幫助" : "沒幫助"}</strong>
          <small>{formatTime(row.created_at)} ｜ 訪客 {shortId(row.visitor_id)}</small>
          <p>{row.question}</p>
        </div>
      ))}
    </div>
  );
}

function VisitList({ rows }) {
  if (!rows.length) return <p>目前沒有瀏覽紀錄。</p>;
  return (
    <div className="record-list">
      {rows.map((row) => (
        <div className="record-item visit-record" key={row.id}>
          <strong>{routeLabel(row.page)}</strong>
          <small>{formatTime(row.created_at)} ｜ 訪客 {shortId(row.visitor_id)}</small>
          <p>{row.path}</p>
        </div>
      ))}
    </div>
  );
}

function routeLabel(route) {
  const labels = {
    chat: "AI 問答",
    courses: "課程資訊",
    faq: "FAQ",
    process: "報名流程",
    contact: "聯絡資訊",
    admin: "管理後台",
  };
  return labels[route] || route || "未知頁面";
}
