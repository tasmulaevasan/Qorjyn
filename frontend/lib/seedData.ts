import { QorjynAppState } from '@/types';

export const initialSeedData: QorjynAppState = {
  businesses: [
    {
      id: "biz-001",
      name: "Арома Coffee",
      type: "coffee",
      district: "Алмалинский",
      phone: "77011234567",
      contactName: "Айдар",
      logoEmoji: "☕",
      allowSurplusSharing: true,
      locations: [
        { id: "loc-001", businessId: "biz-001", name: "Абая", address: "ул. Абая 44, Алматы", coordinates: { lat: 43.2380, lng: 76.9450 } },
        { id: "loc-002", businessId: "biz-001", name: "Достык", address: "пр. Достык 89, Алматы", coordinates: { lat: 43.2360, lng: 76.9570 } },
        { id: "loc-003", businessId: "biz-001", name: "Розыбакиева", address: "ул. Розыбакиева 112, Алматы", coordinates: { lat: 43.2290, lng: 76.9280 } }
      ]
    },
    {
      id: "biz-002",
      name: "Пекарня Нан",
      type: "bakery",
      district: "Медеуский",
      phone: "77019876543",
      contactName: "Динара",
      logoEmoji: "🥐",
      allowSurplusSharing: true,
      locations: [
        { id: "loc-004", businessId: "biz-002", name: "Гоголя", address: "ул. Гоголя 78, Алматы", coordinates: { lat: 43.2565, lng: 76.9284 } },
        { id: "loc-005", businessId: "biz-002", name: "Тулебаева", address: "ул. Тулебаева 55, Алматы", coordinates: { lat: 43.2520, lng: 76.9350 } }
      ]
    },
    {
      id: "biz-003",
      name: "Мини-маркет Береке",
      type: "minimarket",
      district: "Бостандыкский",
      phone: "77015554433",
      contactName: "Кайрат",
      logoEmoji: "🛒",
      allowSurplusSharing: false,
      locations: [
        { id: "loc-006", businessId: "biz-003", name: "Аль-Фараби", address: "пр. Аль-Фараби 15, Алматы", coordinates: { lat: 43.2180, lng: 76.9280 } }
      ]
    }
  ],

  products: [
    { id: "prod-001", name: "Молоко 3.2%", category: "dairy", unit: "л", minStock: 10, avgDailyUsage: 6.5, shelfLifeDays: 5 },
    { id: "prod-002", name: "Кофе арабика (зерно)", category: "coffee", unit: "кг", minStock: 3, avgDailyUsage: 1.2, shelfLifeDays: 180 },
    { id: "prod-003", name: "Стаканы 250 мл", category: "packaging", unit: "шт", minStock: 100, avgDailyUsage: 45, shelfLifeDays: 365 },
    { id: "prod-004", name: "Сахар рафинад", category: "other", unit: "кг", minStock: 5, avgDailyUsage: 0.8, shelfLifeDays: 365 },
    { id: "prod-005", name: "Сливки 10%", category: "dairy", unit: "л", minStock: 5, avgDailyUsage: 2.0, shelfLifeDays: 7 },
    { id: "prod-006", name: "Сироп ваниль", category: "syrups", unit: "л", minStock: 2, avgDailyUsage: 0.3, shelfLifeDays: 180 },
    { id: "prod-007", name: "Сироп карамель", category: "syrups", unit: "л", minStock: 2, avgDailyUsage: 0.4, shelfLifeDays: 180 },
    { id: "prod-008", name: "Мука пшеничная в/с", category: "bakery", unit: "кг", minStock: 20, avgDailyUsage: 8, shelfLifeDays: 180 },
    { id: "prod-009", name: "Масло сливочное 82%", category: "dairy", unit: "кг", minStock: 3, avgDailyUsage: 1.5, shelfLifeDays: 14 },
    { id: "prod-010", name: "Крышки для стаканов", category: "packaging", unit: "шт", minStock: 100, avgDailyUsage: 45, shelfLifeDays: 365 },
    { id: "prod-011", name: "Салфетки бумажные", category: "packaging", unit: "шт", minStock: 200, avgDailyUsage: 60, shelfLifeDays: 365 },
    { id: "prod-012", name: "Чай зелёный (листовой)", category: "coffee", unit: "кг", minStock: 1, avgDailyUsage: 0.15, shelfLifeDays: 365 },
    { id: "prod-013", name: "Шоколад горький 70%", category: "bakery", unit: "кг", minStock: 2, avgDailyUsage: 0.5, shelfLifeDays: 180 },
    { id: "prod-014", name: "Яйца куриные С1", category: "bakery", unit: "шт", minStock: 30, avgDailyUsage: 10, shelfLifeDays: 25 },
    { id: "prod-015", name: "Дрожжи сухие", category: "bakery", unit: "кг", minStock: 0.5, avgDailyUsage: 0.1, shelfLifeDays: 365 }
  ],

  inventory: [
    { id: "inv-001", productId: "prod-001", locationId: "loc-001", currentStock: 4, lastUpdated: "2026-08-14T08:00:00Z", expiryDate: "2026-08-16T00:00:00Z", status: "critical" },
    { id: "inv-002", productId: "prod-002", locationId: "loc-001", currentStock: 2.5, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-003", productId: "prod-003", locationId: "loc-001", currentStock: 340, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-004", productId: "prod-005", locationId: "loc-001", currentStock: 3, lastUpdated: "2026-08-14T08:00:00Z", status: "low" },
    { id: "inv-005", productId: "prod-006", locationId: "loc-001", currentStock: 1.8, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-006", productId: "prod-004", locationId: "loc-001", currentStock: 7, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-007", productId: "prod-001", locationId: "loc-002", currentStock: 12, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-008", productId: "prod-002", locationId: "loc-002", currentStock: 4.0, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-009", productId: "prod-003", locationId: "loc-002", currentStock: 80, lastUpdated: "2026-08-14T08:00:00Z", status: "low" },
    { id: "inv-010", productId: "prod-008", locationId: "loc-004", currentStock: 35, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-011", productId: "prod-009", locationId: "loc-004", currentStock: 1.5, lastUpdated: "2026-08-14T08:00:00Z", status: "low" },
    { id: "inv-012", productId: "prod-001", locationId: "loc-004", currentStock: 25, lastUpdated: "2026-08-14T08:00:00Z", status: "surplus" },
    { id: "inv-013", productId: "prod-014", locationId: "loc-004", currentStock: 60, lastUpdated: "2026-08-14T08:00:00Z", status: "ok" },
    { id: "inv-014", productId: "prod-001", locationId: "loc-006", currentStock: 40, lastUpdated: "2026-08-14T08:00:00Z", status: "surplus" },
    { id: "inv-015", productId: "prod-004", locationId: "loc-006", currentStock: 2, lastUpdated: "2026-08-14T08:00:00Z", status: "low" }
  ],

  inventoryEvents: [
    { id: "evt-001", productId: "prod-001", locationId: "loc-001", type: "receipt", quantity: 20, source: "manual", timestamp: "2026-08-08T09:00:00Z" },
    { id: "evt-002", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -7, source: "manual", timestamp: "2026-08-08T18:00:00Z" },
    { id: "evt-003", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -6, source: "manual", timestamp: "2026-08-09T18:00:00Z" },
    { id: "evt-004", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -5, source: "manual", timestamp: "2026-08-10T18:00:00Z" },
    { id: "evt-005", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -8, source: "manual", note: "Выходной, больше посетителей", timestamp: "2026-08-11T18:00:00Z" },
    { id: "evt-006", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -9, source: "manual", note: "Выходной", timestamp: "2026-08-12T18:00:00Z" },
    { id: "evt-007", productId: "prod-001", locationId: "loc-001", type: "receipt", quantity: 15, source: "auto_order", timestamp: "2026-08-13T10:00:00Z" },
    { id: "evt-008", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -7, source: "manual", timestamp: "2026-08-13T18:00:00Z" },
    { id: "evt-009", productId: "prod-001", locationId: "loc-001", type: "sale", quantity: -4, source: "manual", timestamp: "2026-08-14T12:00:00Z" }
  ],

  suppliers: [
    {
      id: "sup-001", name: "Almaty Milk", phone: "77071001010",
      products: ["prod-001", "prod-005", "prod-009"],
      basePrice: { "prod-001": 450, "prod-005": 680, "prod-009": 2800 },
      minOrder: 5000, avgDeliveryHours: 24,
      reliabilityScore: 96, totalOrders: 48, onTimeDeliveries: 46, shortDeliveries: 1, isActive: true
    },
    {
      id: "sup-002", name: "FoodLine KZ", phone: "77072002020",
      products: ["prod-001", "prod-004", "prod-005", "prod-008", "prod-014"],
      basePrice: { "prod-001": 420, "prod-004": 380, "prod-005": 650, "prod-008": 290, "prod-014": 45 },
      minOrder: 10000, avgDeliveryHours: 72,
      reliabilityScore: 81, totalOrders: 30, onTimeDeliveries: 24, shortDeliveries: 4, isActive: true
    },
    {
      id: "sup-003", name: "Express Dairy", phone: "77073003030",
      products: ["prod-001", "prod-005", "prod-009"],
      basePrice: { "prod-001": 480, "prod-005": 720, "prod-009": 3000 },
      minOrder: 3000, avgDeliveryHours: 4,
      reliabilityScore: 91, totalOrders: 15, onTimeDeliveries: 14, shortDeliveries: 0, isActive: true
    }
  ],

  waves: [
    {
      id: "wave-001",
      productId: "prod-001", productName: "Молоко 3.2%",
      status: "collecting",
      participants: [
        { businessId: "biz-001", businessName: "Арома Coffee", quantity: 22, confirmed: true, savings: 660 },
        { businessId: "biz-002", businessName: "Пекарня Нан", quantity: 40, confirmed: true, savings: 1200 },
        { businessId: "biz-003", businessName: "Мини-маркет Береке", quantity: 35, confirmed: false, savings: 1050 }
      ],
      totalQuantity: 97, targetQuantity: 100,
      individualPrice: 450, groupPrice: 420, savingsPerUnit: 30,
      deadline: "2026-08-15T18:00:00Z",
      createdAt: "2026-08-13T10:00:00Z"
    }
  ],

  orders: [
    {
      id: "ord-001", businessId: "biz-001", supplierId: "sup-001", supplierName: "Almaty Milk",
      items: [{ productId: "prod-001", productName: "Молоко 3.2%", quantity: 20, pricePerUnit: 450, total: 9000 }],
      totalAmount: 9000, status: "in_transit", source: "manual",
      deliveryEvents: [
        { status: "pending", timestamp: "2026-08-13T14:00:00Z" },
        { status: "confirmed", timestamp: "2026-08-13T14:30:00Z", note: "Поставщик подтвердил" },
        { status: "preparing", timestamp: "2026-08-13T16:00:00Z" },
        { status: "in_transit", timestamp: "2026-08-14T08:00:00Z", note: "Курьер выехал" }
      ],
      createdAt: "2026-08-13T14:00:00Z", estimatedDelivery: "2026-08-14T14:00:00Z"
    },
    {
      id: "ord-002", businessId: "biz-002", supplierId: "sup-002", supplierName: "FoodLine KZ",
      items: [
        { productId: "prod-008", productName: "Мука пшеничная в/с", quantity: 50, pricePerUnit: 290, total: 14500 },
        { productId: "prod-014", productName: "Яйца куриные С1", quantity: 120, pricePerUnit: 45, total: 5400 }
      ],
      totalAmount: 19900, status: "delivered", source: "manual",
      deliveryEvents: [
        { status: "pending", timestamp: "2026-08-11T10:00:00Z" },
        { status: "confirmed", timestamp: "2026-08-11T11:00:00Z" },
        { status: "delivered", timestamp: "2026-08-12T16:00:00Z", note: "Получено полностью" }
      ],
      createdAt: "2026-08-11T10:00:00Z"
    }
  ],

  rescueTransfers: [
    {
      id: "rescue-001",
      fromBusinessId: "biz-002", fromBusinessName: "Пекарня Нан",
      toBusinessId: "biz-001", toBusinessName: "Арома Coffee",
      productId: "prod-001", productName: "Молоко 3.2%",
      quantity: 15, distanceKm: 1.3,
      pricePerUnit: 400, status: "proposed",
      expiryDate: "2026-08-16T00:00:00Z",
      createdAt: "2026-08-14T09:00:00Z"
    }
  ],

  forecasts: [
    {
      id: "fc-001", productId: "prod-001", locationId: "loc-001",
      daysUntilStockout: 0.6,
      recommendedOrderQty: 42,
      explanation: "Молока хватит на 0.6 дня (4 л при расходе 6.5 л/день). В выходные ожидается повышенный расход (+40%). Рекомендуем пополнить 42 литра сегодня.",
      factors: [
        { name: "Базовый расход", impact: 0, description: "6.5 л/день в будни" },
        { name: "Выходные", impact: 40, description: "В субботу-воскресенье расход выше на 40%" },
        { name: "Сезон", impact: -5, description: "Лето, горячие напитки чуть менее популярны" }
      ],
      dailyForecast: [
        { date: "2026-08-14", dayOfWeek: "Чт", predictedUsage: 6.5, predictedStock: 4, isWeekend: false },
        { date: "2026-08-15", dayOfWeek: "Пт", predictedUsage: 7.0, predictedStock: -3, isWeekend: false },
        { date: "2026-08-16", dayOfWeek: "Сб", predictedUsage: 9.1, predictedStock: -12.1, isWeekend: true },
        { date: "2026-08-17", dayOfWeek: "Вс", predictedUsage: 9.1, predictedStock: -21.2, isWeekend: true },
        { date: "2026-08-18", dayOfWeek: "Пн", predictedUsage: 6.5, predictedStock: -27.7, isWeekend: false },
        { date: "2026-08-19", dayOfWeek: "Вт", predictedUsage: 6.5, predictedStock: -34.2, isWeekend: false },
        { date: "2026-08-20", dayOfWeek: "Ср", predictedUsage: 6.5, predictedStock: -40.7, isWeekend: false }
      ],
      generatedAt: "2026-08-14T08:00:00Z"
    }
  ],

  valueMetrics: {
    preventedStockouts: 12,
    savedFromWriteoff: 45600,
    groupPurchaseSavings: 28400,
    reducedFrozenCapital: 67000,
    onTimeDeliveryRate: 94,
    avgDeficitResolutionHours: 4.2,
    automatedOperations: 34
  }
};
