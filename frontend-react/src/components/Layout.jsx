import { navItems } from "../data/content";

export function Layout({ route, children }) {
  return (
    <>
      <div className="side-rail side-rail-left" aria-hidden="true">
        <span>RAG</span>
        <span>FAQ</span>
        <span>AI</span>
      </div>
      <div className="side-rail side-rail-right" aria-hidden="true">
        <span>255H</span>
        <span>NUTN</span>
        <span>QA</span>
      </div>
      <main className="app-shell">
        <header className="site-header">
          <a className="brand-mark" href="#/chat" aria-label="AI智慧客服問答系統">
            AI
          </a>
          <nav className="top-nav" aria-label="Main navigation">
            {navItems.map(([id, label]) => (
              <a key={id} className={route === id ? "active" : ""} href={`#/${id}`}>
                {label}
              </a>
            ))}
          </nav>
        </header>
        {children}
      </main>
    </>
  );
}
