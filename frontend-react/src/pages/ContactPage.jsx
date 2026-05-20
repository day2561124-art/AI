import { Intro } from "../components/Intro";

export function ContactPage() {
  return (
    <>
      <Intro eyebrow="聯絡方式" title="官方聯絡與查詢">
        涉及最新梯次、個人資格、補助核定與錄取結果時，請以官方回覆為準。
      </Intro>
      <section className="info-grid">
        <article className="info-card">
          <h2>國立臺南大學 AI 據點</h2>
          <p>聯絡電話：06-213-0019 或 06-2130019</p>
          <p>官方 LINE：@270jdtoe</p>
          <p>訓練地點：臺南市中西區樹林街二段33號</p>
        </article>
        <article className="info-card">
          <h2>查詢平台</h2>
          <ul>
            <li>台灣就業通</li>
            <li>職前訓練網</li>
            <li>產業新尖兵相關頁面</li>
            <li>勞動部在職訓練網</li>
            <li>國立臺南大學 AI 智慧技術與應用人才培訓據點</li>
          </ul>
        </article>
      </section>
    </>
  );
}

