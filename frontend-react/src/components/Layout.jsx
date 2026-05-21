import { navItems } from "../data/content";

export function Layout({ route, children }) {
  return (
    <>
      <div className="side-rail side-rail-left" aria-hidden="true">
        <div className="rail-card rail-card-primary">
          <small>知識核心</small>
          <strong>知識檢索</strong>
          <span>14 個知識段落</span>
        </div>
        <div className="rail-node-map">
          <i />
          <i />
          <i />
          <i />
        </div>
        <div className="rail-card">
          <small>回答模式</small>
          <strong>AI 問答</strong>
          <span>精簡回答</span>
        </div>
      </div>
      <div className="side-rail side-rail-right" aria-hidden="true">
        <div className="rail-card rail-card-primary">
          <small>課程規劃</small>
          <strong>255 小時</strong>
          <span>實戰培訓</span>
        </div>
        <div className="rail-meter">
          <span style={{ "--h": "72%" }} />
          <span style={{ "--h": "46%" }} />
          <span style={{ "--h": "64%" }} />
          <span style={{ "--h": "38%" }} />
        </div>
        <div className="rail-card">
          <small>校區資訊</small>
          <strong>臺南大學</strong>
          <span>府城校區</span>
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
