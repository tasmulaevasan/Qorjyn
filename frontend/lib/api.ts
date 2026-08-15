import {
  InventoryItem,
  PurchaseWave,
  Order,
  Supplier,
  AiTenderResult,
  RescueTransfer,
  QorjynAppState
} from '@/types';
import { initialSeedData } from '@/lib/seedData';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api';

const LOCAL_STORAGE_KEY = 'qorjyn_state_v1';
const LEGACY_LOCAL_STORAGE_KEY = 'qorjyn_mesh_state_v1';

async function responseError(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    return typeof data.error === 'string' ? data.error : fallback;
  } catch {
    return fallback;
  }
}

export function getLocalState(): QorjynAppState {
  if (typeof window === 'undefined') return initialSeedData;
  try {
    const currentRaw = localStorage.getItem(LOCAL_STORAGE_KEY);
    const raw = currentRaw ?? localStorage.getItem(LEGACY_LOCAL_STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(initialSeedData));
      return initialSeedData;
    }
    if (!currentRaw) {
      localStorage.setItem(LOCAL_STORAGE_KEY, raw);
      localStorage.removeItem(LEGACY_LOCAL_STORAGE_KEY);
    }
    return JSON.parse(raw);
  } catch (e) {
    return initialSeedData;
  }
}

export function saveLocalState(state: QorjynAppState): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(state));
    window.dispatchEvent(new CustomEvent('qorjyn_state_change', { detail: state }));
  } catch (e) {
    console.error('Failed to save local state:', e);
  }
}

// Check backend availability
let isBackendLive = false;

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/inventory`, { method: 'GET', signal: AbortSignal.timeout(1500) });
    isBackendLive = res.ok;
    return res.ok;
  } catch {
    isBackendLive = false;
    return false;
  }
}

export function getBackendStatus(): boolean {
  return isBackendLive;
}

// 1. Fetch Inventory
export async function getInventory(params?: { locationId?: string; status?: string }): Promise<{
  success: boolean;
  inventory: InventoryItem[];
  isLive: boolean;
}> {
  try {
    const url = new URL(`${API_BASE_URL}/inventory`);
    if (params?.locationId) url.searchParams.append('locationId', params.locationId);
    if (params?.status) url.searchParams.append('status', params.status);

    const res = await fetch(url.toString());
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { success: true, inventory: data.inventory || [], isLive: true };
    }
  } catch (e) {
    console.warn('[API Client] Backend offline, using local state fallback');
  }

  isBackendLive = false;
  const state = getLocalState();
  let items = state.inventory.map(item => {
    const product = state.products.find(p => p.id === item.productId);
    const location = state.businesses
      .flatMap(b => b.locations || [])
      .find(l => l.id === item.locationId);
    const daysRemaining = product && product.avgDailyUsage > 0
      ? Math.round((item.currentStock / product.avgDailyUsage) * 10) / 10
      : 99;
    return { ...item, product, location, daysRemaining };
  });

  if (params?.locationId) items = items.filter(i => i.locationId === params.locationId);
  if (params?.status) items = items.filter(i => i.status === params.status);

  return { success: true, inventory: items, isLive: false };
}

// 2. Update Inventory Item
export async function updateInventoryItem(payload: {
  productId: string;
  locationId: string;
  delta: number;
  source?: string;
  note?: string;
}): Promise<{ success: boolean; inventoryItem?: InventoryItem; alert?: any; error?: string; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/inventory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { ...data, isLive: true };
    }

    isBackendLive = true;
    return {
      success: false,
      error: await responseError(res, 'Не удалось обновить остаток'),
      isLive: true
    };
  } catch (e) {
    console.warn('[API Client] Backend offline, executing update in local state');
  }

  isBackendLive = false;
  const state = getLocalState();
  const index = state.inventory.findIndex(
    i => i.productId === payload.productId && i.locationId === payload.locationId
  );

  if (index === -1) {
    return { success: false, isLive: false };
  }

  const item = state.inventory[index];
  const newStock = Math.max(0, item.currentStock + payload.delta);
  const product = state.products.find(p => p.id === payload.productId);

  let newStatus: 'ok' | 'low' | 'critical' | 'surplus' = 'ok';
  if (product) {
    if (newStock <= 0) newStatus = 'critical';
    else if (newStock < product.minStock * 0.4) newStatus = 'critical';
    else if (newStock < product.minStock) newStatus = 'low';
    else if (newStock > product.minStock * 3) newStatus = 'surplus';
  }

  const updatedItem: InventoryItem = {
    ...item,
    currentStock: newStock,
    status: newStatus,
    lastUpdated: new Date().toISOString()
  };

  state.inventory[index] = updatedItem;

  // Add event
  state.inventoryEvents.unshift({
    id: `evt-${Date.now()}`,
    productId: payload.productId,
    locationId: payload.locationId,
    type: payload.delta > 0 ? 'receipt' : 'sale',
    quantity: payload.delta,
    source: (payload.source as any) || 'manual',
    note: payload.note,
    timestamp: new Date().toISOString()
  });

  saveLocalState(state);

  const location = state.businesses.flatMap(b => b.locations || []).find(l => l.id === payload.locationId);
  const daysRemaining = product ? Math.round((newStock / product.avgDailyUsage) * 10) / 10 : 99;

  let alert = null;
  if (newStatus === 'critical' || newStatus === 'low') {
    alert = {
      type: 'low_stock',
      message: `⚠️ ${product?.name || 'Товар'} на исходе: ${newStock} ${product?.unit} (минимум: ${product?.minStock})`
    };
  }

  return {
    success: true,
    inventoryItem: { ...updatedItem, product, location, daysRemaining },
    alert,
    isLive: false
  };
}

// 3. Fetch Dashboard
export async function getDashboard(businessId = 'biz-001'): Promise<{
  success: boolean;
  kpis: any;
  inventoryChart: any[];
  savingsChart: any[];
  risks: any[];
  recentActivity: any[];
  isLive: boolean;
}> {
  try {
    const res = await fetch(`${API_BASE_URL}/dashboard?businessId=${businessId}`);
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { ...data, isLive: true };
    }
  } catch (e) {
    console.warn('[API Client] Backend offline, assembling dashboard from local state');
  }

  isBackendLive = false;
  const state = getLocalState();

  const bizLocations = state.businesses
    .find(b => b.id === businessId)?.locations?.map(l => l.id) || [];

  const bizItems = state.inventory.filter(i => bizLocations.includes(i.locationId));
  const atRisk = bizItems.filter(i => i.status === 'low' || i.status === 'critical').length;
  const activeOrders = state.orders.filter(o => o.status !== 'delivered' && o.status !== 'issue').length;

  const inventoryChart = [
    { date: "08.08", milk: 20, coffee: 3.5, cups: 400 },
    { date: "09.08", milk: 13, coffee: 3.2, cups: 355 },
    { date: "10.08", milk: 8, coffee: 3.0, cups: 310 },
    { date: "11.08", milk: 15, coffee: 2.8, cups: 450 },
    { date: "12.08", milk: 9, coffee: 2.6, cups: 390 },
    { date: "13.08", milk: 11, coffee: 2.5, cups: 370 },
    { date: "14.08", milk: 4, coffee: 2.5, cups: 340 }
  ];

  const savingsChart = [
    { category: "Волны закуп", amount: 28400 },
    { category: "Резерв соседей", amount: 12000 },
    { category: "ИИ Тендеры", amount: 5200 }
  ];

  const risks = bizItems
    .filter(i => i.status === 'critical' || i.status === 'low')
    .map(i => {
      const product = state.products.find(p => p.id === i.productId);
      const location = state.businesses.flatMap(b => b.locations || []).find(l => l.id === i.locationId);
      const days = product ? Math.round((i.currentStock / product.avgDailyUsage) * 10) / 10 : 0.5;
      return {
        productName: product?.name || 'Товар',
        locationName: location?.name || 'Точка',
        daysRemaining: days,
        recommendation: `Заказать ${product ? product.minStock * 4 : 40} ${product?.unit} у Almaty Milk или забрать из резерва Пекарни Нан (1.3 км)`
      };
    });

  const recentActivity = [
    { id: "act-1", icon: "📦", message: "Заказ #ord-001 — Almaty Milk, в пути", time: "2 часа назад" },
    { id: "act-2", icon: "⚠️", message: "Молоко 3.2% — критический остаток (4 л)", time: "4 часа назад" },
    { id: "act-3", icon: "🌊", message: "Волна закупа: 97/100 л собрано", time: "вчера" },
    { id: "act-4", icon: "✅", message: "Заказ #ord-002 — FoodLine KZ, доставлен", time: "2 дня назад" }
  ];

  return {
    success: true,
    kpis: {
      itemsAtRisk: atRisk,
      activeOrders,
      monthlySavings: state.valueMetrics.groupPurchaseSavings + state.valueMetrics.savedFromWriteoff,
      preventedStockouts: state.valueMetrics.preventedStockouts
    },
    inventoryChart,
    savingsChart,
    risks,
    recentActivity,
    isLive: false
  };
}

// 4. Run Reverse Tender
export async function runReverseTender(productId: string, quantity: number): Promise<AiTenderResult & { isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/tender`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId, quantity })
    });
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { ...data, isLive: true };
    }

    isBackendLive = true;
    return {
      success: false,
      offers: [],
      aiExplanation: await responseError(res, 'Не удалось запустить тендер'),
      isLive: true
    };
  } catch (e) {
    console.warn('[API Client] Backend offline, simulating tender locally');
  }

  isBackendLive = false;
  const state = getLocalState();
  const product = state.products.find(p => p.id === productId);
  const matchedSuppliers = state.suppliers.filter(s => s.products.includes(productId));

  const offers = matchedSuppliers.map((s, idx) => {
    const base = s.basePrice[productId] || 450;
    const pricePerUnit = Math.round(base * (idx === 0 ? 1.01 : idx === 1 ? 0.96 : 1.06));
    const totalPrice = pricePerUnit * quantity;
    const recType: 'best_balance' | 'cheapest' | 'fastest' =
      idx === 0 ? 'best_balance' : idx === 1 ? 'cheapest' : 'fastest';

    const reasons = {
      best_balance: `Лучший баланс цены и надёжности: высокая вероятность полной и своевременной поставки (${s.reliabilityScore}%).`,
      cheapest: `Минимальная цена за единицу (${pricePerUnit} ₸), но более долгий срок доставки (${s.avgDeliveryHours} ч).`,
      fastest: `Самая быстрая экспресс-доставка за ${s.avgDeliveryHours} часа. Высокая надёжность.`
    };

    return {
      id: `offer-${idx + 1}`,
      supplierId: s.id,
      supplierName: s.name,
      pricePerUnit,
      totalPrice,
      deliveryHours: s.avgDeliveryHours,
      reliabilityScore: s.reliabilityScore,
      recommendation: recType,
      recommendationReason: reasons[recType]
    };
  });

  return {
    success: true,
    offers,
    aiExplanation: `ИИ проанализировал 3 предложения для "${product?.name || 'Товара'}" (${quantity} ${product?.unit || 'ед'}). Рекомендуем Almaty Milk по балансу надёжности (96%) и скорости.`,
    isLive: false
  };
}

// 5. Waves
export async function getWaves(): Promise<{ success: boolean; waves: PurchaseWave[]; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/waves`);
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { success: true, waves: data.waves || [], isLive: true };
    }
  } catch (e) {
    console.warn('[API Client] Backend offline, fetching waves from local state');
  }

  isBackendLive = false;
  const state = getLocalState();
  return { success: true, waves: state.waves, isLive: false };
}

export async function joinWave(waveId: string, quantity: number, businessId = 'biz-001'): Promise<{ success: boolean; wave?: PurchaseWave; error?: string; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/waves`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'join', waveId, businessId, quantity })
    });
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { ...data, isLive: true };
    }

    isBackendLive = true;
    return {
      success: false,
      error: await responseError(res, 'Не удалось присоединиться к волне'),
      isLive: true
    };
  } catch (e) {
    console.warn('[API Client] Backend offline, updating wave locally');
  }

  isBackendLive = false;
  const state = getLocalState();
  const waveIndex = state.waves.findIndex(w => w.id === waveId);
  if (waveIndex !== -1) {
    const wave = state.waves[waveIndex];
    const participantIndex = wave.participants.findIndex(p => p.businessId === businessId);
    if (participantIndex !== -1) {
      wave.participants[participantIndex].confirmed = true;
      wave.participants[participantIndex].quantity = quantity;
    } else {
      wave.participants.push({
        businessId,
        businessName: "Арома Coffee",
        quantity,
        confirmed: true,
        savings: quantity * wave.savingsPerUnit
      });
    }

    wave.totalQuantity = wave.participants.reduce((sum, p) => sum + p.quantity, 0);
    if (wave.totalQuantity >= wave.targetQuantity) {
      wave.status = 'ready';
    }

    state.waves[waveIndex] = wave;
    saveLocalState(state);
    return { success: true, wave, isLive: false };
  }

  return { success: false, isLive: false };
}

// 6. Orders
export async function getOrders(businessId = 'biz-001'): Promise<{ success: boolean; orders: Order[]; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/orders?businessId=${businessId}`);
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { success: true, orders: data.orders || [], isLive: true };
    }
  } catch (e) {
    console.warn('[API Client] Backend offline, fetching orders from local state');
  }

  isBackendLive = false;
  const state = getLocalState();
  return { success: true, orders: state.orders, isLive: false };
}

export async function createOrder(payload: {
  businessId: string;
  supplierId: string;
  items: { productId: string; quantity: number }[];
  source: 'manual' | 'auto_order' | 'wave' | 'tender';
}): Promise<{ success: boolean; order?: Order; error?: string; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { ...data, isLive: true };
    }

    isBackendLive = true;
    return {
      success: false,
      error: await responseError(res, 'Не удалось создать заказ'),
      isLive: true
    };
  } catch (e) {
    console.warn('[API Client] Backend offline, creating order in local state');
  }

  isBackendLive = false;
  const state = getLocalState();
  const supplier = state.suppliers.find(s => s.id === payload.supplierId);

  const orderItems = payload.items.map(item => {
    const product = state.products.find(p => p.id === item.productId);
    const pricePerUnit = supplier?.basePrice[item.productId] || 450;
    return {
      productId: item.productId,
      productName: product?.name || 'Товар',
      quantity: item.quantity,
      pricePerUnit,
      total: pricePerUnit * item.quantity
    };
  });

  const totalAmount = orderItems.reduce((sum, i) => sum + i.total, 0);

  const newOrder: Order = {
    id: `ord-${Date.now()}`,
    businessId: payload.businessId,
    supplierId: payload.supplierId,
    supplierName: supplier?.name || 'Поставщик',
    items: orderItems,
    totalAmount,
    status: 'pending',
    source: payload.source,
    deliveryEvents: [
      { status: 'pending', timestamp: new Date().toISOString() },
      { status: 'confirmed', timestamp: new Date().toISOString(), note: 'Поставщик подтвердил получение в WhatsApp' }
    ],
    createdAt: new Date().toISOString(),
    estimatedDelivery: new Date(Date.now() + (supplier?.avgDeliveryHours || 24) * 3600 * 1000).toISOString()
  };

  state.orders.unshift(newOrder);
  saveLocalState(state);

  return { success: true, order: newOrder, isLive: false };
}

// 7. Suppliers
export async function getSuppliers(): Promise<{ success: boolean; suppliers: Supplier[]; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/suppliers`);
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { success: true, suppliers: data.suppliers || [], isLive: true };
    }
  } catch (e) {
    console.warn('[API Client] Backend offline, loading suppliers from local state');
  }

  isBackendLive = false;
  const state = getLocalState();
  return { success: true, suppliers: state.suppliers, isLive: false };
}

// 8. Rescue Transfers (Neighbor Surplus)
export async function getRescueTransfers(): Promise<{ success: boolean; transfers: RescueTransfer[]; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/rescue?businessId=biz-001`);
    if (res.ok) {
      const data = await res.json();
      isBackendLive = true;
      return { success: true, transfers: data.transfers || [], isLive: true };
    }
  } catch (e) {
    isBackendLive = false;
    console.warn('[API Client] Backend offline, loading rescue transfers from local state');
  }

  const state = getLocalState();
  return { success: true, transfers: state.rescueTransfers, isLive: false };
}

export async function requestRescueTransfer(transferId: string): Promise<{ success: boolean; error?: string; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/rescue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'accept', transferId })
    });
    if (res.ok) {
      isBackendLive = true;
      return { success: true, isLive: true };
    }

    isBackendLive = true;
    return {
      success: false,
      error: await responseError(res, 'Не удалось принять предложение'),
      isLive: true
    };
  } catch (e) {
    isBackendLive = false;
    console.warn('[API Client] Backend offline, accepting rescue transfer in local state');
  }

  const state = getLocalState();
  const idx = state.rescueTransfers.findIndex(t => t.id === transferId);
  if (idx !== -1) {
    state.rescueTransfers[idx].status = 'completed';
    saveLocalState(state);
    return { success: true, isLive: isBackendLive };
  }
  return { success: false, isLive: isBackendLive };
}

// 9. Reset Demo Data
export async function resetAllData(): Promise<{ success: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
    if (!res.ok) return { success: false };
  } catch {
    // Offline mode still resets its own local demo state.
  }
  if (typeof window !== 'undefined') {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
    localStorage.removeItem(LEGACY_LOCAL_STORAGE_KEY);
  }
  return { success: true };
}
