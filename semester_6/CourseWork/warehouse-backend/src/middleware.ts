import { NextRequest, NextResponse } from "next/server";

const allowedOrigins = new Set(["http://localhost:3000"]);
const corsHeaders = {
  "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "content-type, authorization",
  "Access-Control-Max-Age": "86400",
};

export function middleware(request: NextRequest) {
  const origin = request.headers.get("origin");
  const headers = new Headers(corsHeaders);

  if (origin && allowedOrigins.has(origin)) {
    headers.set("Access-Control-Allow-Origin", origin);
  }

  if (request.method === "OPTIONS") {
    return new NextResponse(null, { status: 204, headers });
  }

  const response = NextResponse.next();
  for (const [key, value] of headers.entries()) {
    response.headers.set(key, value);
  }

  return response;
}

export const config = {
  matcher: "/api/:path*",
};
