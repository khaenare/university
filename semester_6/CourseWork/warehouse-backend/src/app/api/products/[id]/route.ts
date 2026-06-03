import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";

import { OPERATOR_ROLES, requireRole } from "@/lib/authorization";
import { parseJsonObjectBody } from "@/lib/http";
import { prisma } from "@/lib/prisma";
import {
  ProductValidationError,
  validateOptionalBoolean,
  validatePatchProductType,
  validatePatchString,
} from "@/lib/products";

type ProductRouteContext = {
  params: Promise<{
    id: string;
  }>;
};

type UpdateProductBody = {
  sku?: string;
  name?: string;
  unit?: string;
  type?: string;
  isActive?: boolean;
};

export async function GET(request: NextRequest, context: ProductRouteContext) {
  const authorizationError = requireRole(request, OPERATOR_ROLES);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;
  const product = await prisma.product.findUnique({ where: { id } });

  if (!product) {
    return NextResponse.json({ message: "Product not found." }, { status: 404 });
  }

  return NextResponse.json(product);
}

export async function PATCH(request: NextRequest, context: ProductRouteContext) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;
  const parsedBody = await parseJsonObjectBody<UpdateProductBody>(request);

  if (parsedBody instanceof NextResponse) {
    return parsedBody;
  }

  try {
    const data: UpdateProductBody = {};

    if (parsedBody.sku !== undefined) {
      data.sku = validatePatchString(parsedBody.sku, "Product SKU");
    }

    if (parsedBody.name !== undefined) {
      data.name = validatePatchString(parsedBody.name, "Product name");
    }

    if (parsedBody.unit !== undefined) {
      data.unit = validatePatchString(parsedBody.unit, "Product unit");
    }

    if (parsedBody.type !== undefined) {
      data.type = validatePatchProductType(parsedBody.type);
    }

    if (parsedBody.isActive !== undefined) {
      data.isActive = validateOptionalBoolean(parsedBody.isActive, "isActive");
    }

    if (Object.keys(data).length === 0) {
      return NextResponse.json({ message: "At least one field must be provided." }, { status: 400 });
    }

    const updated = await prisma.product.update({
      where: { id },
      data,
    });

    return NextResponse.json(updated);
  } catch (error) {
    if (error instanceof ProductValidationError) {
      return NextResponse.json({ message: error.message }, { status: 400 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "Product not found." }, { status: 404 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2002") {
      return NextResponse.json({ message: "Product with this SKU already exists." }, { status: 409 });
    }

    throw error;
  }
}

export async function DELETE(request: NextRequest, context: ProductRouteContext) {
  const authorizationError = requireRole(request, ["ADMIN"]);

  if (authorizationError) {
    return authorizationError;
  }

  const { id } = await context.params;

  try {
    await prisma.product.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2025") {
      return NextResponse.json({ message: "Product not found." }, { status: 404 });
    }

    if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === "P2003") {
      return NextResponse.json(
        { message: "Cannot delete product with related inventory records." },
        { status: 409 },
      );
    }

    throw error;
  }
}
