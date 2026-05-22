import { useEffect, useMemo, useRef, useState } from "react";
import { Intro } from "../components/Intro";
import { quickQuestions } from "../data/content";
import { askQuestion, getPublicChatHistory, sendFeedback } from "../services/api";

function cleanAnswerText(text = "") {
  const markers = ["來源依據：", "來源依據:", "注意事項：", "注意事項:"];
  const cutIndex = markers
    .map((marker) => text.indexOf(marker))
    .filter((index) => index >= 0)
    .sort((a, b) => a - b)[0];
  return (cutIndex >= 0 ? text.slice(0, cutIndex) : text).trim();
}

export function ChatPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      text: "您好，我可以協助查詢 AI智慧應用產業人才培訓班的課程、報名、補助、甄試與聯絡資訊。",
      sources: ["整合知識庫"],
      notice: "實際資訊仍以官方最新公告與承辦單位回覆為準。",
    },
  ]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const messagesEndRef = useRef(null);
  const historyPreview = useMemo(() => history.slice(0, 12), [history]);

  async function loadHistory() {
    try {
      const data = await getPublicChatHistory(40);
      setHistory(data.items || []);
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  async function submitQuestion(event) {
    event.preventDefault();
    const currentQuestion = question.trim();
    if (!currentQuestion) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      text: currentQuestion,
    };
    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setLoading(true);
    setFeedbackStatus("");
    try {
      const response = await askQuestion(currentQuestion);
      setMessages((current) => [
        ...current,
        {
          id: response.conversation_id || `assistant-${Date.now()}`,
          role: "assistant",
          text: response.answer,
          question: currentQuestion,
          rawAnswer: response.answer,
          conversationId: response.conversation_id,
          sources: response.sources || [],
          notice: response.notice,
        },
      ]);
      loadHistory();
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: `assistant-error-${Date.now()}`,
          role: "assistant",
          text: "目前無法連線到後端 API，請稍後再試。",
          sources: [],
          notice: "實際資訊仍以官方最新公告與承辦單位回覆為準。",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(message, helpful) {
    setFeedbackStatus("儲存回饋中...");
    try {
      await sendFeedback({
        question: message.question || "",
        answer: message.rawAnswer || message.text,
        helpful,
        conversation_id: message.conversationId,
        comment: null,
      });
      setFeedbackStatus(helpful ? "已儲存有幫助回饋。" : "已儲存沒幫助回饋。");
    } catch {
      setFeedbackStatus("回饋儲存失敗。");
    }
  }

  return (
    <>
      <Intro
        eyebrow="國立臺南大學 × 勞動部勞動力發展署雲嘉南分署｜AI智慧應用產業人才培訓班"
        title="AI智慧客服問答系統"
      >
        根據整合知識庫回答課程、報名、補助、甄試、聯絡方式與職前訓練問題。
      </Intro>
      <section className="chat-panel">
        <div className="chat-layout">
          <div className="messenger">
            <div className="quick-actions">
              {quickQuestions.map((item) => (
                <button
                  key={item.question}
                  type="button"
                  title={item.question}
                  onClick={() => setQuestion(item.question)}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div className="message-list" aria-live="polite">
              {messages.map((message) => (
                <ChatBubble
                  key={message.id}
                  message={message}
                  onFeedback={handleFeedback}
                />
              ))}
              {loading && (
                <div className="message-row assistant">
                  <div className="avatar">AI</div>
                  <div className="message-bubble typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <form className="chat-composer" onSubmit={submitQuestion}>
              <label className="sr-only" htmlFor="question">請輸入問題</label>
              <textarea
                id="question"
                rows="2"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="輸入問題，例如：115 年第 02 期報名截止時間？"
              />
              <button type="submit" disabled={loading || !question.trim()}>
                {loading ? "查詢中" : "送出"}
              </button>
            </form>
            <p className="feedback-status">{feedbackStatus}</p>
          </div>

          <aside className="history-panel" aria-label="過往歷史聊天紀錄">
            <div className="history-heading">
              <span>History</span>
              <h2>大家最近問過</h2>
              <p>匿名顯示所有使用者在此網站提出過的問題。</p>
            </div>
            <div className="history-list">
              {historyPreview.length ? (
                historyPreview.map((item) => (
                  <button
                    className="history-item"
                    key={item.id}
                    type="button"
                    onClick={() => setQuestion(item.question)}
                    title="套用這個問題"
                  >
                    <strong>{item.question}</strong>
                    <small>{formatTime(item.created_at)} · {item.category_label || "一般問題"}</small>
                  </button>
                ))
              ) : (
                <p className="history-empty">目前還沒有公開提問紀錄。</p>
              )}
            </div>
          </aside>
        </div>
      </section>
    </>
  );
}

function ChatBubble({ message, onFeedback }) {
  const isUser = message.role === "user";
  const displayText = cleanAnswerText(message.text);
  const uniqueSources = Array.from(new Set(message.sources || []));

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      {!isUser && <div className="avatar">AI</div>}
      <div className="message-bubble">
        <p>{displayText || message.text}</p>
        {!isUser && message.conversationId && (
          <div className="message-meta">
            {uniqueSources.length > 0 && (
              <details>
                <summary>來源依據</summary>
                <ul>
                  {uniqueSources.map((source) => (
                    <li key={source}>{source}</li>
                  ))}
                </ul>
              </details>
            )}
            {message.notice && (
              <details>
                <summary>注意事項</summary>
                <p>{message.notice}</p>
              </details>
            )}
            <div className="bubble-feedback">
              <button type="button" onClick={() => onFeedback(message, true)}>有幫助</button>
              <button type="button" onClick={() => onFeedback(message, false)}>沒幫助</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function formatTime(value) {
  if (!value) return "剛剛";
  return new Date(value).toLocaleString("zh-TW", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
