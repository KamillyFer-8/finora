"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { financeApi } from "./api";

const now = new Date();
const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().slice(0, 10);
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function BudgetManager() {
  const client = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ category_id: "", period_start: monthStart, period_end: monthEnd, limit_amount: "" });
  const budgets = useQuery({ queryKey: ["budgets"], queryFn: financeApi.budgets });
  const alerts = useQuery({ queryKey: ["alerts"], queryFn: financeApi.alerts });
  const categories = useQuery({ queryKey: ["categories"], queryFn: financeApi.categories });
  const refresh = () => { client.invalidateQueries({ queryKey: ["budgets"] }); client.invalidateQueries({ queryKey: ["alerts"] }); };
  const create = useMutation({ mutationFn: financeApi.createBudget, onSuccess: () => { refresh(); setOpen(false); } });
  const remove = useMutation({ mutationFn: financeApi.deleteBudget, onSuccess: refresh });
  function submit(event: React.FormEvent) { event.preventDefault(); create.mutate({ ...form, limit_amount: Number(form.limit_amount) }); }
  return <><header className="flex flex-wrap items-end justify-between gap-5"><div><p className="text-sm text-primary">Planejamento</p><h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold">Orçamentos</h1><p className="mt-2 text-muted">Defina limites antes que os gastos decidam por você.</p></div><Button onClick={() => setOpen((value) => !value)}><Plus className="size-4" />Novo orçamento</Button></header>{alerts.data?.length ? <div className="mt-8 grid gap-3">{alerts.data.map((alert) => <div key={alert.id} className={`flex items-center gap-3 rounded-xl border p-4 text-sm ${alert.level === "danger" ? "border-danger/20 bg-danger/10 text-danger" : "border-warning/20 bg-warning/10 text-warning"}`}><AlertTriangle className="size-4" />{alert.message}</div>)}</div> : null}{open ? <Card className="mt-8 p-6"><form onSubmit={submit} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><label className="grid gap-2 text-sm font-medium">Categoria<select required className="min-h-12 rounded-xl border border-white/10 bg-[#16191f] px-4" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}><option value="">Selecione</option>{categories.data?.filter((item) => item.type === "expense").map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><Input label="Início" type="date" required value={form.period_start} onChange={(e) => setForm({ ...form, period_start: e.target.value })} /><Input label="Fim" type="date" required value={form.period_end} onChange={(e) => setForm({ ...form, period_end: e.target.value })} /><Input label="Limite" type="number" min="0.01" step="0.01" required value={form.limit_amount} onChange={(e) => setForm({ ...form, limit_amount: e.target.value })} /><Button type="submit" disabled={create.isPending}>Salvar orçamento</Button></form></Card> : null}{create.isError ? <p role="alert" className="mt-4 rounded-xl bg-danger/10 p-4 text-sm text-danger">Já existe um orçamento para esta categoria e período ou os dados são inválidos.</p> : null}{budgets.isLoading ? <div className="mt-8 grid gap-4 md:grid-cols-2"><div className="h-52 animate-pulse rounded-card bg-white/5" /><div className="h-52 animate-pulse rounded-card bg-white/5" /></div> : budgets.data?.length ? <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{budgets.data.map((item) => { const color = item.alert_level === "exceeded" ? "#FF5D6C" : item.alert_level === "warning" ? "#FFB547" : "#B7FF2A"; return <Card key={item.id} className="p-6"><div className="flex items-start justify-between"><div><span className="block size-2.5 rounded-full" style={{ backgroundColor: item.category_color }} /><h2 className="mt-3 text-lg font-semibold">{item.category_name}</h2></div><button aria-label={`Excluir orçamento de ${item.category_name}`} onClick={() => remove.mutate(item.id)} className="text-muted hover:text-danger"><Trash2 className="size-4" /></button></div><p className="mt-8 font-[family-name:var(--font-display)] text-2xl font-semibold">{money.format(Number(item.spent_amount))} <span className="text-base font-normal text-muted">/ {money.format(Number(item.limit_amount))}</span></p><div className="mt-5 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, item.percentage)}%`, backgroundColor: color }} /></div><div className="mt-3 flex justify-between text-xs text-muted"><span>{item.percentage.toFixed(0)}% utilizado</span><span>{money.format(Number(item.remaining_amount))} restante</span></div></Card>; })}</div> : <Card className="mt-8 p-10 text-center text-muted">Nenhum orçamento cadastrado.</Card>}</>;
}
