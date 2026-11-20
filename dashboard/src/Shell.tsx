import type { ReactNode } from "react";

export function Shell({ children }: { children: ReactNode }) {
  return (
    <main>
      <p className="tagline">Check the papers before you submit them.</p>
      <nav>
        <a href="/">Queue</a>
        <a href="/instructions">Instructions</a>
      </nav>
      <section className="panel">
        <h1>Policy Passer</h1>
        {children}
      </section>
    </main>
  );
}
