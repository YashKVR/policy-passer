import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";
import { App } from "./App";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("App", () => {
  test("shows the backend is up", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );
    render(<App />);
    expect(await screen.findByText("The backend is up.")).toBeTruthy();
  });

  test("shows the backend is down when health fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    render(<App />);
    expect(await screen.findByText("The backend is down.")).toBeTruthy();
  });

  test("shows the backend is down when the status is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "starting" }),
      }),
    );
    render(<App />);
    expect(await screen.findByText("The backend is down.")).toBeTruthy();
  });

  test("shows the backend is down when the response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );
    render(<App />);
    expect(await screen.findByText("The backend is down.")).toBeTruthy();
  });
});
