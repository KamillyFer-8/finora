import { expect, test } from "@playwright/test";

test("authenticated user can navigate the completed application shell", async ({ page }, testInfo) => {
  const email = `portfolio-${testInfo.project.name}-${Date.now()}@example.com`;
  await page.goto("/cadastro");
  await page.getByLabel("Nome").fill("Usuária Portfólio");
  await page.getByLabel("E-mail").fill(email);
  await page.getByLabel("Senha").fill("senha-segura-portfolio");
  await page.getByRole("button", { name: "Criar conta" }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByRole("navigation", { name: "Principal" })).toBeVisible();
  if (testInfo.project.name === "mobile-chrome") await page.getByRole("button", { name: "Abrir menu" }).click();
  await page.getByRole("link", { name: "Transações" }).click();
  await expect(page.getByRole("heading", { name: "Transações" })).toBeVisible();
  await page.getByRole("button", { name: "Nova transação" }).click();
  await expect(page.getByLabel("Recorrência")).toBeVisible();
  await expect(page.getByText("Comprovante (opcional)")).toBeVisible();
  await page.goto("/configuracoes");
  await expect(page.getByRole("heading", { name: "Configurações" })).toBeVisible();
  await page.goto("/ajuda");
  await expect(page.getByRole("heading", { name: "Ajuda" })).toBeVisible();
  await page.goto("/perfil");
  await expect(page.getByText(email)).toBeVisible();
});
