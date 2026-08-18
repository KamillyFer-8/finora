import { forwardRef, type SelectHTMLAttributes } from "react";
type Props = SelectHTMLAttributes<HTMLSelectElement> & { label?: string; error?: string };
export const Select = forwardRef<HTMLSelectElement, Props>(function Select({ label, error, className = "", children, ...props }, ref) { return <label className="grid gap-2 text-sm font-medium">{label}<select ref={ref} className={`min-h-12 rounded-xl border border-white/10 bg-[#16191f] px-4 text-sm ${className}`} {...props}>{children}</select>{error ? <span role="alert" className="text-xs text-danger">{error}</span> : null}</label>; });
