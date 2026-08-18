"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api/client";

export function ResetPasswordForm({ token }: { token: string }) {
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const { data } = await apiClient.post("/auth/reset-password", { token, new_password: password });
    setMessage(data.message);
  }
  return <form onSubmit={submit} className="grid gap-5"><Input label="Nova senha" type="password" minLength={10} required value={password} onChange={(event) => setPassword(event.target.value)} />{message ? <p role="status" className="rounded-xl bg-primary/10 p-3 text-sm text-primary">{message}</p> : null}<Button type="submit">Redefinir senha</Button></form>;
}
