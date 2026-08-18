import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("landing page has no automatically detectable accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test("login exposes validation feedback and remains usable on mobile", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Entrar" }).waitFor();
  await page.getByLabel("E-mail").fill("invalido");
  await page.getByLabel("Senha").fill("curta");
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page.getByText("Informe um e-mail válido")).toBeVisible();
  await expect(page.getByText("Use pelo menos 10 caracteres")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Boas-vindas" })).toBeVisible();
});
