# 🤝 QORJYN Mesh — Multi-Agent Coordination Hub

Welcome! This repository contains the complete **QORJYN Mesh** B2B collective supply chain platform.

- **Frontend:** Next.js 14 (App Router), Tailwind CSS, Recharts, Lucide Icons. Located in the root directory.
- **Backend Specs & Contract:** Detailed API specification and seed data structure for Django backend.

---

## 🚀 Quick Start for Frontend

```bash
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

---

## 📡 API Contract with Backend

The frontend automatically connects to the backend at `http://localhost:4000/api` (or custom URL specified in `NEXT_PUBLIC_API_URL`).

### Key Endpoints Expected:

1. `GET /api/inventory` — Returns list of inventory items with joined product & location data.
2. `POST /api/inventory` — Updates item quantity (`productId`, `locationId`, `delta`).
3. `GET /api/dashboard?businessId=biz-001` — Returns KPIs, 7-day usage trends, and risk warnings.
4. `POST /api/tender` — Generates 3 supplier offers ("Best Balance", "Cheapest", "Fastest") with 2s AI delay.
5. `GET /api/waves` & `POST /api/waves` — Returns active collective purchasing waves & allows joining.
6. `GET /api/orders` & `POST /api/orders` — Orders tracking and creation.
7. `GET /api/suppliers` — Supplier reliability ratings.
8. `POST /api/webhook/greenapi` — WhatsApp incoming webhook handler for text, photo (receipt scan), and voice notes.

---

## 🔄 Standalone Offline Mode

If the backend is not running, the frontend seamlessly operates in **Standalone Mode** using local storage and rich seed data, allowing immediate testing and demonstration!
