import assert from "node:assert/strict";
import test from "node:test";

import {
  buildProductionOrderPayload,
  buildProductionRecipePayload,
  buildReceiptPayload,
  buildWriteOffPayload,
} from "@/lib/form-payloads";

function createFormData(entries: Array<[string, string]>): FormData {
  const formData = new FormData();
  for (const [key, value] of entries) {
    formData.append(key, value);
  }
  return formData;
}

test("buildReceiptPayload validates and converts datetime-local to ISO", () => {
  const payload = buildReceiptPayload(
    createFormData([
      ["supplierId", "s-1"],
      ["invoiceNumber", "INV-1"],
      ["invoiceDate", "2026-06-01T12:30"],
      ["productId", "p-1"],
      ["quantity", "2"],
      ["purchasePrice", "10.5"],
    ]),
  );

  assert.equal(payload.supplierId, "s-1");
  assert.equal(payload.lines[0].quantity, 2);
  assert.equal(payload.lines[0].purchasePrice, 10.5);
  assert.match(payload.invoiceDate, /^2026-06-01T/);
});

test("buildReceiptPayload supports multiple unique lines", () => {
  const payload = buildReceiptPayload(
    createFormData([
      ["supplierId", "s-1"],
      ["invoiceNumber", "INV-2"],
      ["invoiceDate", "2026-06-01T12:30"],
      ["productId", "p-1"],
      ["quantity", "2"],
      ["purchasePrice", "10"],
      ["productId", "p-2"],
      ["quantity", "3"],
      ["purchasePrice", "20"],
    ]),
  );

  assert.equal(payload.lines.length, 2);
  assert.equal(payload.lines[1].productId, "p-2");
});

test("buildReceiptPayload rejects duplicate products", () => {
  assert.throws(() =>
    buildReceiptPayload(
      createFormData([
        ["supplierId", "s-1"],
        ["invoiceNumber", "INV-3"],
        ["invoiceDate", "2026-06-01T12:30"],
        ["productId", "p-1"],
        ["quantity", "2"],
        ["purchasePrice", "10"],
        ["productId", "p-1"],
        ["quantity", "3"],
        ["purchasePrice", "20"],
      ]),
    ),
  );
});

test("buildReceiptPayload rejects invalid quantity", () => {
  assert.throws(() =>
    buildReceiptPayload(
      createFormData([
        ["supplierId", "s-1"],
        ["invoiceNumber", "INV-1"],
        ["invoiceDate", "2026-06-01T12:30"],
        ["productId", "p-1"],
        ["quantity", "0"],
        ["purchasePrice", "10"],
      ]),
    ),
  );
});

test("buildWriteOffPayload validates quantity", () => {
  const payload = buildWriteOffPayload(
    createFormData([
      ["reason", "SALE"],
      ["productId", "p-1"],
      ["quantity", "3"],
    ]),
  );

  assert.equal(payload.reason, "SALE");
  assert.equal(payload.lines[0].quantity, 3);
});

test("buildWriteOffPayload supports multiple unique lines", () => {
  const payload = buildWriteOffPayload(
    createFormData([
      ["reason", "SALE"],
      ["productId", "p-1"],
      ["quantity", "3"],
      ["productId", "p-2"],
      ["quantity", "4"],
    ]),
  );

  assert.equal(payload.lines.length, 2);
  assert.equal(payload.lines[1].productId, "p-2");
  assert.equal(payload.lines[1].quantity, 4);
});

test("buildWriteOffPayload rejects duplicate products", () => {
  assert.throws(() =>
    buildWriteOffPayload(
      createFormData([
        ["reason", "SALE"],
        ["productId", "p-1"],
        ["quantity", "3"],
        ["productId", "p-1"],
        ["quantity", "4"],
      ]),
    ),
  );
});

test("buildWriteOffPayload rejects invalid reason", () => {
  assert.throws(() =>
    buildWriteOffPayload(
      createFormData([
        ["reason", "INVALID"],
        ["productId", "p-1"],
        ["quantity", "3"],
      ]),
    ),
  );
  assert.throws(() =>
    buildWriteOffPayload(
      createFormData([
        ["reason", "PRODUCTION"],
        ["productId", "p-1"],
        ["quantity", "3"],
      ]),
    ),
  );
});

test("buildProductionOrderPayload validates payload", () => {
  const payload = buildProductionOrderPayload(
    createFormData([
      ["finishedProductId", "f-1"],
      ["quantity", "1.25"],
    ]),
  );

  assert.equal(payload.finishedProductId, "f-1");
  assert.equal(payload.quantity, 1.25);
});

test("buildProductionOrderPayload rejects invalid quantity", () => {
  assert.throws(() =>
    buildProductionOrderPayload(
      createFormData([
        ["finishedProductId", "f-1"],
        ["quantity", "-1"],
      ]),
    ),
  );
});

test("buildProductionRecipePayload supports multiple components", () => {
  const payload = buildProductionRecipePayload(
    createFormData([
      ["finishedProductId", "f-1"],
      ["componentId", "c-1"],
      ["componentQuantity", "2"],
      ["componentId", "c-2"],
      ["componentQuantity", "3"],
    ]),
  );

  assert.equal(payload.finishedProductId, "f-1");
  assert.equal(payload.items.length, 2);
});

test("buildProductionRecipePayload rejects duplicate components", () => {
  assert.throws(() =>
    buildProductionRecipePayload(
      createFormData([
        ["finishedProductId", "f-1"],
        ["componentId", "c-1"],
        ["componentQuantity", "2"],
        ["componentId", "c-1"],
        ["componentQuantity", "3"],
      ]),
    ),
  );
});
