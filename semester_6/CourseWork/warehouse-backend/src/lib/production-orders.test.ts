import assert from "node:assert/strict";
import test from "node:test";

import {
  ProductionOrderValidationError,
  requireProductionProductId,
  requireProductionQuantity,
} from "@/lib/production-orders";

test("requireProductionProductId validates id", () => {
  assert.equal(requireProductionProductId("  p-1 "), "p-1");
  assert.throws(() => requireProductionProductId(""), ProductionOrderValidationError);
});

test("requireProductionQuantity validates quantity", () => {
  assert.equal(requireProductionQuantity(2.5), 2.5);
  assert.throws(() => requireProductionQuantity(0), ProductionOrderValidationError);
  assert.throws(() => requireProductionQuantity(Number.POSITIVE_INFINITY), ProductionOrderValidationError);
});
