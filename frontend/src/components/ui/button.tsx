import { cloneElement, isValidElement, type ButtonHTMLAttributes, type ReactElement, type ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
  asChild?: boolean;
  children: ReactNode;
};

const styles = "inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-5 text-sm font-semibold transition duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:pointer-events-none disabled:opacity-50";

export function Button({ variant = "primary", asChild, className = "", children, ...props }: ButtonProps) {
  const variants = variant === "primary" ? "bg-primary text-[#172000] hover:bg-[#c6ff56]" : "border border-white/10 bg-white/5 text-foreground hover:bg-white/10";
  const composed = `${styles} ${variants} ${className}`;
  if (asChild && isValidElement(children)) {
    return cloneElement(children as ReactElement<{ className?: string }>, { className: composed });
  }
  return <button className={composed} {...props}>{children}</button>;
}
