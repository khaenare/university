import { hash } from "bcryptjs";

import { Prisma, ProductType, TransactionType, UserRole, WriteOffReason } from "@prisma/client";

import { prisma } from "../src/lib/prisma";

async function main() {
  const adminEmail = process.env.SEED_ADMIN_EMAIL ?? "admin@localhost";
  const adminPassword = process.env.SEED_ADMIN_PASSWORD ?? "admin12345";

  if (process.env.NODE_ENV === "production") {
    throw new Error("Seed script is blocked in production environment.");
  }

  if (adminPassword.length < 10) {
    throw new Error("Admin seed password must be at least 10 characters long.");
  }
  const passwordHash = await hash(adminPassword, 10);

  await prisma.user.upsert({
    where: { email: adminEmail },
    update: {
      passwordHash,
      role: UserRole.ADMIN,
    },
    create: {
      email: adminEmail,
      passwordHash,
      role: UserRole.ADMIN,
    },
  });

  const managerPasswordHash = await hash(process.env.SEED_MANAGER_PASSWORD ?? "manager12345", 10);
  await prisma.user.upsert({
    where: { email: "manager@localhost" },
    update: {
      passwordHash: managerPasswordHash,
      role: UserRole.MANAGER,
    },
    create: {
      email: "manager@localhost",
      passwordHash: managerPasswordHash,
      role: UserRole.MANAGER,
    },
  });

  await prisma.costSnapshot.deleteMany();
  await prisma.productionOrderItem.deleteMany();
  await prisma.productionOrder.deleteMany();
  await prisma.inventoryTransaction.deleteMany();
  await prisma.writeOffLine.deleteMany();
  await prisma.writeOff.deleteMany();
  await prisma.receiptLine.deleteMany();
  await prisma.receipt.deleteMany();
  await prisma.bomItem.deleteMany();
  await prisma.bom.deleteMany();

  const metalParts = await prisma.supplier.upsert({
    where: { name: "Metal Parts Ltd" },
    update: {
      contactName: "John Smith",
      contactEmail: "sales@metalparts.example",
      contactPhone: "+1 555 0101",
      address: "12 Industrial Road",
    },
    create: {
      name: "Metal Parts Ltd",
      contactName: "John Smith",
      contactEmail: "sales@metalparts.example",
      contactPhone: "+1 555 0101",
      address: "12 Industrial Road",
    },
  });

  const industrial = await prisma.supplier.upsert({
    where: { name: "Industrial Components Co" },
    update: {
      contactName: "Mary Johnson",
      contactEmail: "orders@industrial.example",
      contactPhone: "+1 555 0202",
      address: "45 Factory Avenue",
    },
    create: {
      name: "Industrial Components Co",
      contactName: "Mary Johnson",
      contactEmail: "orders@industrial.example",
      contactPhone: "+1 555 0202",
      address: "45 Factory Avenue",
    },
  });

  const bolt = await upsertProduct("CMP-BOLT-M8", "M8 Bolt", "pcs", ProductType.COMPONENT);
  const nut = await upsertProduct("CMP-NUT-M8", "M8 Nut", "pcs", ProductType.COMPONENT);
  const plate = await upsertProduct("CMP-STEEL-PLATE", "Steel Plate", "pcs", ProductType.COMPONENT);
  const motor = await upsertProduct("CMP-MOTOR-12V", "12V Motor", "pcs", ProductType.COMPONENT);
  const cable = await upsertProduct("CMP-CABLE-1M", "Power Cable 1m", "pcs", ProductType.COMPONENT);
  const assemblyKit = await upsertProduct("FIN-ASSEMBLY-KIT", "Assembly Kit", "pcs", ProductType.FINISHED);
  const controlBox = await upsertProduct("FIN-CONTROL-BOX", "Control Box", "pcs", ProductType.FINISHED);

  await createBom(assemblyKit.id, [
    { componentId: bolt.id, quantity: "4" },
    { componentId: nut.id, quantity: "4" },
    { componentId: plate.id, quantity: "1" },
  ]);

  await createBom(controlBox.id, [
    { componentId: motor.id, quantity: "1" },
    { componentId: cable.id, quantity: "2" },
    { componentId: bolt.id, quantity: "2" },
  ]);

  await createReceipt(metalParts.id, "MP-INV-1001", "2026-05-20T09:00:00.000Z", [
    { productId: bolt.id, quantity: "500", purchasePrice: "0.15" },
    { productId: nut.id, quantity: "500", purchasePrice: "0.10" },
    { productId: plate.id, quantity: "80", purchasePrice: "5.50" },
  ]);

  await createReceipt(industrial.id, "IC-INV-2050", "2026-05-21T10:00:00.000Z", [
    { productId: motor.id, quantity: "40", purchasePrice: "18.00" },
    { productId: cable.id, quantity: "120", purchasePrice: "2.25" },
  ]);

  await createReceipt(metalParts.id, "MP-INV-1002", "2026-05-25T12:00:00.000Z", [
    { productId: bolt.id, quantity: "300", purchasePrice: "0.18" },
    { productId: nut.id, quantity: "300", purchasePrice: "0.12" },
  ]);

  await createProductionOrder(assemblyKit.id, "12", [
    { componentId: bolt.id, quantity: "48" },
    { componentId: nut.id, quantity: "48" },
    { componentId: plate.id, quantity: "12" },
  ], "66.96", "5.5800");

  await createProductionOrder(controlBox.id, "8", [
    { componentId: motor.id, quantity: "8" },
    { componentId: cable.id, quantity: "16" },
    { componentId: bolt.id, quantity: "16" },
  ], "181.68", "22.7100");

  await createWriteOff(WriteOffReason.SALE, [
    { productId: assemblyKit.id, quantity: "3" },
    { productId: controlBox.id, quantity: "2" },
  ]);

  console.log(`Seeded admin user: ${adminEmail}`);
  console.log("Seeded manager user: manager@localhost");
  console.log("Seeded demo warehouse data.");
}

async function upsertProduct(sku: string, name: string, unit: string, type: ProductType) {
  return prisma.product.upsert({
    where: { sku },
    update: { name, unit, type, isActive: true },
    create: { sku, name, unit, type, isActive: true },
  });
}

async function createBom(
  finishedProductId: string,
  items: Array<{ componentId: string; quantity: string }>,
) {
  await prisma.bom.deleteMany({ where: { finishedProductId } });
  return prisma.bom.create({
    data: {
      finishedProductId,
      items: {
        create: items.map((item) => ({
          componentId: item.componentId,
          quantity: new Prisma.Decimal(item.quantity),
        })),
      },
    },
  });
}

async function createReceipt(
  supplierId: string,
  invoiceNumber: string,
  invoiceDate: string,
  lines: Array<{ productId: string; quantity: string; purchasePrice: string }>,
) {
  const receipt = await prisma.receipt.create({
    data: {
      supplierId,
      invoiceNumber,
      invoiceDate: new Date(invoiceDate),
      lines: {
        create: lines.map((line) => ({
          productId: line.productId,
          quantity: new Prisma.Decimal(line.quantity),
          purchasePrice: new Prisma.Decimal(line.purchasePrice),
        })),
      },
    },
  });

  await prisma.inventoryTransaction.createMany({
    data: lines.map((line) => ({
      productId: line.productId,
      type: TransactionType.RECEIPT,
      quantity: new Prisma.Decimal(line.quantity),
      unitCost: new Prisma.Decimal(line.purchasePrice),
      sourceDocument: `receipt:${receipt.id}`,
    })),
  });
}

async function createProductionOrder(
  finishedProductId: string,
  outputQuantity: string,
  components: Array<{ componentId: string; quantity: string }>,
  totalCost: string,
  unitCost: string,
) {
  const order = await prisma.productionOrder.create({
    data: {
      finishedProductId,
      quantity: new Prisma.Decimal(outputQuantity),
      items: {
        create: components.map((component) => ({
          componentId: component.componentId,
          quantity: new Prisma.Decimal(component.quantity),
        })),
      },
    },
  });

  await prisma.inventoryTransaction.create({
    data: {
      productId: finishedProductId,
      type: TransactionType.PRODUCTION_OUTPUT,
      quantity: new Prisma.Decimal(outputQuantity),
      unitCost: new Prisma.Decimal(unitCost),
      sourceDocument: `production:${order.id}`,
    },
  });

  await prisma.inventoryTransaction.createMany({
    data: components.map((component) => ({
      productId: component.componentId,
      type: TransactionType.ISSUE_PRODUCTION,
      quantity: new Prisma.Decimal(component.quantity).negated(),
      sourceDocument: `production:${order.id}`,
    })),
  });

  await prisma.costSnapshot.create({
    data: {
      productionOrderId: order.id,
      finishedProductId,
      totalCost: new Prisma.Decimal(totalCost),
      unitCost: new Prisma.Decimal(unitCost),
      calculationData: {
        outputQuantity,
        components,
      },
    },
  });
}

async function createWriteOff(
  reason: WriteOffReason,
  lines: Array<{ productId: string; quantity: string }>,
) {
  const writeOff = await prisma.writeOff.create({
    data: {
      reason,
      lines: {
        create: lines.map((line) => ({
          productId: line.productId,
          quantity: new Prisma.Decimal(line.quantity),
        })),
      },
    },
  });

  await prisma.inventoryTransaction.createMany({
    data: lines.map((line) => ({
      productId: line.productId,
      type: TransactionType.ISSUE_SALE,
      quantity: new Prisma.Decimal(line.quantity).negated(),
      sourceDocument: `writeoff:${writeOff.id}`,
    })),
  });
}

main()
  .catch((error) => {
    console.error("Seed failed:", error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
