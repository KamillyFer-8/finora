import type { Metadata } from "next";
import { AppProviders } from "@/providers/app-providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Finora — Clareza para suas finanças",
  description: "Fundação da plataforma de gestão financeira pessoal Finora.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body className="font-[family-name:var(--font-body)] antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
