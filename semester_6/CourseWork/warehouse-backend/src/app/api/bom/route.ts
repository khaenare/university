import { ProductType, Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { assertProductType, BomValidationError, requireBomItems, requireId } from "@/lib/bom";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";

type CreateBomBody = {
  finishedProductId?: string;
  items?: Array<{
    componentId?: string;
    quantity?: number;
  }>;
};

export async function GET(request: NextRequest) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const list = await prisma.bom.findMany({
    include: {
      finishedProduct: true,
      items: {
        include: {
          component: true,
        },
      },
    },
    orderBy: { createdAt: "desc" },
  });

  return NextResponse.json(list);
}

export async function POST(request: NextRequest) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const parsedBody = await parseJsonObjectBody<CreateBomBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const finishedProductId = requireId(parsedBody.finishedProductId, "Finished product ID");
    const items = requireBomItems(parsedBody.items);

    const bom = await prisma.$transaction(async (tx) => {
      const finishedProduct = await tx.product.findUnique({ where: { id: finishedProductId } });

      if (!finishedProduct) {
        throw new BomValidationError("Finished product not found.");
      }

      assertProductType(
        finishedProduct.type,
        ProductType.FINISHED,
        "Finished product must have FINISHED type.",
      );

      const componentIds = items.map((item) => item.componentId);
      const components = await tx.product.findMany({
        where: { id: { in: componentIds } },
      });

      if (components.length !== componentIds.length) {
        throw new BomValidationError("One or more BOM components were not found.");
      }

      for (const component of components) {
        assertProductType(
          component.type,
          ProductType.COMPONENT,
          `Product ${component.id} must have COMPONENT type to be used in BOM.`,
        );
      }

      return tx.bom.create({
        data: {
          finishedProductId,
          items: {
            create: items,
          },
        },
        include: {
          finishedProduct: true,
          items: true,
        },
      });
    });

    return NextResponse.json(bom, { status: 201 });
  } catch (error) {
    if (error instanceof BomValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2002") {
      return NextResponse.json(
        { message: "BOM for this finished product already exists." },
        { status: 409 },
      );
    }

    throw error;
  }
}
