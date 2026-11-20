import { screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

afterEach(() => {
  vi.resetModules();
  vi.unstubAllGlobals();
  document.body.innerHTML = "";
});

test("mounts into the root element", async () => {
  document.body.innerHTML = '<div id="root"></div>';
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    }),
  );
  await import("./main");
  expect(await screen.findByText("Policy Passer")).toBeTruthy();
});

test("throws when the root element is missing", async () => {
  document.body.innerHTML = "";
  await expect(import("./main")).rejects.toThrow("Root element is missing");
});
