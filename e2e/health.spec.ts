import { expect, test } from "@playwright/test";

test("shows the backend is up", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("The backend is up.")).toBeVisible();
});
