export function Intro({ eyebrow, title, children }) {
  return (
    <section className="intro">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p>{children}</p>
    </section>
  );
}

