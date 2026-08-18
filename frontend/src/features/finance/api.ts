import { apiClient } from "@/lib/api/client";
import type { Account, Attachment, Budget, Card, Category, DashboardReport, Goal, Invoice, PlanningAlert, Recurrence, Transaction, TransactionPage } from "./types";

export const financeApi = {
  accounts: () => apiClient.get<Account[]>("/accounts").then(({ data }) => data),
  createAccount: (payload: object) => apiClient.post<Account>("/accounts", payload).then(({ data }) => data),
  deleteAccount: (id: string) => apiClient.delete(`/accounts/${id}`),
  categories: () => apiClient.get<Category[]>("/categories").then(({ data }) => data),
  createCategory: (payload: object) => apiClient.post<Category>("/categories", payload).then(({ data }) => data),
  transactions: (params: URLSearchParams) => apiClient.get<TransactionPage>(`/transactions?${params}`).then(({ data }) => data),
  createTransaction: (payload: object) => apiClient.post<Transaction>("/transactions", payload).then(({ data }) => data),
  updateTransaction: ({ id, payload }: { id: string; payload: object }) => apiClient.patch<Transaction>(`/transactions/${id}`, payload).then(({ data }) => data),
  deleteTransaction: (id: string) => apiClient.delete(`/transactions/${id}`),
  duplicateTransaction: (id: string) => apiClient.post<Transaction>(`/transactions/${id}/duplicate`).then(({ data }) => data),
  recurrences: () => apiClient.get<Recurrence[]>("/recurrences").then(({ data }) => data),
  createRecurrence: (payload: object) => apiClient.post<Recurrence>("/recurrences", payload).then(({ data }) => data),
  deleteRecurrence: (id: string) => apiClient.delete(`/recurrences/${id}`),
  cards: () => apiClient.get<Card[]>("/cards").then(({ data }) => data),
  createCard: (payload: object) => apiClient.post<Card>("/cards", payload).then(({ data }) => data),
  createPurchase: ({ cardId, payload }: { cardId: string; payload: object }) => apiClient.post(`/cards/${cardId}/purchases`, payload),
  invoices: () => apiClient.get<Invoice[]>("/invoices").then(({ data }) => data),
  closeInvoice: (id: string) => apiClient.post<Invoice>(`/invoices/${id}/close`).then(({ data }) => data),
  payInvoice: ({ id, accountId }: { id: string; accountId: string }) => apiClient.post<Invoice>(`/invoices/${id}/pay`, { account_id: accountId }).then(({ data }) => data),
  budgets: () => apiClient.get<Budget[]>("/budgets").then(({ data }) => data),
  createBudget: (payload: object) => apiClient.post<Budget>("/budgets", payload).then(({ data }) => data),
  deleteBudget: (id: string) => apiClient.delete(`/budgets/${id}`),
  alerts: () => apiClient.get<PlanningAlert[]>("/alerts").then(({ data }) => data),
  goals: () => apiClient.get<Goal[]>("/goals").then(({ data }) => data),
  createGoal: (payload: object) => apiClient.post<Goal>("/goals", payload).then(({ data }) => data),
  deleteGoal: (id: string) => apiClient.delete(`/goals/${id}`),
  contribute: ({ goalId, payload }: { goalId: string; payload: object }) => apiClient.post(`/goals/${goalId}/contributions`, payload),
  deleteContribution: (id: string) => apiClient.delete(`/goals/contributions/${id}`),
  report: (params: URLSearchParams) => apiClient.get<DashboardReport>(`/reports/dashboard?${params}`).then(({ data }) => data),
  exportReport: (params: URLSearchParams) => apiClient.get(`/reports/export.csv?${params}`, { responseType: "blob" }),
  attachments: () => apiClient.get<Attachment[]>("/attachments").then(({ data }) => data),
  uploadAttachment: (payload: FormData) => apiClient.post<Attachment>("/attachments", payload).then(({ data }) => data),
  deleteAttachment: (id: string) => apiClient.delete(`/attachments/${id}`),
};

export function attachmentUrl(path: string) {
  return new URL(path, apiClient.defaults.baseURL).toString();
}
