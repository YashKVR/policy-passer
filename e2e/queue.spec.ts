import { expect, test } from "@playwright/test";

test("shows the queue", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("link", { name: /CHK-1001/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /CHK-1002/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /CHK-1003/ })).toBeVisible();
  await expect(page.getByText("waiting").first()).toBeVisible();
  await expect(page.getByText("decided")).toBeVisible();
});

test("shows a decided check", async ({ page }) => {
  await page.goto("/checks/CHK-1003");
  await expect(page.getByText("rejected", { exact: true })).toBeVisible();
  await expect(
    page.getByText(/No police report for a theft of \$300\.00/),
  ).toBeVisible();
  await expect(
    page.getByText(
      "The policy requires a police report filed within 24 hours.",
    ),
  ).toBeVisible();
  await expect(
    page.getByText("Read the baggage section of the policy."),
  ).toBeVisible();
  await expect(
    page.getByText(
      "Checked the papers for a police report filed within 24 hours.",
    ),
  ).toBeVisible();
  await expect(page.getByText("$300.00").first()).toBeVisible();
  await expect(page.getByRole("button", { name: "Run check" })).toHaveCount(0);
});

test("shows run on a waiting check", async ({ page }) => {
  await page.goto("/checks/CHK-1001");
  await expect(page.getByRole("button", { name: "Run check" })).toBeVisible();
});

test("shows the instructions without an editor", async ({ page }) => {
  await page.goto("/instructions");
  await expect(page.getByText("Do not submit the papers.")).toBeVisible();
  await expect(page.locator("textarea, input, button")).toHaveCount(0);
});
