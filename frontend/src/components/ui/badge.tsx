import type { ReactNode } from "react";
export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "danger" }) { return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${tone === "success" ? "bg-primary/15 text-primary" : tone === "danger" ? "bg-danger/15 text-danger" : "bg-white/10 text-muted"}`}>{children}</span>; }
