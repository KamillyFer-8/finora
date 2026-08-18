import { AuthForm } from "@/features/auth/auth-form";

export default function LoginPage() {
  return <><h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight">Boas-vindas</h1><p className="mb-8 mt-2 text-sm text-muted">Acesse sua visão financeira com segurança.</p><AuthForm mode="login" /></>;
}
