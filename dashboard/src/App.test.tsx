import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { App } from "./App";
import { decidedCheck, queue, instructions } from "./fixtures";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.history.pushState({}, "", "/");
});

test("shows the queue and that the backend is up", async () => {
  window.history.pushState({}, "", "/");
  mockFetch({
    "/api/health": { status: "ok" },
    "/api/checks": queue,
  });
  render(<App />);
  expect(await screen.findByText("The backend is up.")).toBeTruthy();
  expect(screen.getByText("CHK-1001").closest("li")?.textContent).toContain(
    "waiting",
  );
  expect(screen.getByText("CHK-1002").closest("li")?.textContent).toContain(
    "waiting",
  );
  expect(screen.getByText("CHK-1003").closest("li")?.textContent).toContain(
    "decided",
  );
});

test("shows an unknown status as it is stored", async () => {
  mockFetch({
    "/api/health": { status: "ok" },
    "/api/checks": [{ id: "CHK-1004", title: "Other", status: "paused" }],
  });
  render(<App />);
  expect(await screen.findByText("paused")).toBeTruthy();
});

test("shows the backend is down when health fails", async () => {
  mockFetch({});
  render(<App />);
  expect(await screen.findByText("The backend is down.")).toBeTruthy();
  expect(await screen.findByText("The queue is unavailable.")).toBeTruthy();
});

test("shows the backend is down when the status is not ok", async () => {
  mockFetch({
    "/api/health": { status: "starting" },
    "/api/checks": queue,
  });
  render(<App />);
  expect(await screen.findByText("The backend is down.")).toBeTruthy();
});

test("shows a decided check", async () => {
  window.history.pushState({}, "", "/checks/CHK-1003");
  mockFetch({
    "/api/checks/CHK-1003": decidedCheck,
    "/api/checks/CHK-1003/activity": [
      { message: "Read the baggage section of the policy." },
      {
        message:
          "Checked the papers for a police report filed within 24 hours.",
      },
    ],
  });
  render(<App />);
  expect(await screen.findByText("rejected")).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Run check" })).toBeNull();
  expect(
    screen.getByText(/No police report for a theft of \$300\.00/),
  ).toBeTruthy();
  expect(
    screen.getByText(
      "The policy requires a police report filed within 24 hours.",
    ),
  ).toBeTruthy();
  expect(
    screen.getByText("Read the baggage section of the policy."),
  ).toBeTruthy();
  expect(
    screen.getByText(
      "Checked the papers for a police report filed within 24 hours.",
    ),
  ).toBeTruthy();
});

test("shows a waiting check with no mistakes", async () => {
  window.history.pushState({}, "", "/checks/CHK-1001");
  mockFetch({
    "/api/checks/CHK-1001": {
      ...decidedCheck,
      id: "CHK-1001",
      title: "Maya Chen, emergency treatment",
      status: "waiting",
      outcome: "",
      explanation: "",
      policy_section: "",
      mistakes: [],
      claim_papers: "Itemized receipt attached for $480.00.",
    },
    "/api/checks/CHK-1001/activity": [],
  });
  render(<App />);
  expect(await screen.findByText("not decided")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Run check" })).toBeTruthy();
  expect(screen.getByText("No mistakes.")).toBeTruthy();
  expect(screen.getByText(/\$480\.00/)).toBeTruthy();
});

test("runs a waiting check and polls the activity", async () => {
  vi.useFakeTimers({ toFake: ["setInterval", "clearInterval"] });
  window.history.pushState({}, "", "/checks/CHK-1001");
  let runs = 0;
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/activity")) {
        runs += 1;
        const steps = runs > 1 ? [{ message: "Reading the policy copy." }] : [];
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(steps),
        });
      }
      if (url.endsWith("/run")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ...decidedCheck,
              id: "CHK-1001",
              status: "decided",
              outcome: "approved",
              explanation: "The papers are ready to submit.",
              mistakes: [],
            }),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            ...decidedCheck,
            id: "CHK-1001",
            status: "waiting",
            outcome: "",
            explanation: "",
            policy_section: "",
            mistakes: [],
          }),
      });
    }),
  );
  render(<App />);
  const button = await screen.findByRole("button", { name: "Run check" });
  button.click();
  await vi.advanceTimersByTimeAsync(1000);
  expect(await screen.findByText("Reading the policy copy.")).toBeTruthy();
  expect(await screen.findByText("approved")).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Run check" })).toBeNull();
  vi.useRealTimers();
});

test("shows when a check cannot be run", async () => {
  window.history.pushState({}, "", "/checks/CHK-1001");
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/run")) {
        return Promise.resolve({
          ok: false,
          status: 409,
          json: () => Promise.resolve({}),
        });
      }
      if (url.endsWith("/activity")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
      }
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            ...decidedCheck,
            id: "CHK-1001",
            status: "waiting",
            outcome: "",
            explanation: "",
            policy_section: "",
            mistakes: [],
          }),
      });
    }),
  );
  render(<App />);
  (await screen.findByRole("button", { name: "Run check" })).click();
  expect(await screen.findByText("The check could not be run.")).toBeTruthy();
});

test("shows a missing check", async () => {
  window.history.pushState({}, "", "/checks/CHK-404");
  mockFetch({});
  render(<App />);
  expect(await screen.findByText("Check not found.")).toBeTruthy();
});

test("shows the instructions without an editor", async () => {
  window.history.pushState({}, "", "/instructions");
  mockFetch({ "/api/instructions": { instructions } });
  render(<App />);
  expect(await screen.findByText(/Do not submit the papers/)).toBeTruthy();
  expect(screen.queryByRole("textbox")).toBeNull();
  expect(screen.queryByRole("button")).toBeNull();
});

test("shows when the instructions cannot be loaded", async () => {
  window.history.pushState({}, "", "/instructions");
  mockFetch({});
  render(<App />);
  expect(await screen.findByText("Instructions are unavailable.")).toBeTruthy();
});

function mockFetch(routes: Record<string, unknown>) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const body = routes[String(input)];
      if (body === undefined) {
        return Promise.resolve({
          ok: false,
          status: 404,
          json: () => Promise.resolve({}),
        });
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(body),
      });
    }),
  );
}
