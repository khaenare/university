import { ProductType, Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { assertProductType, BomValidationError, requireBomItems, requireId } from "@/lib/bom";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";

type BomRouteContext = {
  params: Promise<{ id: string }>;
};

type UpdateBomBody = {
  finishedProductId?: string;
  items?: Array<{
    componentId?: string;
    quantity?: number;
  }>;
};

export async function GET(request: NextRequest, context: BomRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;
  const bom = await prisma.bom.findUnique({
    where: { id },
    include: {
      finishedProduct: true,
      items: {
        include: {
          component: true,
        },
      },
    },
  });

  if (!bom) {
    return NextResponse.json({ message: "BOM not found." }, { status: 404 });
  }

  return NextResponse.json(bom);
}

export async function PATCH(request: NextRequest, context: BomRouteContext) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;
  const parsedBody = await parseJsonObjectBody<UpdateBomBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const hasFinishedProductId = parsedBody.finishedProductId !== undefined;
    const hasItems = parsedBody.items !== undefined;

    if (!hasFinishedProductId && !hasItems) {
      return NextResponse.json({ message: "At least one field must be provided." }, { status: 400 });
    }

    const updated = await prisma.$transaction(async (tx) => {
      const existing = await tx.bom.findUnique({ where: { id } });
      if (!existing) {
        return null;
      }

      const nextFinishedProductId = hasFinishedProductId
        ? requireId(parsedBody.finishedProductId, "Finished product ID")
        : existing.finishedProductId;

      const finishedProduct = await tx.product.findUnique({ where: { id: nextFinishedProductId } });
      if (!finishedProduct) {
        throw new BomValidationError("Finished product not found.");
      }

      assertProductType(
        finishedProduct.type,
        ProductType.FINISHED,
        "Finished product must have FINISHED type.",
      );

      const normalizedItems = hasItems ? requireBomItems(parsedBody.items) : null;

      if (normalizedItems) {
        const componentIds = normalizedItems.map((item) => item.componentId);
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
      }

      await tx.bom.update({
        where: { id },
        data: {
          finishedProductId: nextFinishedProductId,
        },
      });

      if (normalizedItems) {
        await tx.bomItem.deleteMany({ where: { bomId: id } });
        await tx.bomItem.createMany({
          data: normalizedItems.map((item) => ({
            bomId: id,
            componentId: item.componentId,
            quantity: item.quantity,
          })),
        });
      }

      return tx.bom.findUnique({
        where: { id },
        include: {
          finishedProduct: true,
          items: true,
        },
      });
    });

    if (!updated) {
      return NextResponse.json({ message: "BOM not found." }, { status: 404 });
    }

    return NextResponse.json(updated);
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

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "BOM not found." }, { status: 404 });
    }

    throw error;
  }
}

export async function DELETE(request: NextRequest, context: BomRouteContext) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  try {
    await prisma.bom.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "BOM not found." }, { status: 404 });
    }

    throw error;
  }
}
