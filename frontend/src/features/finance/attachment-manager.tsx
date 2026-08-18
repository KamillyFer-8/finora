"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Paperclip, Trash2, Upload } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { attachmentUrl, financeApi } from "./api";

export function AttachmentManager() {
  const client = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [transactionId, setTransactionId] = useState("");
  const attachments = useQuery({ queryKey: ["attachments"], queryFn: financeApi.attachments });
  const transactions = useQuery({
    queryKey: ["transactions", "attachments"],
    queryFn: () => financeApi.transactions(new URLSearchParams({ page_size: "100" })),
  });
  const upload = useMutation({
    mutationFn: financeApi.uploadAttachment,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["attachments"] });
      setFile(null);
    },
  });
  const remove = useMutation({
    mutationFn: financeApi.deleteAttachment,
    onSuccess: () => client.invalidateQueries({ queryKey: ["attachments"] }),
  });

  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) return;
    const data = new FormData();
    data.append("file", file);
    if (transactionId) data.append("transaction_id", transactionId);
    upload.mutate(data);
  }

  return <><header><p className="text-sm text-primary">Documentos</p><h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold">Anexos</h1><p className="mt-2 text-muted">Comprovantes, recibos e notas fiscais armazenados no ambiente local.</p></header><Card className="mt-8 p-6"><form onSubmit={submit} className="grid gap-4 md:grid-cols-[1fr_1fr_auto] md:items-end"><label className="grid gap-2 text-sm font-medium">Arquivo PDF, JPEG ou PNG<input aria-label="Selecionar arquivo" type="file" accept="application/pdf,image/jpeg,image/png" required onChange={(event) => setFile(event.target.files?.[0] ?? null)} className="min-h-12 rounded-xl border border-dashed border-white/15 bg-white/[0.03] p-3 text-sm text-muted file:mr-4 file:rounded-lg file:border-0 file:bg-primary file:px-3 file:py-1 file:font-semibold file:text-[#172000]" /></label><label className="grid gap-2 text-sm font-medium">Transação relacionada<select className="min-h-12 rounded-xl border border-white/10 bg-[#16191f] px-4" value={transactionId} onChange={(event) => setTransactionId(event.target.value)}><option value="">Sem vínculo</option>{transactions.data?.items.map((item) => <option key={item.id} value={item.id}>{item.description}</option>)}</select></label><Button type="submit" disabled={!file || upload.isPending}><Upload className="size-4" />{upload.isPending ? "Enviando..." : "Enviar"}</Button></form>{upload.isError ? <p role="alert" className="mt-4 rounded-xl bg-danger/10 p-3 text-sm text-danger">Não foi possível enviar. Confira o formato e o tamanho do arquivo.</p> : null}</Card>{attachments.isError ? <Card className="mt-5 p-8 text-center"><p className="text-danger">Não foi possível carregar os anexos.</p><Button className="mt-4" variant="secondary" onClick={() => attachments.refetch()}>Tentar novamente</Button></Card> : attachments.isLoading ? <div className="mt-5 h-48 animate-pulse rounded-card bg-white/5" /> : attachments.data?.length ? <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{attachments.data.map((item) => <Card key={item.id} className="p-5"><div className="flex items-start justify-between"><span className="grid size-10 place-items-center rounded-xl bg-primary/10 text-primary">{item.mime_type === "application/pdf" ? <FileText className="size-5" /> : <Paperclip className="size-5" />}</span><button aria-label={`Excluir ${item.original_name}`} onClick={() => remove.mutate(item.id)} className="text-muted hover:text-danger"><Trash2 className="size-4" /></button></div><a href={attachmentUrl(item.url)} target="_blank" rel="noreferrer" className="mt-6 block truncate font-medium hover:text-primary">{item.original_name}</a><p className="mt-2 text-xs text-muted">{(item.size / 1024).toFixed(1)} KB · {new Date(item.created_at).toLocaleDateString("pt-BR")}</p></Card>)}</div> : <Card className="mt-5 p-10 text-center text-muted">Nenhum anexo enviado.</Card>}</>;
}
