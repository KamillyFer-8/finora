"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api/client";

const schema = z.object({ name: z.string().min(2, "Informe seu nome").optional(), email: z.email("Informe um e-mail válido"), password: z.string().min(10, "Use pelo menos 10 caracteres") });
type Fields = z.infer<typeof schema>;

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const [serverError, setServerError] = useState("");
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<Fields>({ resolver: zodResolver(schema) });
  const isRegister = mode === "register";
  async function submit(fields: Fields) {
    setServerError("");
    try {
      await apiClient.post(`/auth/${isRegister ? "register" : "login"}`, fields);
      router.replace("/dashboard");
      router.refresh();
    } catch (error) {
      setServerError(axios.isAxiosError(error) ? error.response?.data?.detail ?? "Não foi possível entrar." : "Erro inesperado.");
    }
  }
  return <form className="grid gap-5" onSubmit={handleSubmit(submit)} noValidate>{isRegister ? <Input label="Nome" autoComplete="name" error={errors.name?.message} {...register("name")} /> : null}<Input label="E-mail" type="email" autoComplete="email" error={errors.email?.message} {...register("email")} /><Input label="Senha" type="password" autoComplete={isRegister ? "new-password" : "current-password"} error={errors.password?.message} {...register("password")} />{serverError ? <p role="alert" className="rounded-xl bg-danger/10 p-3 text-sm text-danger">{serverError}</p> : null}<Button type="submit" disabled={isSubmitting}>{isSubmitting ? "Aguarde..." : isRegister ? "Criar conta" : "Entrar"}</Button><p className="text-center text-sm text-muted">{isRegister ? "Já possui uma conta? " : "Ainda não possui conta? "}<Link className="font-semibold text-primary hover:underline" href={isRegister ? "/login" : "/cadastro"}>{isRegister ? "Entrar" : "Cadastre-se"}</Link></p>{!isRegister ? <Link href="/recuperar-senha" className="text-center text-sm text-muted hover:text-foreground">Esqueci minha senha</Link> : null}</form>;
}
