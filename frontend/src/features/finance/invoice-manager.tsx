"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, CheckCircle2, ChevronDown } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { financeApi } from "./api";

const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const labels = { open: "Aberta", closed: "Fechada", paid: "Paga", overdue: "Atrasada" };
const colors = { open: "text-info bg-info/10", closed: "text-warning bg-warning/10", paid: "text-primary bg-primary/10", overdue: "text-danger bg-danger/10" };

export function InvoiceManager() {
  const client = useQueryClient();
  const [accountId, setAccountId] = useState("");
  const invoices = useQuery({ queryKey: ["invoices"], queryFn: financeApi.invoices });
  const accounts = useQuery({ queryKey: ["accounts"], queryFn: financeApi.accounts });
  const refresh = () => { client.invalidateQueries({ queryKey: ["invoices"] }); client.invalidateQueries({ queryKey: ["cards"] }); client.invalidateQueries({ queryKey: ["accounts"] }); };
  const close = useMutation({ mutationFn: financeApi.closeInvoice, onSuccess: refresh });
  const pay = useMutation({ mutationFn: financeApi.payInvoice, onSuccess: refresh });
  return <><header><p className="text-sm text-primary">Compromissos</p><h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold">Faturas</h1><p className="mt-2 text-muted">Parcelas, vencimentos e pagamentos em um só histórico.</p></header><Card className="mt-8 p-4"><label className="grid gap-2 text-sm font-medium sm:max-w-sm">Conta para pagamento<select className="min-h-12 rounded-xl border border-white/10 bg-[#16191f] px-4" value={accountId} onChange={(e) => setAccountId(e.target.value)}><option value="">Selecione antes de pagar</option>{accounts.data?.map((item) => <option key={item.id} value={item.id}>{item.name} · {money.format(Number(item.balance))}</option>)}</select></label></Card>{invoices.isLoading ? <div className="mt-5 h-72 animate-pulse rounded-card bg-white/5" /> : invoices.data?.length ? <div className="mt-5 grid gap-4">{invoices.data.map((invoice) => <Card key={invoice.id} className="overflow-hidden"><div className="grid gap-5 p-6 md:grid-cols-[1fr_auto_auto] md:items-center"><div><div className="flex flex-wrap items-center gap-3"><h2 className="text-lg font-semibold">{invoice.card_name}</h2><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${colors[invoice.status]}`}>{labels[invoice.status]}</span></div><p className="mt-2 flex items-center gap-2 text-sm text-muted"><CalendarDays className="size-4" />Vence em {new Date(`${invoice.due_date}T12:00:00`).toLocaleDateString("pt-BR")}</p></div><strong className="font-[family-name:var(--font-display)] text-2xl">{money.format(Number(invoice.total))}</strong><div className="flex gap-2">{invoice.status === "open" ? <Button variant="secondary" onClick={() => close.mutate(invoice.id)}>Fechar</Button> : null}{invoice.status !== "paid" ? <Button disabled={!accountId || pay.isPending} onClick={() => pay.mutate({ id: invoice.id, accountId })}><CheckCircle2 className="size-4" />Pagar</Button> : null}</div></div><details className="border-t border-white/10"><summary className="flex cursor-pointer list-none items-center justify-between px-6 py-4 text-sm text-muted">Ver {invoice.installments.length} compras <ChevronDown className="size-4" /></summary><div className="divide-y divide-white/10 border-t border-white/10">{invoice.installments.map((item) => <div key={item.id} className="flex items-center justify-between gap-4 px-6 py-4 text-sm"><div><p>{item.description}</p><p className="mt-1 text-xs text-muted">Parcela {item.number}/{item.installment_count}</p></div><b>{money.format(Number(item.amount))}</b></div>)}</div></details></Card>)}</div> : <Card className="mt-5 p-10 text-center text-muted">Nenhuma fatura gerada.</Card>}{pay.isError ? <p role="alert" className="mt-4 rounded-xl bg-danger/10 p-4 text-sm text-danger">Pagamento não realizado. Verifique o saldo da conta.</p> : null}</>;
}
