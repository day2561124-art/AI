import { Intro } from "../components/Intro";
import { courses } from "../data/content";

export function CoursesPage() {
  return (
    <>
      <Intro eyebrow="課程期別資訊" title="114 第 01 期與 115 第 02 期">
        不同期別的報名、補助、甄試與聯絡資訊必須分開查詢。
      </Intro>
      <section className="info-grid">
        {courses.map((course) => (
          <article className="info-card" key={course.title}>
            <h2>{course.title}</h2>
            <ul>{course.items.map((item) => <li key={item}>{item}</li>)}</ul>
          </article>
        ))}
      </section>
      <p className="notice-band">實際課程期別、名額、報名狀態與補助資格仍以官方最新公告為準。</p>
    </>
  );
}

