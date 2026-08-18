import { AuthForm } from "@/features/auth/auth-form";

export default function RegisterPage() {
  return <><h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight">Crie sua conta</h1><p className="mb-8 mt-2 text-sm text-muted">Comece a construir uma vida financeira mais clara.</p><AuthForm mode="register" /></>;
}
