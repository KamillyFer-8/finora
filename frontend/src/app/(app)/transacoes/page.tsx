import { TransactionManager } from "@/features/finance/transaction-manager";

export default async function TransactionsPage({ searchParams }: { searchParams: Promise<{ search?: string }> }) { const { search } = await searchParams; return <TransactionManager initialSearch={search} />; }
