// ============ QORJYN DATA MODELS ============

export interface Location {
  id: string;
  businessId: string;
  name: string;
  address: string;
  coordinates: { lat: number; lng: number };
}

export interface Business {
  id: string;
  name: string;
  type: string; // 'coffee' | 'bakery' | 'minimarket'
  category?: string;
  district: string;
  phone: string;
  contactName: string;
  logoEmoji: string;
  allowSurplusSharing: boolean;
  locations: Location[];
  avgCheck?: number;
  description?: string;
  logoUrl?: string;
  address?: string;
}

export interface Product {
  id: string;
  name: string;
  category: 'dairy' | 'coffee' | 'packaging' | 'bakery' | 'syrups' | 'other';
  unit: string;
  minStock: number;
  avgDailyUsage: number;
  shelfLifeDays: number;
}

export interface InventoryItem {
  id: string;
  productId: string;
  locationId: string;
  currentStock: number;
  lastUpdated: string;
  expiryDate?: string;
  status: 'ok' | 'low' | 'critical' | 'surplus';
  product?: Product;
  location?: Location;
  daysRemaining?: number;
}

export interface InventoryEvent {
  id: string;
  productId: string;
  locationId: string;
  type: 'receipt' | 'sale' | 'writeoff' | 'transfer_in' | 'transfer_out' | 'adjustment';
  quantity: number;
  source: 'whatsapp' | 'manual' | 'auto_order' | 'rescue';
  note?: string;
  timestamp: string;
}

export interface Supplier {
  id: string;
  name: string;
  phone: string;
  products: string[];
  basePrice: Record<string, number>;
  minOrder: number;
  avgDeliveryHours: number;
  reliabilityScore: number;
  totalOrders: number;
  onTimeDeliveries: number;
  shortDeliveries: number;
  isActive: boolean;
}

export interface WaveParticipant {
  businessId: string;
  businessName: string;
  quantity: number;
  confirmed: boolean;
  savings: number;
}

export interface PurchaseWave {
  id: string;
  productId: string;
  productName: string;
  status: 'collecting' | 'ready' | 'ordered' | 'delivered' | 'cancelled';
  participants: WaveParticipant[];
  totalQuantity: number;
  targetQuantity: number;
  individualPrice: number;
  groupPrice: number;
  savingsPerUnit: number;
  deadline: string;
  createdAt: string;
}

export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  pricePerUnit: number;
  total: number;
}

export interface DeliveryEvent {
  status: string;
  timestamp: string;
  note?: string;
}

export interface Order {
  id: string;
  businessId: string;
  supplierId: string;
  supplierName: string;
  items: OrderItem[];
  totalAmount: number;
  status: 'pending' | 'confirmed' | 'preparing' | 'in_transit' | 'delivered' | 'issue';
  source: 'manual' | 'auto_order' | 'wave' | 'tender';
  waveId?: string;
  deliveryEvents: DeliveryEvent[];
  createdAt: string;
  estimatedDelivery?: string;
}

export interface RescueTransfer {
  id: string;
  fromBusinessId: string;
  fromBusinessName: string;
  toBusinessId: string;
  toBusinessName: string;
  productId: string;
  productName: string;
  quantity: number;
  distanceKm: number;
  pricePerUnit?: number;
  status: 'proposed' | 'accepted' | 'completed' | 'declined';
  expiryDate?: string;
  createdAt: string;
}

export interface ValueMetrics {
  preventedStockouts: number;
  savedFromWriteoff: number;
  groupPurchaseSavings: number;
  reducedFrozenCapital: number;
  onTimeDeliveryRate: number;
  avgDeficitResolutionHours: number;
  automatedOperations: number;
}

export interface TenderOffer {
  id: string;
  supplierId: string;
  supplierName: string;
  pricePerUnit: number;
  totalPrice: number;
  deliveryHours: number;
  reliabilityScore: number;
  recommendation: 'best_balance' | 'cheapest' | 'fastest';
  recommendationReason: string;
}

export interface AiTenderResult {
  success: boolean;
  offers: TenderOffer[];
  aiExplanation: string;
}

export interface ForecastFactor {
  name: string;
  impact: number;
  description: string;
}

export interface DailyForecast {
  date: string;
  dayOfWeek: string;
  predictedUsage: number;
  predictedStock: number;
  isWeekend: boolean;
}

export interface InventoryForecast {
  id: string;
  productId: string;
  locationId: string;
  daysUntilStockout: number;
  recommendedOrderQty: number;
  explanation: string;
  factors: ForecastFactor[];
  dailyForecast: DailyForecast[];
  generatedAt: string;
}

// Global App State
export interface QorjynAppState {
  businesses: Business[];
  products: Product[];
  inventory: InventoryItem[];
  inventoryEvents: InventoryEvent[];
  suppliers: Supplier[];
  waves: PurchaseWave[];
  orders: Order[];
  rescueTransfers: RescueTransfer[];
  forecasts: InventoryForecast[];
  valueMetrics: ValueMetrics;
}
