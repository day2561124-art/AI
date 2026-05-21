import { Intro } from "../components/Intro";

const platformLinks = [
  {
    label: "台灣就業通課程頁面",
    description: "115 年第 02 期立即報名",
    href: "https://its.taiwanjobs.gov.tw/Course/Detail?ID=161756",
  },
  {
    label: "114 年第 01 期報名頁",
    description: "知識庫公告提供之報名網址",
    href: "https://reurl.cc/eVd7bQ",
  },
  {
    label: "課程簡介",
    description: "AI智慧應用產業人才培訓班介紹",
    href: "https://pse.is/85tqme",
  },
  {
    label: "國立臺南大學 AI 據點",
    description: "AI 智慧技術與應用人才培訓據點",
    href: "https://ppt.cc/f5cezx",
  },
];

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
          <div className="link-list">
            {platformLinks.map((item) => (
              <a
                key={item.href}
                href={item.href}
                target="_blank"
                rel="noreferrer"
                aria-label={`${item.label}，另開新視窗`}
              >
                <span>{item.label}</span>
                <small>{item.description}</small>
              </a>
            ))}
          </div>
        </article>
      </section>
    </>
  );
}
