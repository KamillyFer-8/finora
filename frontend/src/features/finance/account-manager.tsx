"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, WalletCards } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { financeApi } from "./api";

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function AccountManager() {
  const client = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", institution: "", type: "checking", balance: "0" });
  const accounts = useQuery({ queryKey: ["accounts"], queryFn: financeApi.accounts });
  const create = useMutation({ mutationFn: financeApi.createAccount, onSuccess: () => { client.invalidateQueries({ queryKey: ["accounts"] }); setShowForm(false); setForm({ name: "", institution: "", type: "checking", balance: "0" }); } });
  const remove = useMutation({ mutationFn: financeApi.deleteAccount, onSuccess: () => client.invalidateQueries({ queryKey: ["accounts"] }) });
  function submit(event: React.FormEvent) { event.preventDefault(); create.mutate({ ...form, balance: Number(form.balance) }); }
  return <><header className="flex flex-wrap items-end justify-between gap-5"><div><p className="text-sm text-primary">Patrimônio</p><h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold">Contas</h1><p className="mt-2 text-muted">Centralize os lugares onde seu dinheiro vive.</p></div><Button onClick={() => setShowForm((value) => !value)}><Plus className="size-4" />Nova conta</Button></header>{showForm ? <Card className="mt-8 p-6"><form onSubmit={submit} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"><Input label="Nome" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /><Input label="Instituição" required value={form.institution} onChange={(e) => setForm({ ...form, institution: e.target.value })} /><label className="grid gap-2 text-sm font-medium">Tipo<select className="min-h-12 rounded-xl border border-white/10 bg-[#16191f] px-4" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}><option value="checking">Corrente</option><option value="savings">Poupança</option><option value="digital">Digital</option><option value="cash">Dinheiro</option><option value="investment">Investimento</option></select></label><Input label="Saldo inicial" type="number" step="0.01" value={form.balance} onChange={(e) => setForm({ ...form, balance: e.target.value })} /><div className="md:col-span-2 lg:col-span-4"><Button type="submit" disabled={create.isPending}>{create.isPending ? "Salvando..." : "Salvar conta"}</Button></div></form></Card> : null}{accounts.isLoading ? <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{[1,2,3].map((item) => <div key={item} className="h-48 animate-pulse rounded-card bg-white/5" />)}</div> : accounts.isError ? <Card className="mt-8 p-6 text-danger">Não foi possível carregar suas contas.</Card> : accounts.data?.length ? <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{accounts.data.map((account) => <Card key={account.id} className="p-6"><div className="flex justify-between"><span className="grid size-10 place-items-center rounded-xl bg-primary/10 text-primary"><WalletCards className="size-5" /></span><button aria-label={`Excluir ${account.name}`} onClick={() => remove.mutate(account.id)} className="text-muted hover:text-danger"><Trash2 className="size-4" /></button></div><p className="mt-8 text-sm text-muted">{account.institution}</p><h2 className="mt-1 text-lg font-semibold">{account.name}</h2><p className="mt-5 font-[family-name:var(--font-display)] text-3xl font-semibold">{money.format(Number(account.balance))}</p></Card>)}</div> : <Card className="mt-8 p-10 text-center text-muted">Nenhuma conta cadastrada.</Card>}</>;
}
