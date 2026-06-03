import { NextRequest, NextResponse } from "next/server";

import { hashToken } from "@/lib/auth";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";

type LogoutBody = {
  refreshToken?: string;
};

export async function POST(request: NextRequest) {
  const parsedBody = await parseJsonObjectBody<LogoutBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  const body = parsedBody;

  if (!body.refreshToken) {
    return NextResponse.json({ message: "Refresh token is required." }, { status: 400 });
  }

  await prisma.refreshToken.deleteMany({
    where: {
      tokenHash: hashToken(body.refreshToken),
    },
  });

  return NextResponse.json({ message: "Logged out successfully." });
}
