import { NextRequest, NextResponse } from "next/server";

import { createAccessToken, createRefreshToken, hashToken, verifyRefreshToken } from "@/lib/auth";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";

type RefreshBody = {
  refreshToken?: string;
};

export async function POST(request: NextRequest) {
  const parsedBody = await parseJsonObjectBody<RefreshBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  const body = parsedBody;

  if (!body.refreshToken) {
    return NextResponse.json({ message: "Refresh token is required." }, { status: 400 });
  }

  try {
    const payload = verifyRefreshToken(body.refreshToken);
    const tokenHash = hashToken(body.refreshToken);
    const nextRefreshToken = createRefreshToken({ sub: payload.sub });
    const user = await prisma.$transaction(async (tx) => {
      const storedToken = await tx.refreshToken.findUnique({ where: { tokenHash } });

      if (!storedToken || storedToken.expiresAt < new Date()) {
        return null;
      }

      const deleted = await tx.refreshToken.deleteMany({
        where: {
          tokenHash,
          expiresAt: {
            gt: new Date(),
          },
        },
      });

      if (deleted.count !== 1) {
        return null;
      }

      const foundUser = await tx.user.findUnique({ where: { id: payload.sub } });

      if (!foundUser) {
        return null;
      }

      await tx.refreshToken.create({
        data: {
          tokenHash: hashToken(nextRefreshToken),
          userId: foundUser.id,
          expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        },
      });

      return foundUser;
    });

    if (!user) {
      return NextResponse.json({ message: "Refresh token is invalid." }, { status: 401 });
    }

    const accessToken = createAccessToken({
      sub: user.id,
      role: user.role,
      email: user.email,
    });

    return NextResponse.json({ accessToken, refreshToken: nextRefreshToken });
  } catch {
    return NextResponse.json({ message: "Refresh token is invalid." }, { status: 401 });
  }
}
