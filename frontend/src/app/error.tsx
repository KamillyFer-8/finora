"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { if (process.env.NODE_ENV === "development") console.error(error); }, [error]);
  return <Card className="mx-auto max-w-lg p-8 text-center"><h2 className="text-2xl font-semibold">Não foi possível carregar esta área.</h2><p className="mt-3 text-muted">Tente novamente. Se o problema continuar, volte à tela anterior.</p><div className="mt-6"><Button onClick={reset}>Tentar novamente</Button></div></Card>;
}
