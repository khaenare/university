-- CreateTable
CREATE TABLE "ProductionOrder" (
    "id" TEXT NOT NULL,
    "finishedProductId" TEXT NOT NULL,
    "quantity" DECIMAL(14,3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ProductionOrder_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ProductionOrderItem" (
    "id" TEXT NOT NULL,
    "productionOrderId" TEXT NOT NULL,
    "componentId" TEXT NOT NULL,
    "quantity" DECIMAL(14,3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ProductionOrderItem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CostSnapshot" (
    "id" TEXT NOT NULL,
    "productionOrderId" TEXT NOT NULL,
    "finishedProductId" TEXT NOT NULL,
    "totalCost" DECIMAL(14,2) NOT NULL,
    "unitCost" DECIMAL(14,4) NOT NULL,
    "calculationData" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "CostSnapshot_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "ProductionOrder_finishedProductId_createdAt_idx" ON "ProductionOrder"("finishedProductId", "createdAt");

-- CreateIndex
CREATE INDEX "ProductionOrderItem_productionOrderId_idx" ON "ProductionOrderItem"("productionOrderId");

-- CreateIndex
CREATE INDEX "ProductionOrderItem_componentId_idx" ON "ProductionOrderItem"("componentId");

-- CreateIndex
CREATE UNIQUE INDEX "CostSnapshot_productionOrderId_key" ON "CostSnapshot"("productionOrderId");

-- CreateIndex
CREATE INDEX "CostSnapshot_finishedProductId_createdAt_idx" ON "CostSnapshot"("finishedProductId", "createdAt");

-- AddForeignKey
ALTER TABLE "ProductionOrder" ADD CONSTRAINT "ProductionOrder_finishedProductId_fkey" FOREIGN KEY ("finishedProductId") REFERENCES "Product"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProductionOrderItem" ADD CONSTRAINT "ProductionOrderItem_productionOrderId_fkey" FOREIGN KEY ("productionOrderId") REFERENCES "ProductionOrder"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProductionOrderItem" ADD CONSTRAINT "ProductionOrderItem_componentId_fkey" FOREIGN KEY ("componentId") REFERENCES "Product"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CostSnapshot" ADD CONSTRAINT "CostSnapshot_productionOrderId_fkey" FOREIGN KEY ("productionOrderId") REFERENCES "ProductionOrder"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CostSnapshot" ADD CONSTRAINT "CostSnapshot_finishedProductId_fkey" FOREIGN KEY ("finishedProductId") REFERENCES "Product"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
