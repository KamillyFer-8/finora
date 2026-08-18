import { ForgotPasswordForm } from "@/features/auth/forgot-password-form";

export default function ForgotPasswordPage() {
  return <><h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Recuperar senha</h1><p className="mb-8 mt-2 text-sm text-muted">Enviaremos instruções caso o e-mail esteja cadastrado.</p><ForgotPasswordForm /></>;
}
