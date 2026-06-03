import { ProductType, Prisma, TransactionType } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";
import {
  ReceiptValidationError,
  requireInvoiceDate,
  requireReceiptId,
  requireReceiptLines,
} from "@/lib/receipts";

type CreateReceiptBody = {
  supplierId?: string;
  invoiceNumber?: string;
  invoiceDate?: string;
  lines?: Array<{
    productId?: string;
    quantity?: number;
    purchasePrice?: number;
  }>;
};

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const receipts = await prisma.receipt.findMany({
    include: {
      supplier: true,
      lines: {
        include: {
          product: true,
        },
      },
    },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(receipts);
}

export async function POST(request: NextRequest) {
  const authorizationError = requireRole(request, ["ADMIN", "MANAGER"]);

  if (authorizationError) {
    return authorizationError;
  }

  const parsedBody = await parseJsonObjectBody<CreateReceiptBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const supplierId = requireReceiptId(parsedBody.supplierId, "Supplier ID");
    const invoiceNumber = requireReceiptId(parsedBody.invoiceNumber, "Invoice number");
    const invoiceDate = requireInvoiceDate(parsedBody.invoiceDate);
    const lines = requireReceiptLines(parsedBody.lines);

    const receipt = await prisma.$transaction(async (tx) => {
      const supplier = await tx.supplier.findUnique({ where: { id: supplierId } });
      if (!supplier) {
        throw new ReceiptValidationError("Supplier not found.");
      }

      const productIds = Array.from(new Set(lines.map((line) => line.productId)));
      const products = await tx.product.findMany({ where: { id: { in: productIds } } });

      if (products.length !== productIds.length) {
        throw new ReceiptValidationError("One or more products were not found.");
      }

      for (const product of products) {
        if (product.type !== ProductType.COMPONENT && product.type !== ProductType.FINISHED) {
          throw new ReceiptValidationError(`Product ${product.id} has unsupported type.`);
        }
      }

      const createdReceipt = await tx.receipt.create({
        data: {
          supplierId,
          invoiceNumber,
          invoiceDate,
          lines: {
            create: lines,
          },
        },
      });

      await tx.inventoryTransaction.createMany({
        data: lines.map((line) => ({
          productId: line.productId,
          type: TransactionType.RECEIPT,
          quantity: new Prisma.Decimal(line.quantity),
          unitCost: new Prisma.Decimal(line.purchasePrice),
          sourceDocument: `receipt:${createdReceipt.id}`,
        })),
      });

      return tx.receipt.findUnique({
        where: { id: createdReceipt.id },
        include: {
          supplier: true,
          lines: {
            include: {
              product: true,
            },
          },
        },
      });
    });

    return NextResponse.json(receipt, { status: 201 });
  } catch (error) {
    if (error instanceof ReceiptValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    throw error;
  }
}
