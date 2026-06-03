import { compare } from "bcryptjs";
import { NextRequest, NextResponse } from "next/server";

import { createAccessToken, createRefreshToken, hashToken } from "@/lib/auth";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";

type LoginBody = {
  email?: string;
  password?: string;
};

export async function POST(request: NextRequest) {
  const parsedBody = await parseJsonObjectBody<LoginBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  const body = parsedBody;

  if (!body.email || !body.password) {
    return NextResponse.json({ message: "Email and password are required." }, { status: 400 });
  }

  const user = await prisma.user.findUnique({ where: { email: body.email } });

  if (!user) {
    return NextResponse.json({ message: "Invalid credentials." }, { status: 401 });
  }

  const passwordMatches = await compare(body.password, user.passwordHash);

  if (!passwordMatches) {
    return NextResponse.json({ message: "Invalid credentials." }, { status: 401 });
  }

  const accessToken = createAccessToken({
    sub: user.id,
    role: user.role,
    email: user.email,
  });
  const refreshToken = createRefreshToken({ sub: user.id });

  await prisma.refreshToken.create({
    data: {
      tokenHash: hashToken(refreshToken),
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    },
  });

  return NextResponse.json({
    accessToken,
    refreshToken,
    user: {
      id: user.id,
      email: user.email,
      role: user.role,
    },
  });
}
