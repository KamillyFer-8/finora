import { forwardRef, type InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string };

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input({ label, error, id, className = "", ...props }, ref) {
  const inputId = id ?? props.name;
  return <label htmlFor={inputId} className="grid gap-2 text-sm font-medium">{label}<input ref={ref} id={inputId} aria-invalid={Boolean(error)} aria-describedby={error ? `${inputId}-error` : undefined} className={`min-h-12 rounded-xl border border-white/10 bg-white/[0.04] px-4 text-foreground outline-none transition placeholder:text-muted/60 focus:border-primary/50 focus:ring-2 focus:ring-primary/10 ${className}`} {...props} />{error ? <span id={`${inputId}-error`} className="text-xs text-danger">{error}</span> : null}</label>;
});
