const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NODE_ENV === "development" ? "http://localhost:3001" : "");

const ACCESS_TOKEN_KEY = "warehouse.accessToken";

export type StockValuationItem = {
  productId: string;
  sku: string;
  name: string;
  unit: string;
  type: string;
  quantity: string;
  unitCost: string;
  valuation: string;
};

export type StockValuationResponse = {
  totalValuation: string;
  items: StockValuationItem[];
};

export type ProductionCostItem = {
  snapshotId: string;
  productionOrderId: string;
  finishedProduct: {
    id: string;
    sku: string;
    name: string;
    unit: string;
  };
  outputQuantity: string;
  totalCost: string;
  unitCost: string;
  calculationData: unknown;
  createdAt: string;
};

export type ProductionCostResponse = {
  items: ProductionCostItem[];
};

export type MovementItem = {
  id: string;
  product: {
    id: string;
    sku: string;
    name: string;
    unit: string;
  };
  type: string;
  quantity: string;
  unitCost: string | null;
  sourceDocument: string | null;
  createdAt: string;
};

export type MovementsResponse = {
  items: MovementItem[];
};

export type SupplierOption = {
  id: string;
  name: string;
};

export type ProductOption = {
  id: string;
  sku: string;
  name: string;
  type: "COMPONENT" | "FINISHED";
  unit?: string;
  isActive?: boolean;
  createdAt?: string;
};

export type SupplierItem = SupplierOption & {
  contactName: string | null;
  contactEmail: string | null;
  contactPhone: string | null;
  address: string | null;
  createdAt: string;
};

export type CreateProductPayload = {
  sku: string;
  name: string;
  unit: string;
  type: "COMPONENT" | "FINISHED";
  isActive?: boolean;
};

export type CreateSupplierPayload = {
  name: string;
  contactName?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  address?: string | null;
};

export type ReceiptItem = {
  id: string;
  supplierId: string;
  supplier?: SupplierOption;
  invoiceNumber: string;
  invoiceDate: string;
  createdAt: string;
  lines?: Array<{
    product?: ProductOption;
    quantity: string;
    purchasePrice: string;
  }>;
};

export type ReceiptsResponse = {
  items: ReceiptItem[];
};

export type CreateReceiptPayload = {
  supplierId: string;
  invoiceNumber: string;
  invoiceDate: string;
  lines: Array<{
    productId: string;
    quantity: number;
    purchasePrice: number;
  }>;
};

export type WriteOffItem = {
  id: string;
  reason: "SALE";
  createdAt: string;
  lines?: Array<{
    product?: ProductOption;
    quantity: string;
  }>;
};

export type CreateWriteOffPayload = {
  reason: "SALE";
  lines: Array<{
    productId: string;
    quantity: number;
  }>;
};

export type ProductionOrderItem = {
  id: string;
  finishedProductId: string;
  finishedProduct?: ProductOption;
  quantity: string;
  createdAt: string;
};

export type CreateProductionOrderPayload = {
  finishedProductId: string;
  quantity: number;
};

export type ProductionRecipeItem = {
  id: string;
  finishedProductId: string;
  finishedProduct?: ProductOption;
  items: Array<{
    componentId: string;
    quantity: string;
    component?: ProductOption;
  }>;
};

export type CreateProductionRecipePayload = {
  finishedProductId: string;
  items: Array<{
    componentId: string;
    quantity: number;
  }>;
};

export type UserRole = "ADMIN" | "MANAGER";

export type AuthUser = {
  id: string;
  email: string;
  role: UserRole;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  accessToken: string;
  refreshToken: string;
  user: AuthUser;
};

async function request<T>(path: string): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: authHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    handleUnauthorized(path, response.status);
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as T;
}

async function requestWithBody<TResponse, TPayload>(
  path: string,
  method: "POST" | "PATCH" | "DELETE",
  payload: TPayload,
): Promise<TResponse> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      "content-type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    handleUnauthorized(path, response.status);
    throw new Error(await readErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  return (await response.json()) as TResponse;
}

function authHeaders(): HeadersInit {
  if (typeof window === "undefined") {
    return {};
  }

  const token = window.localStorage.getItem(ACCESS_TOKEN_KEY);

  if (!token) {
    return {};
  }

  return { authorization: `Bearer ${token}` };
}

function handleUnauthorized(path: string, status: number) {
  if (status !== 401 || path.startsWith("/api/auth/login")) {
    return;
  }

  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem("warehouse.refreshToken");
  window.dispatchEvent(new Event("warehouse:unauthorized"));
}

async function readErrorMessage(response: Response): Promise<string> {
  const text = await response.text();

  if (!text) {
    return `Request failed with status ${response.status}`;
  }

  try {
    const parsed = JSON.parse(text) as { message?: string };
    return parsed.message ?? text;
  } catch {
    return text;
  }
}

export function login(payload: LoginPayload): Promise<LoginResponse> {
  return requestWithBody<LoginResponse, LoginPayload>("/api/auth/login", "POST", payload);
}

export async function getCurrentUser(accessToken: string): Promise<AuthUser> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured.");
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    handleUnauthorized("/api/auth/me", response.status);
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as AuthUser;
}

export function logout(refreshToken: string): Promise<unknown> {
  return requestWithBody<unknown, { refreshToken: string }>("/api/auth/logout", "POST", { refreshToken });
}

export function getStockValuation(): Promise<StockValuationResponse> {
  return request<StockValuationResponse>("/api/reports/stock-valuation");
}

export function getProductionCosts(limit?: number): Promise<ProductionCostResponse> {
  const query = limit === undefined ? "" : `?limit=${limit}`;
  return request<ProductionCostResponse>(`/api/reports/production-cost${query}`);
}

export function getMovements(limit?: number): Promise<MovementsResponse> {
  const query = limit === undefined ? "" : `?limit=${limit}`;
  return request<MovementsResponse>(`/api/reports/movements${query}`);
}

export async function getReceipts(): Promise<ReceiptsResponse> {
  const data = await request<ReceiptItem[]>("/api/receipts");
  return { items: data };
}

export function createReceipt(payload: CreateReceiptPayload): Promise<unknown> {
  return requestWithBody<unknown, CreateReceiptPayload>("/api/receipts", "POST", payload);
}

export function deleteReceipt(id: string): Promise<void> {
  return requestWithBody<void, Record<string, never>>(`/api/receipts/${id}`, "DELETE", {});
}

export async function getWriteOffs(): Promise<{ items: WriteOffItem[] }> {
  const data = await request<WriteOffItem[]>("/api/writeoffs");
  return { items: data };
}

export function createWriteOff(payload: CreateWriteOffPayload): Promise<unknown> {
  return requestWithBody<unknown, CreateWriteOffPayload>("/api/writeoffs", "POST", payload);
}

export function deleteWriteOff(id: string): Promise<void> {
  return requestWithBody<void, Record<string, never>>(`/api/writeoffs/${id}`, "DELETE", {});
}

export async function getProductionOrders(): Promise<{ items: ProductionOrderItem[] }> {
  const data = await request<ProductionOrderItem[]>("/api/production-orders");
  return { items: data };
}

export function createProductionOrder(payload: CreateProductionOrderPayload): Promise<unknown> {
  return requestWithBody<unknown, CreateProductionOrderPayload>(
    "/api/production-orders",
    "POST",
    payload,
  );
}

export function getSuppliers(): Promise<SupplierOption[]> {
  return request<SupplierOption[]>("/api/suppliers");
}

export function getSupplierList(): Promise<SupplierItem[]> {
  return request<SupplierItem[]>("/api/suppliers");
}

export function createSupplier(payload: CreateSupplierPayload): Promise<SupplierItem> {
  return requestWithBody<SupplierItem, CreateSupplierPayload>("/api/suppliers", "POST", payload);
}

export function updateSupplier(id: string, payload: Partial<CreateSupplierPayload>): Promise<SupplierItem> {
  return requestWithBody<SupplierItem, Partial<CreateSupplierPayload>>(`/api/suppliers/${id}`, "PATCH", payload);
}

export function deleteSupplier(id: string): Promise<void> {
  return requestWithBody<void, Record<string, never>>(`/api/suppliers/${id}`, "DELETE", {});
}

export function getProducts(): Promise<ProductOption[]> {
  return request<ProductOption[]>("/api/products");
}

export function createProduct(payload: CreateProductPayload): Promise<ProductOption> {
  return requestWithBody<ProductOption, CreateProductPayload>("/api/products", "POST", payload);
}

export function updateProduct(id: string, payload: Partial<CreateProductPayload>): Promise<ProductOption> {
  return requestWithBody<ProductOption, Partial<CreateProductPayload>>(`/api/products/${id}`, "PATCH", payload);
}

export function deleteProduct(id: string): Promise<void> {
  return requestWithBody<void, Record<string, never>>(`/api/products/${id}`, "DELETE", {});
}

export function getProductionRecipes(): Promise<ProductionRecipeItem[]> {
  return request<ProductionRecipeItem[]>("/api/bom");
}

export function createProductionRecipe(payload: CreateProductionRecipePayload): Promise<unknown> {
  return requestWithBody<unknown, CreateProductionRecipePayload>("/api/bom", "POST", payload);
}
