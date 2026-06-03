import { UserRole } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { verifyAccessToken } from "@/lib/auth";

export const OPERATOR_ROLES: UserRole[] = ["ADMIN", "MANAGER"];

function readBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return null;
  }

  return authHeader.slice("Bearer ".length);
}

export function requireRole(request: NextRequest, allowedRoles: UserRole[]): NextResponse | null {
  const token = readBearerToken(request);

  if (!token) {
    return NextResponse.json({ message: "Unauthorized." }, { status: 401 });
  }

  try {
    const payload = verifyAccessToken(token);

    if (!allowedRoles.includes(payload.role)) {
      return NextResponse.json({ message: "Forbidden." }, { status: 403 });
    }

    return null;
  } catch {
    return NextResponse.json({ message: "Unauthorized." }, { status: 401 });
  }
}
