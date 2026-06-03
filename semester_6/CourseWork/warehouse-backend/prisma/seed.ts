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

  const electronics = await upsertSupplier(
    "Electronics Supply Hub",
    "Alan Brown",
    "sales@electronics-hub.example",
    "+1 555 0303",
    "88 Circuit Street",
  );
  const packaging = await upsertSupplier(
    "Packaging Materials Inc",
    "Olivia Green",
    "orders@packaging.example",
    "+1 555 0404",
    "7 Boxmaker Lane",
  );
  const mechanics = await upsertSupplier(
    "Precision Mechanics Group",
    "Sophia Clark",
    "supply@precision.example",
    "+1 555 0505",
    "19 Tooling Park",
  );
  const fasteners = await upsertSupplier(
    "Fasteners Warehouse",
    "Michael Lee",
    "desk@fasteners.example",
    "+1 555 0606",
    "101 Bolt Boulevard",
  );

  const bolt = await upsertProduct("CMP-BOLT-M8", "M8 Bolt", "pcs", ProductType.COMPONENT);
  const nut = await upsertProduct("CMP-NUT-M8", "M8 Nut", "pcs", ProductType.COMPONENT);
  const plate = await upsertProduct("CMP-STEEL-PLATE", "Steel Plate", "pcs", ProductType.COMPONENT);
  const motor = await upsertProduct("CMP-MOTOR-12V", "12V Motor", "pcs", ProductType.COMPONENT);
  const cable = await upsertProduct("CMP-CABLE-1M", "Power Cable 1m", "pcs", ProductType.COMPONENT);
  const sensor = await upsertProduct("CMP-SENSOR-TEMP", "Temperature Sensor", "pcs", ProductType.COMPONENT);
  const relay = await upsertProduct("CMP-RELAY-5V", "5V Relay", "pcs", ProductType.COMPONENT);
  const pcb = await upsertProduct("CMP-PCB-CTRL", "Control PCB", "pcs", ProductType.COMPONENT);
  const enclosure = await upsertProduct("CMP-ENCLOSURE-S", "Small Enclosure", "pcs", ProductType.COMPONENT);
  const label = await upsertProduct("CMP-LABEL-SET", "Product Label Set", "pcs", ProductType.COMPONENT);
  const box = await upsertProduct("CMP-BOX-SHIP", "Shipping Box", "pcs", ProductType.COMPONENT);
  const rubberFeet = await upsertProduct("CMP-RUBBER-FEET", "Rubber Feet", "pcs", ProductType.COMPONENT);
  const screw = await upsertProduct("CMP-SCREW-M3", "M3 Screw", "pcs", ProductType.COMPONENT);
  const connector = await upsertProduct("CMP-CONNECTOR-4P", "4-pin Connector", "pcs", ProductType.COMPONENT);
  const bracket = await upsertProduct("CMP-BRACKET-U", "U Bracket", "pcs", ProductType.COMPONENT);
  const assemblyKit = await upsertProduct("FIN-ASSEMBLY-KIT", "Assembly Kit", "pcs", ProductType.FINISHED);
  const controlBox = await upsertProduct("FIN-CONTROL-BOX", "Control Box", "pcs", ProductType.FINISHED);
  const sensorModule = await upsertProduct("FIN-SENSOR-MODULE", "Sensor Module", "pcs", ProductType.FINISHED);
  const powerUnit = await upsertProduct("FIN-POWER-DIST", "Power Distribution Unit", "pcs", ProductType.FINISHED);
  const starterKit = await upsertProduct("FIN-STARTER-KIT", "Starter Kit", "pcs", ProductType.FINISHED);
  const panelKit = await upsertProduct("FIN-PANEL-MOUNT", "Panel Mount Kit", "pcs", ProductType.FINISHED);

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

  await createBom(sensorModule.id, [
    { componentId: sensor.id, quantity: "2" },
    { componentId: pcb.id, quantity: "1" },
    { componentId: enclosure.id, quantity: "1" },
    { componentId: connector.id, quantity: "1" },
  ]);

  await createBom(powerUnit.id, [
    { componentId: relay.id, quantity: "3" },
    { componentId: pcb.id, quantity: "1" },
    { componentId: cable.id, quantity: "3" },
    { componentId: screw.id, quantity: "6" },
  ]);

  await createBom(starterKit.id, [
    { componentId: cable.id, quantity: "1" },
    { componentId: connector.id, quantity: "2" },
    { componentId: screw.id, quantity: "4" },
    { componentId: box.id, quantity: "1" },
    { componentId: label.id, quantity: "1" },
  ]);

  await createBom(panelKit.id, [
    { componentId: bracket.id, quantity: "2" },
    { componentId: screw.id, quantity: "8" },
    { componentId: rubberFeet.id, quantity: "4" },
    { componentId: label.id, quantity: "1" },
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

  await createReceipt(electronics.id, "ESH-INV-3001", "2026-05-26T09:30:00.000Z", [
    { productId: sensor.id, quantity: "160", purchasePrice: "7.20" },
    { productId: relay.id, quantity: "180", purchasePrice: "3.40" },
    { productId: pcb.id, quantity: "90", purchasePrice: "11.50" },
  ]);

  await createReceipt(packaging.id, "PMI-INV-4100", "2026-05-27T11:15:00.000Z", [
    { productId: box.id, quantity: "220", purchasePrice: "1.10" },
    { productId: label.id, quantity: "260", purchasePrice: "0.35" },
  ]);

  await createReceipt(mechanics.id, "PMG-INV-7780", "2026-05-28T14:20:00.000Z", [
    { productId: enclosure.id, quantity: "120", purchasePrice: "6.80" },
    { productId: bracket.id, quantity: "140", purchasePrice: "2.75" },
    { productId: rubberFeet.id, quantity: "420", purchasePrice: "0.22" },
  ]);

  await createReceipt(fasteners.id, "FW-INV-9090", "2026-05-29T08:45:00.000Z", [
    { productId: screw.id, quantity: "900", purchasePrice: "0.06" },
    { productId: bolt.id, quantity: "500", purchasePrice: "0.17" },
    { productId: nut.id, quantity: "500", purchasePrice: "0.11" },
  ]);

  await createReceipt(electronics.id, "ESH-INV-3002", "2026-05-30T16:10:00.000Z", [
    { productId: connector.id, quantity: "260", purchasePrice: "1.45" },
    { productId: cable.id, quantity: "160", purchasePrice: "2.10" },
    { productId: motor.id, quantity: "30", purchasePrice: "17.50" },
  ]);

  await createReceipt(packaging.id, "PMI-INV-4101", "2026-06-01T10:05:00.000Z", [
    { productId: assemblyKit.id, quantity: "10", purchasePrice: "6.20" },
    { productId: controlBox.id, quantity: "6", purchasePrice: "23.50" },
    { productId: box.id, quantity: "100", purchasePrice: "1.05" },
  ]);

  await createProductionOrder(assemblyKit.id, "12", [
    { componentId: bolt.id, quantity: "48" },
    { componentId: nut.id, quantity: "48" },
    { componentId: plate.id, quantity: "12" },
  ]);

  await createProductionOrder(controlBox.id, "8", [
    { componentId: motor.id, quantity: "8" },
    { componentId: cable.id, quantity: "16" },
    { componentId: bolt.id, quantity: "16" },
  ]);

  await createProductionOrder(sensorModule.id, "18", [
    { componentId: sensor.id, quantity: "36" },
    { componentId: pcb.id, quantity: "18" },
    { componentId: enclosure.id, quantity: "18" },
    { componentId: connector.id, quantity: "18" },
  ]);

  await createProductionOrder(powerUnit.id, "14", [
    { componentId: relay.id, quantity: "42" },
    { componentId: pcb.id, quantity: "14" },
    { componentId: cable.id, quantity: "42" },
    { componentId: screw.id, quantity: "84" },
  ]);

  await createProductionOrder(starterKit.id, "5", [
    { componentId: cable.id, quantity: "5" },
    { componentId: connector.id, quantity: "10" },
    { componentId: screw.id, quantity: "20" },
    { componentId: box.id, quantity: "5" },
    { componentId: label.id, quantity: "5" },
  ]);

  await createProductionOrder(panelKit.id, "24", [
    { componentId: bracket.id, quantity: "48" },
    { componentId: screw.id, quantity: "192" },
    { componentId: rubberFeet.id, quantity: "96" },
    { componentId: label.id, quantity: "24" },
  ]);

  await createWriteOff(WriteOffReason.SALE, [
    { productId: assemblyKit.id, quantity: "3" },
    { productId: controlBox.id, quantity: "2" },
  ]);

  await createWriteOff(WriteOffReason.SALE, [
    { productId: sensorModule.id, quantity: "4" },
    { productId: panelKit.id, quantity: "6" },
  ]);

  await createWriteOff(WriteOffReason.SALE, [
    { productId: powerUnit.id, quantity: "3" },
    { productId: starterKit.id, quantity: "2" },
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

async function upsertSupplier(
  name: string,
  contactName: string,
  contactEmail: string,
  contactPhone: string,
  address: string,
) {
  return prisma.supplier.upsert({
    where: { name },
    update: { contactName, contactEmail, contactPhone, address },
    create: { name, contactName, contactEmail, contactPhone, address },
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
) {
  const totalCost = await calculateSeedProductionCost(components);
  const unitCost = totalCost.div(new Prisma.Decimal(outputQuantity));

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
      unitCost,
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
      totalCost,
      unitCost,
      calculationData: {
        outputQuantity,
        components: await Promise.all(components.map(async (component) => {
          const averageUnitCost = await getSeedWeightedAverageCost(component.componentId);
          const quantity = new Prisma.Decimal(component.quantity);

          return {
            componentId: component.componentId,
            quantity: component.quantity,
            averageUnitCost: averageUnitCost.toString(),
            lineCost: quantity.mul(averageUnitCost).toString(),
          };
        })),
      },
    },
  });
}

async function calculateSeedProductionCost(components: Array<{ componentId: string; quantity: string }>) {
  let total = new Prisma.Decimal(0);

  for (const component of components) {
    const averageUnitCost = await getSeedWeightedAverageCost(component.componentId);
    total = total.add(new Prisma.Decimal(component.quantity).mul(averageUnitCost));
  }

  return total;
}

async function getSeedWeightedAverageCost(productId: string) {
  const receiptLines = await prisma.receiptLine.findMany({
    where: { productId },
    select: { quantity: true, purchasePrice: true },
  });

  const totals = receiptLines.reduce(
    (acc, line) => ({
      quantity: acc.quantity.add(line.quantity),
      value: acc.value.add(line.quantity.mul(line.purchasePrice)),
    }),
    { quantity: new Prisma.Decimal(0), value: new Prisma.Decimal(0) },
  );

  if (totals.quantity.isZero()) {
    throw new Error(`Cannot calculate seed production cost without receipt history for product ${productId}.`);
  }

  return totals.value.div(totals.quantity);
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
