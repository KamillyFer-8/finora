import Link from "next/link";
import type { ReactNode } from "react";
import { Card } from "@/components/ui/card";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return <main className="grid min-h-screen place-items-center px-6 py-12"><div className="w-full max-w-md"><Link href="/" className="mb-8 flex items-center justify-center gap-3"><span className="grid size-10 place-items-center rounded-xl bg-primary font-black text-[#172000]">F</span><span className="font-[family-name:var(--font-display)] text-xl font-bold">FINORA</span></Link><Card className="p-7 sm:p-9">{children}</Card></div></main>;
}
