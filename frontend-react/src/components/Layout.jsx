import { navItems } from "../data/content";

export function Layout({ route, children }) {
  return (
    <main className="app-shell">
      <nav className="top-nav" aria-label="Main navigation">
        {navItems.map(([id, label]) => (
          <a key={id} className={route === id ? "active" : ""} href={`#/${id}`}>
            {label}
          </a>
        ))}
      </nav>
      {children}
    </main>
  );
}

