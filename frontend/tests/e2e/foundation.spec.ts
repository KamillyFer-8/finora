import { expect, test } from "@playwright/test";

test("shows the Finora foundation", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Decisões melhores");
});
