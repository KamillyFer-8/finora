import { ArrowUpRight, BadgeCheck, Layers3, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const foundations = [
  { icon: Layers3, title: "Arquitetura modular", text: "Frontend e API independentes, unidos por contratos REST versionados." },
  { icon: ShieldCheck, title: "Segurança por desenho", text: "Regras críticas e isolamento de dados permanecem no backend." },
  { icon: BadgeCheck, title: "Qualidade contínua", text: "Lint, tipos, testes e build executados automaticamente no CI." },
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8 sm:px-10 lg:px-16">
      <nav className="flex items-center justify-between" aria-label="Navegação principal">
        <a href="#inicio" className="flex items-center gap-3 rounded-lg focus-visible:outline-2 focus-visible:outline-primary">
          <span className="grid size-10 place-items-center rounded-xl bg-primary text-lg font-black text-[#172000]">F</span>
          <span className="font-[family-name:var(--font-display)] text-lg font-bold tracking-[-0.04em]">FINORA</span>
        </a>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-muted">Sprint 7 · Produção</span>
      </nav>

      <section id="inicio" className="grid flex-1 items-center gap-14 py-20 lg:grid-cols-[1.08fr_0.92fr]">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-2 text-sm text-primary">
            <Sparkles aria-hidden="true" className="size-4" /> Sua vida financeira, finalmente legível.
          </div>
          <h1 className="max-w-3xl font-[family-name:var(--font-display)] text-5xl font-semibold leading-[1.02] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
            Decisões melhores começam com <span className="text-primary">clareza.</span>
          </h1>
          <p className="mt-7 max-w-xl text-base leading-7 text-muted sm:text-lg">
            A fundação técnica do Finora está pronta para transformar contas, compromissos e metas em uma visão financeira coesa.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Button asChild><a href="/login">Entrar no Finora <ArrowUpRight aria-hidden="true" className="size-4" /></a></Button>
            <Button variant="secondary" asChild><a href="http://localhost:8000/docs">Documentação da API</a></Button>
          </div>
        </div>

        <Card className="relative overflow-hidden p-7 sm:p-9">
          <div className="absolute -right-20 -top-24 size-64 rounded-full bg-primary/10 blur-3xl" />
          <div className="relative">
            <div className="flex items-start justify-between">
              <div><p className="text-sm text-muted">Saldo consolidado</p><p className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight">R$ 24.680,40</p></div>
              <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">+8,4%</span>
            </div>
            <div className="mt-12 flex h-36 items-end gap-2" aria-hidden="true">
              {[38, 52, 45, 70, 58, 84, 74, 96, 80, 108, 92, 122].map((height, index) => (
                <span key={height} className={`flex-1 rounded-t-sm ${index > 8 ? "bg-primary" : "bg-white/10"}`} style={{ height }} />
              ))}
            </div>
            <div className="mt-6 flex justify-between border-t border-white/10 pt-5 text-sm"><span className="text-muted">Visão demonstrativa</span><span>Design system v0.1</span></div>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 pb-12 md:grid-cols-3" aria-label="Pilares da fundação">
        {foundations.map(({ icon: Icon, title, text }) => (
          <Card key={title} className="p-6">
            <Icon aria-hidden="true" className="size-5 text-primary" />
            <h2 className="mt-8 font-[family-name:var(--font-display)] text-lg font-semibold">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-muted">{text}</p>
          </Card>
        ))}
      </section>
    </main>
  );
}
