import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { AppShell } from "@/components/app-shell";

export default async function ProtectedLayout({ children }: { children: ReactNode }) {
  if (!(await cookies()).has("access_token")) redirect("/login");
  return <><a href="#main-content" className="skip-link">Pular para o conteúdo</a><div id="main-content" tabIndex={-1}><AppShell>{children}</AppShell></div></>;
}
