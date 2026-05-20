import { Intro } from "../components/Intro";
import { steps } from "../data/content";

export function ProcessPage() {
  return (
    <>
      <Intro eyebrow="流程導覽" title="申請與報名流程">
        使用者可先確認身分別，再前往適合的官方平台查詢與報名。
      </Intro>
      <section className="timeline">
        {steps.map(([title, body], index) => (
          <article key={title}>
            <span>{index + 1}</span>
            <h2>{title}</h2>
            <p>{body}</p>
          </article>
        ))}
      </section>
    </>
  );
}

