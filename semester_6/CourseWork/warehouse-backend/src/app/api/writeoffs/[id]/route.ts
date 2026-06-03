import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { prisma } from "@/lib/prisma";

type WriteOffRouteContext = {
  params: Promise<{ id: string }>;
};

export async function GET(request: NextRequest, context: WriteOffRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  const writeOff = await prisma.writeOff.findUnique({
    where: { id },
    include: {
      lines: {
        include: {
          product: true,
        },
      },
    },
  });

  if (!writeOff) {
    return NextResponse.json({ message: "Write-off not found." }, { status: 404 });
  }

  return NextResponse.json(writeOff);
}
