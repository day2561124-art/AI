import { useState } from "react";
import { Intro } from "../components/Intro";
import { quickQuestions } from "../data/content";
import { askQuestion, sendFeedback } from "../services/api";

export function ChatPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const uniqueSources = Array.from(new Set(answer?.sources || []));
  const shouldShowNotice = Boolean(
    answer?.notice && !answer?.answer?.includes(answer.notice)
  );

  async function submitQuestion(event) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setFeedbackStatus("");
    try {
      setAnswer(await askQuestion(question.trim()));
    } catch {
      setAnswer({
        answer: "目前無法連線到後端 API，請確認 FastAPI 是否已啟動。",
        sources: [],
        notice: "實際資訊仍以官方最新公告與承辦單位回覆為準。",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(helpful) {
    if (!answer) return;
    setFeedbackStatus("儲存回饋中...");
    try {
      await sendFeedback({
        question,
        answer: answer.answer,
        helpful,
        comment: null,
      });
      setFeedbackStatus(helpful ? "已儲存有幫助回饋。" : "已儲存需改善回饋。");
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
        根據整合知識庫回答課程、報名、補助、甄試、聯絡方式、職前訓練與在職訓練問題。
      </Intro>
      <section className="chat-panel">
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
        <form className="chat-form" onSubmit={submitQuestion}>
          <label htmlFor="question">請輸入問題</label>
          <textarea
            id="question"
            rows="4"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="例如：我要怎麼報名 AI智慧應用產業人才培訓班？"
          />
          <button type="submit">{loading ? "查詢中..." : "送出問題"}</button>
        </form>
        {answer && (
          <article className="answer-box">
            <h2>回答</h2>
            <p>{answer.answer}</p>
            <h3>來源依據</h3>
            <ul>
              {(uniqueSources.length ? uniqueSources : ["目前沒有可引用的明確來源"]).map((source) => (
                <li key={source}>{source}</li>
              ))}
            </ul>
            {shouldShowNotice && (
              <>
                <h3>注意事項</h3>
                <p>{answer.notice}</p>
              </>
            )}
            <div className="feedback-actions">
              <button type="button" onClick={() => handleFeedback(true)}>有幫助</button>
              <button type="button" onClick={() => handleFeedback(false)}>需改善</button>
            </div>
            <p className="feedback-status">{feedbackStatus}</p>
          </article>
        )}
      </section>
    </>
  );
}
