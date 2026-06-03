import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseOptionalDate } from "@/lib/date";
import { prisma } from "@/lib/prisma";
import { parseOptionalLimit } from "@/lib/query";

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  try {
    const from = parseOptionalDate(request.nextUrl.searchParams.get("from"), "from");
    const to = parseOptionalDate(request.nextUrl.searchParams.get("to"), "to");
    const productId = request.nextUrl.searchParams.get("productId");
    const limit = parseOptionalLimit(request.nextUrl.searchParams.get("limit"));

    const movements = await prisma.inventoryTransaction.findMany({
      where: {
        productId: productId ?? undefined,
        createdAt: {
          gte: from ?? undefined,
          lte: to ?? undefined,
        },
      },
      include: {
        product: {
          select: {
            id: true,
            sku: true,
            name: true,
            unit: true,
          },
        },
      },
      orderBy: { createdAt: "desc" },
      take: limit,
    });

    return NextResponse.json({
      items: movements.map((movement) => ({
        id: movement.id,
        product: movement.product,
        type: movement.type,
        quantity: movement.quantity.toString(),
        unitCost: movement.unitCost?.toString() ?? null,
        sourceDocument: movement.sourceDocument,
        createdAt: movement.createdAt,
      })),
    });
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Invalid '")) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
