import { navItems } from "../data/content";

export function Layout({ route, children }) {
  return (
    <>
      <div className="side-rail side-rail-left" aria-hidden="true">
        <div className="rail-card rail-card-primary">
          <small>Knowledge Core</small>
          <strong>RAG</strong>
          <span>14 chunks indexed</span>
        </div>
        <div className="rail-node-map">
          <i />
          <i />
          <i />
          <i />
        </div>
        <div className="rail-card">
          <small>Answer Mode</small>
          <strong>FAQ + AI</strong>
          <span>concise retrieval</span>
        </div>
      </div>
      <div className="side-rail side-rail-right" aria-hidden="true">
        <div className="rail-card rail-card-primary">
          <small>Program</small>
          <strong>255H</strong>
          <span>practical training</span>
        </div>
        <div className="rail-meter">
          <span style={{ "--h": "72%" }} />
          <span style={{ "--h": "46%" }} />
          <span style={{ "--h": "64%" }} />
          <span style={{ "--h": "38%" }} />
        </div>
        <div className="rail-card">
          <small>Campus</small>
          <strong>NUTN</strong>
          <span>Fucheng campus</span>
        </div>
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
