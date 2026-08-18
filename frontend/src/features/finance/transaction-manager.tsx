"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, Edit3, Plus, RotateCw, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { financeApi } from "./api";
import type { Transaction } from "./types";

const schema = z.object({
  description: z.string().min(2, "Informe uma descrição"), amount: z.string().refine((value) => Number(value) > 0, "Informe um valor positivo"),
  type: z.enum(["income", "expense"]), account_id: z.string().min(1, "Selecione uma conta"), category_id: z.string().optional(), date: z.string().min(1),
  status: z.enum(["pending", "completed", "cancelled"]), notes: z.string().optional(), card_id: z.string().optional(), installments: z.string().optional(),
  recurrence: z.enum(["none", "weekly", "monthly", "yearly"]), recurrence_end: z.string().optional(),
});
type Fields = z.infer<typeof schema>;
const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const controlClass = "min-h-12 rounded-xl border border-white/10 bg-[#16191f] px-4 text-sm";
const defaults: Partial<Fields> = { type: "expense", status: "completed", date: new Date().toISOString().slice(0, 10), recurrence: "none", installments: "1" };

export function TransactionManager({ initialSearch = "" }: { initialSearch?: string }) {
  const client = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Transaction | null>(null);
  const [receipt, setReceipt] = useState<File | null>(null);
  const [filters, setFilters] = useState({ search: initialSearch, type: "", status: "", account_id: "", category_id: "", start_date: "", end_date: "", sort: "date_desc" });
  const [page, setPage] = useState(1);
  const params = useMemo(() => { const value = new URLSearchParams({ page: String(page), page_size: "10" }); Object.entries(filters).forEach(([key, item]) => { if (item) value.set(key, item); }); return value; }, [filters, page]);
  const accounts = useQuery({ queryKey: ["accounts"], queryFn: financeApi.accounts });
  const categories = useQuery({ queryKey: ["categories"], queryFn: financeApi.categories });
  const cards = useQuery({ queryKey: ["cards"], queryFn: financeApi.cards });
  const transactions = useQuery({ queryKey: ["transactions", params.toString()], queryFn: () => financeApi.transactions(params) });
  const recurrences = useQuery({ queryKey: ["recurrences"], queryFn: financeApi.recurrences });
  const { register, handleSubmit, reset, control, formState: { errors } } = useForm<Fields>({ resolver: zodResolver(schema), defaultValues: defaults });
  const selectedType = useWatch({ control, name: "type" });
  const selectedCard = useWatch({ control, name: "card_id" });
  const recurrence = useWatch({ control, name: "recurrence" });
  const invalidate = () => { void client.invalidateQueries({ queryKey: ["transactions"] }); void client.invalidateQueries({ queryKey: ["accounts"] }); void client.invalidateQueries({ queryKey: ["recurrences"] }); void client.invalidateQueries({ queryKey: ["cards"] }); void client.invalidateQueries({ queryKey: ["invoices"] }); };
  const uploadReceipt = async (transactionId: string | null) => { if (!receipt) return; const data = new FormData(); data.append("file", receipt); if (transactionId) data.append("transaction_id", transactionId); await financeApi.uploadAttachment(data); };
  const save = useMutation({ mutationFn: async (fields: Fields) => {
    if (selectedCard && !editing) { await financeApi.createPurchase({ cardId: selectedCard, payload: { description: fields.description, total_amount: Number(fields.amount), installment_count: Number(fields.installments || 1), purchase_date: fields.date } }); await uploadReceipt(null); return; }
    const payload = { description: fields.description, amount: Number(fields.amount), type: fields.type, account_id: fields.account_id, category_id: fields.category_id || null, date: fields.date, status: fields.status, notes: fields.notes || null };
    const transaction = editing ? await financeApi.updateTransaction({ id: editing.id, payload }) : await financeApi.createTransaction(payload);
    await uploadReceipt(transaction.id);
    if (!editing && fields.recurrence !== "none") await financeApi.createRecurrence({ ...payload, frequency: fields.recurrence, interval: 1, next_run_at: fields.date, end_date: fields.recurrence_end || null });
  }, onSuccess: () => { invalidate(); setShowForm(false); setEditing(null); setReceipt(null); reset(defaults); } });
  const remove = useMutation({ mutationFn: financeApi.deleteTransaction, onSuccess: invalidate });
  const duplicate = useMutation({ mutationFn: financeApi.duplicateTransaction, onSuccess: invalidate });
  const removeRecurrence = useMutation({ mutationFn: financeApi.deleteRecurrence, onSuccess: invalidate });
  const changeFilter = (name: keyof typeof filters, value: string) => { setFilters((current) => ({ ...current, [name]: value })); setPage(1); };
  const startEdit = (item: Transaction) => { setEditing(item); setShowForm(true); reset({ ...defaults, ...item, amount: String(item.amount), category_id: item.category_id ?? "", notes: item.notes ?? "" }); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const closeForm = () => { setShowForm(false); setEditing(null); setReceipt(null); reset(defaults); };

  return <>
    <header className="flex flex-wrap items-end justify-between gap-5"><div><p className="text-sm text-primary">Movimentações</p><h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold">Transações</h1><p className="mt-2 text-muted">Acompanhe entradas, saídas e recorrências em um só lugar.</p></div><Button onClick={() => { if (showForm) closeForm(); else setShowForm(true); }}><Plus className="size-4" />{showForm ? "Fechar" : "Nova transação"}</Button></header>
    {showForm ? <Card className="mt-8 p-6"><form onSubmit={handleSubmit((fields) => save.mutate(fields))} className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <Input label="Descrição" error={errors.description?.message} {...register("description")} /><Input label="Valor" type="number" step="0.01" error={errors.amount?.message} {...register("amount")} />
      <label className="grid gap-2 text-sm font-medium">Tipo<select className={controlClass} {...register("type")}><option value="expense">Despesa</option><option value="income">Receita</option></select></label>
      <label className="grid gap-2 text-sm font-medium">Conta<select className={controlClass} {...register("account_id")}><option value="">Selecione</option>{accounts.data?.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select>{errors.account_id ? <span className="text-xs text-danger">{errors.account_id.message}</span> : null}</label>
      <label className="grid gap-2 text-sm font-medium">Categoria<select className={controlClass} {...register("category_id")}><option value="">Sem categoria</option>{categories.data?.filter((item) => item.type === selectedType).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
      <Input label="Data" type="date" error={errors.date?.message} {...register("date")} />
      <label className="grid gap-2 text-sm font-medium">Status<select className={controlClass} {...register("status")}><option value="completed">Concluída</option><option value="pending">Pendente</option><option value="cancelled">Cancelada</option></select></label>
      {!editing && selectedType === "expense" ? <label className="grid gap-2 text-sm font-medium">Cartão (opcional)<select className={controlClass} {...register("card_id")}><option value="">Não usar cartão</option>{cards.data?.map((item) => <option key={item.id} value={item.id}>{item.name} • {item.last_four}</option>)}</select></label> : null}
      {selectedCard ? <Input label="Parcelas" type="number" min="1" max="48" {...register("installments")} /> : null}
      {!editing && !selectedCard ? <label className="grid gap-2 text-sm font-medium">Recorrência<select className={controlClass} {...register("recurrence")}><option value="none">Não repetir</option><option value="weekly">Semanal</option><option value="monthly">Mensal</option><option value="yearly">Anual</option></select></label> : null}
      {recurrence !== "none" && !editing ? <Input label="Repetir até (opcional)" type="date" {...register("recurrence_end")} /> : null}
      <label className="grid gap-2 text-sm font-medium md:col-span-2">Observações<textarea className={`${controlClass} min-h-24 py-3`} maxLength={2000} {...register("notes")} /></label>
      <label className="grid gap-2 text-sm font-medium">Comprovante (opcional)<input type="file" accept="application/pdf,image/jpeg,image/png" className={`${controlClass} py-3`} onChange={(event) => setReceipt(event.target.files?.[0] ?? null)} /></label>
      <div className="flex items-center gap-3 md:col-span-2 xl:col-span-3"><Button type="submit" disabled={save.isPending}>{save.isPending ? "Salvando..." : editing ? "Atualizar transação" : "Salvar"}</Button><Button type="button" variant="secondary" onClick={closeForm}>Cancelar</Button>{save.isError ? <span role="alert" className="text-sm text-danger">Não foi possível salvar. Revise os dados.</span> : null}</div>
    </form></Card> : null}
    <Card className="mt-8 p-4"><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4"><input aria-label="Pesquisar transações" placeholder="Pesquisar..." value={filters.search} onChange={(e) => changeFilter("search", e.target.value)} className={controlClass} /><select aria-label="Filtrar por tipo" className={controlClass} value={filters.type} onChange={(e) => changeFilter("type", e.target.value)}><option value="">Todos os tipos</option><option value="income">Receitas</option><option value="expense">Despesas</option></select><select aria-label="Filtrar por status" className={controlClass} value={filters.status} onChange={(e) => changeFilter("status", e.target.value)}><option value="">Todos os status</option><option value="completed">Concluídas</option><option value="pending">Pendentes</option><option value="cancelled">Canceladas</option></select><select aria-label="Filtrar por conta" className={controlClass} value={filters.account_id} onChange={(e) => changeFilter("account_id", e.target.value)}><option value="">Todas as contas</option>{accounts.data?.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><select aria-label="Filtrar por categoria" className={controlClass} value={filters.category_id} onChange={(e) => changeFilter("category_id", e.target.value)}><option value="">Todas as categorias</option>{categories.data?.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select><Input aria-label="Data inicial" type="date" value={filters.start_date} onChange={(e) => changeFilter("start_date", e.target.value)} /><Input aria-label="Data final" type="date" value={filters.end_date} onChange={(e) => changeFilter("end_date", e.target.value)} /><select aria-label="Ordenar transações" className={controlClass} value={filters.sort} onChange={(e) => changeFilter("sort", e.target.value)}><option value="date_desc">Mais recentes</option><option value="date_asc">Mais antigas</option><option value="amount_desc">Maior valor</option><option value="amount_asc">Menor valor</option></select></div></Card>
    {transactions.isLoading ? <div className="mt-5 h-64 animate-pulse rounded-card bg-white/5" /> : transactions.isError ? <Card className="mt-5 p-6 text-danger">Não foi possível carregar. <Button variant="secondary" onClick={() => transactions.refetch()}>Tentar novamente</Button></Card> : <Card className="mt-5 overflow-hidden"><div className="divide-y divide-white/10">{transactions.data?.items.map((item) => <article key={item.id} className="grid gap-3 p-5 sm:grid-cols-[1fr_auto_auto] sm:items-center"><div><h2 className="font-medium">{item.description}</h2><p className="mt-1 text-xs text-muted">{new Date(`${item.date}T12:00:00`).toLocaleDateString("pt-BR")} · {item.status}{item.notes ? ` · ${item.notes}` : ""}</p></div><strong className={item.type === "income" ? "text-primary" : "text-foreground"}>{item.type === "expense" ? "−" : "+"} {money.format(Number(item.amount))}</strong><div className="flex gap-3"><button aria-label={`Editar ${item.description}`} onClick={() => startEdit(item)} className="text-muted hover:text-primary"><Edit3 className="size-4" /></button><button aria-label={`Duplicar ${item.description}`} onClick={() => duplicate.mutate(item.id)} className="text-muted hover:text-primary"><Copy className="size-4" /></button><button aria-label={`Excluir ${item.description}`} onClick={() => remove.mutate(item.id)} className="text-muted hover:text-danger"><Trash2 className="size-4" /></button></div></article>)}{!transactions.data?.items.length ? <p className="p-10 text-center text-muted">Nenhuma transação encontrada.</p> : null}</div>{transactions.data && transactions.data.total > 10 ? <div className="flex items-center justify-between border-t border-white/10 p-4"><Button variant="secondary" disabled={page === 1} onClick={() => setPage((value) => value - 1)}>Anterior</Button><span className="text-sm text-muted">Página {page}</span><Button variant="secondary" disabled={page * 10 >= transactions.data.total} onClick={() => setPage((value) => value + 1)}>Próxima</Button></div> : null}</Card>}
    {recurrences.data?.length ? <section className="mt-10"><h2 className="flex items-center gap-2 text-xl font-semibold"><RotateCw className="size-5 text-primary" />Recorrências ativas</h2><div className="mt-4 grid gap-3 md:grid-cols-2">{recurrences.data.map((item) => <Card key={item.id} className="flex items-center justify-between p-5"><div><strong>{item.description}</strong><p className="mt-1 text-xs text-muted">{item.frequency === "weekly" ? "Semanal" : item.frequency === "monthly" ? "Mensal" : "Anual"} · próxima em {new Date(`${item.next_run_at}T12:00:00`).toLocaleDateString("pt-BR")}</p></div><button aria-label={`Excluir recorrência ${item.description}`} onClick={() => removeRecurrence.mutate(item.id)} className="text-muted hover:text-danger"><Trash2 className="size-4" /></button></Card>)}</div></section> : null}
  </>;
}
