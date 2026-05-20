import { navItems } from "../data/content";

export function Layout({ route, children }) {
  return (
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
  );
}
