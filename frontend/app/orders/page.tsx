'use client';

import React, { useEffect, useState } from 'react';
import { getOrders, getSuppliers } from '@/lib/api';
import { Order, Supplier } from '@/types';
import {
  Truck,
  CheckCircle2,
  Clock,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  PackageCheck,
  Building2
} from 'lucide-react';

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadData = async () => {
    setIsLoading(true);
    const [ordRes, supRes] = await Promise.all([getOrders(), getSuppliers()]);
    setOrders(ordRes.orders || []);
    setSuppliers(supRes.suppliers || []);
    setIsLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const getOrderStatusBadge = (status: string) => {
    switch (status) {
      case 'in_transit':
        return (
          <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-bold flex items-center space-x-1">
            <Truck className="w-3.5 h-3.5 animate-pulse" />
            <span>В ПУТИ (КУРЬЕР)</span>
          </span>
        );
      case 'delivered':
        return (
          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>ДОСТАВЛЕН</span>
          </span>
        );
      case 'confirmed':
        return (
          <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold flex items-center space-x-1">
            <Clock className="w-3.5 h-3.5" />
            <span>ПОДТВЕРЖДЕН</span>
          </span>
        );
      default:
        return (
          <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700 text-xs font-bold">
            ОФОРМЛЯЕТСЯ
          </span>
        );
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">
            <Truck className="w-4 h-4" />
            <span>Трекинг Заказов & Рейтинг Поставщиков</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white">Мониторинг Снабжения</h1>
        </div>

        <button
          onClick={loadData}
          className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Orders List */}
      <div className="space-y-4">
        <h2 className="text-lg font-extrabold text-white">Активные & Завершенные Заказы</h2>

        <div className="space-y-4">
          {orders.map(order => (
            <div
              key={order.id}
              className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl backdrop-blur-md space-y-4"
            >
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <span className="text-base font-black text-white">{order.supplierName}</span>
                    <span className="text-xs text-slate-500 font-mono">#{order.id}</span>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Источник: <span className="font-semibold text-slate-200 uppercase">{order.source}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-base font-black text-emerald-400">{order.totalAmount.toLocaleString()} ₸</div>
                    <div className="text-[11px] text-slate-500">Сумма заказа</div>
                  </div>
                  {getOrderStatusBadge(order.status)}
                </div>
              </div>

              {/* Order Items */}
              <div className="space-y-2">
                {order.items.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center text-xs p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                    <span className="font-extrabold text-slate-200">{item.productName}</span>
                    <span className="text-slate-400">
                      {item.quantity} ед × {item.pricePerUnit} ₸ = <strong className="text-white">{item.total.toLocaleString()} ₸</strong>
                    </span>
                  </div>
                ))}
              </div>

              {/* Timeline Delivery Events */}
              <div className="pt-2">
                <div className="text-[11px] font-bold text-slate-400 uppercase mb-2">История статусов:</div>
                <div className="flex flex-wrap gap-2">
                  {order.deliveryEvents.map((evt, idx) => (
                    <span key={idx} className="px-3 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-[11px] text-slate-300">
                      ✅ {evt.status}: {evt.note || 'ОК'}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Supplier Reliability Scorecard */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
        <h2 className="text-lg font-extrabold text-white flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <span>Рейтинг Надёжности Поставщиков Алматы</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {suppliers.map(sup => (
            <div key={sup.id} className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-extrabold text-white text-base">{sup.name}</h3>
                  <p className="text-xs text-slate-400">Тел: {sup.phone}</p>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-black text-xs border border-emerald-500/30">
                  {sup.reliabilityScore}%
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-300 pt-2 border-t border-slate-800">
                <div className="flex justify-between">
                  <span className="text-slate-400">Всего заказов:</span>
                  <span className="font-bold text-white">{sup.totalOrders}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Вовремя:</span>
                  <span className="font-bold text-emerald-400">{sup.onTimeDeliveries}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Сбои / недовозы:</span>
                  <span className="font-bold text-amber-400">{sup.shortDeliveries}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
