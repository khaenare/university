import { NextRequest, NextResponse } from "next/server";

import { verifyAccessToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

function readBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return null;
  }

  return authHeader.slice("Bearer ".length);
}

export async function GET(request: NextRequest) {
  const token = readBearerToken(request);

  if (!token) {
    return NextResponse.json({ message: "Unauthorized." }, { status: 401 });
  }

  try {
    const payload = verifyAccessToken(token);
    const user = await prisma.user.findUnique({ where: { id: payload.sub } });

    if (!user) {
      return NextResponse.json({ message: "User not found." }, { status: 404 });
    }

    return NextResponse.json({
      id: user.id,
      email: user.email,
      role: user.role,
      createdAt: user.createdAt,
    });
  } catch {
    return NextResponse.json({ message: "Unauthorized." }, { status: 401 });
  }
}
