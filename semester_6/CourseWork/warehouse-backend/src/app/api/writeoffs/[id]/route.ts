import { Prisma } from "@prisma/client";
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

export async function DELETE(request: NextRequest, context: WriteOffRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  try {
    await prisma.$transaction(async (tx) => {
      await tx.inventoryTransaction.deleteMany({ where: { sourceDocument: `writeoff:${id}` } });
      await tx.writeOff.delete({ where: { id } });
    });

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "Write-off not found." }, { status: 404 });
    }

    throw error;
  }
}
