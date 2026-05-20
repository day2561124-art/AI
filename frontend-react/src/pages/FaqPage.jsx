import { Intro } from "../components/Intro";
import { faqs } from "../data/content";

export function FaqPage() {
  return (
    <>
      <Intro eyebrow="FAQ" title="常見問題">
        回答以知識庫整理內容為基礎，若無明確資料必須以官方回覆為準。
      </Intro>
      <section className="faq-list">
        {faqs.map(([question, answer]) => (
          <article key={question}>
            <h2>{question}</h2>
            <p>{answer}</p>
          </article>
        ))}
      </section>
    </>
  );
}

