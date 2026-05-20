import React, { useEffect, useMemo, useState } from "react";
import { Intro } from "../components/Intro";
import { RecordList } from "../components/RecordList";
import {
  getAdminStats,
  getChatLogs,
  getFeedback,
  getUnanswered,
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
  const [knowledgeFile, setKnowledgeFile] = useState(null);
  const [knowledgeStatus, setKnowledgeStatus] = useState("");
  const [error, setError] = useState("");

  async function loadAdmin(activeToken = token) {
    if (!activeToken) return;
    setError("");
    try {
      const [statsData, logsData, feedbackData, unansweredData] = await Promise.all([
        getAdminStats(activeToken),
        getChatLogs(activeToken),
        getFeedback(activeToken),
        getUnanswered(activeToken),
      ]);
      setStats(statsData);
      setChatLogs(logsData.items || []);
      setFeedback(feedbackData.items || []);
      setUnanswered(unansweredData.items || []);
    } catch {
      setStats(null);
      setChatLogs([]);
      setFeedback([]);
      setUnanswered([]);
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

  const statItems = useMemo(() => Object.entries(stats || {}), [stats]);

  return (
    <>
      <Intro eyebrow="管理後台" title="問答紀錄、回饋與知識庫管理">
        查看問答紀錄、使用者回饋、無法回答問題，並可上傳新的 TXT 知識庫重新建立檢索資料。
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
            <h2>知識庫管理</h2>
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

          <section className="admin-grid">
            <AdminCard title="統計">
              <dl>{statItems.map(([key, value]) => <React.Fragment key={key}><dt>{key}</dt><dd>{String(value)}</dd></React.Fragment>)}</dl>
            </AdminCard>
            <AdminCard title="無法回答">
              <RecordList rows={unanswered} emptyText="目前沒有無法回答問題。" />
            </AdminCard>
            <AdminCard title="使用者回饋">
              <RecordList rows={feedback} emptyText="目前沒有回饋。" />
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
