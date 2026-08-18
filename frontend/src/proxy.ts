import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  if (!request.cookies.has("access_token")) return NextResponse.redirect(new URL("/login", request.url));
  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*", "/contas/:path*", "/transacoes/:path*", "/cartoes/:path*", "/faturas/:path*", "/orcamentos/:path*", "/metas/:path*", "/relatorios/:path*", "/anexos/:path*"] };
