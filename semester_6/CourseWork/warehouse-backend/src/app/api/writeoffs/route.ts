import { Prisma, TransactionType } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { assertSufficientStock, InventoryValidationError } from "@/lib/inventory";
import { prisma } from "@/lib/prisma";
import {
  requireWriteOffLines,
  requireWriteOffReason,
  WriteOffValidationError,
} from "@/lib/writeoffs";

type CreateWriteOffBody = {
  reason?: string;
  lines?: Array<{
    productId?: string;
    quantity?: number;
  }>;
};

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const writeOffs = await prisma.writeOff.findMany({
    include: {
      lines: {
        include: {
          product: true,
        },
      },
    },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(writeOffs);
}

export async function POST(request: NextRequest) {
  const authorizationError = requireRole(request, ["ADMIN", "MANAGER"]);

  if (authorizationError) {
    return authorizationError;
  }

  const parsedBody = await parseJsonObjectBody<CreateWriteOffBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const reason = requireWriteOffReason(parsedBody.reason);
    const lines = requireWriteOffLines(parsedBody.lines);

    const writeOff = await prisma.$transaction(
      async (tx) => {
        const productIds = lines.map((line) => line.productId);
        const products = await tx.product.findMany({ where: { id: { in: productIds } } });

        if (products.length !== productIds.length) {
          throw new WriteOffValidationError("One or more products were not found.");
        }

        for (const line of lines) {
          await assertSufficientStock(tx, line.productId, new Prisma.Decimal(line.quantity));
        }

        const created = await tx.writeOff.create({
          data: {
            reason,
            lines: {
              create: lines,
            },
          },
        });

        await tx.inventoryTransaction.createMany({
          data: lines.map((line) => ({
            productId: line.productId,
            type: TransactionType.ISSUE_SALE,
            quantity: new Prisma.Decimal(line.quantity).negated(),
            sourceDocument: `writeoff:${created.id}`,
          })),
        });

        return tx.writeOff.findUnique({
          where: { id: created.id },
          include: {
            lines: {
              include: {
                product: true,
              },
            },
          },
        });
      },
      { isolationLevel: Prisma.TransactionIsolationLevel.Serializable },
    );

    return NextResponse.json(writeOff, { status: 201 });
  } catch (error) {
    if (error instanceof WriteOffValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    if (error instanceof InventoryValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
