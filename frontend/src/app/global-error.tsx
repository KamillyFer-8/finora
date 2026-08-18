"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { if (process.env.NODE_ENV === "development") console.error(error); }, [error]);
  return <html lang="pt-BR"><body className="grid min-h-screen place-items-center bg-[#090A0D] p-6 text-[#F5F7FA]"><main className="max-w-md text-center"><p className="text-sm text-[#B7FF2A]">FINORA</p><h1 className="mt-3 text-3xl font-semibold">Algo saiu do fluxo.</h1><p className="mt-3 text-[#9BA1AA]">Não foi possível concluir a operação. Tente novamente sem perder o contexto.</p><div className="mt-7"><Button onClick={reset}>Tentar novamente</Button></div></main></body></html>;
}
