"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api/client";

export function ForgotPasswordForm() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [resetToken, setResetToken] = useState("");
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const { data } = await apiClient.post("/auth/forgot-password", { email });
    setMessage(data.message);
    setResetToken(data.reset_token ?? "");
  }
  return <form onSubmit={submit} className="grid gap-5"><Input label="E-mail" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} />{message ? <p role="status" className="rounded-xl bg-primary/10 p-3 text-sm text-primary">{message}</p> : null}{resetToken ? <Link className="text-center text-sm font-semibold text-primary" href={`/resetar-senha?token=${encodeURIComponent(resetToken)}`}>Abrir link de desenvolvimento</Link> : null}<Button type="submit">Enviar instruções</Button></form>;
}
