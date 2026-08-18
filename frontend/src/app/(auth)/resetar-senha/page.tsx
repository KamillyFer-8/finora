import { ResetPasswordForm } from "@/features/auth/reset-password-form";

export default async function ResetPasswordPage({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const { token } = await searchParams;
  return <><h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold">Nova senha</h1><p className="mb-8 mt-2 text-sm text-muted">Escolha uma senha forte e exclusiva.</p>{token ? <ResetPasswordForm token={token} /> : <p role="alert" className="text-danger">Link de recuperação inválido.</p>}</>;
}
