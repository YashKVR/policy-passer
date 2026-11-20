import { useEffect, useState } from "react";

type Health = "loading" | "up" | "down";

export function App() {
  const [health, setHealth] = useState<Health>("loading");

  useEffect(() => {
    void fetch("/api/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("health failed");
        }
        return response.json() as Promise<{ status: string }>;
      })
      .then((body) => {
        setHealth(body.status === "ok" ? "up" : "down");
      })
      .catch(() => {
        setHealth("down");
      });
  }, []);

  return (
    <main>
      <p className="tagline">Check the papers before you submit them.</p>
      <section className="panel">
        <h1>Policy Passer</h1>
        <p>{healthMessage(health)}</p>
      </section>
    </main>
  );
}

function healthMessage(health: Health): string {
  if (health === "loading") {
    return "Checking the backend.";
  }
  if (health === "up") {
    return "The backend is up.";
  }
  return "The backend is down.";
}
