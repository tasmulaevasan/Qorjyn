'use client';

import React, { useEffect, useState } from 'react';
import { getInventory, updateInventoryItem } from '@/lib/api';
import { InventoryItem } from '@/types';
import { AiSimulatorModal } from '@/components/AiSimulatorModal';
import {
  Boxes,
  Sparkles,
  Plus,
  Minus,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Filter,
  RefreshCw,
  Camera,
  Mic,
  Zap
} from 'lucide-react';

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAiModalOpen, setIsAiModalOpen] = useState<boolean>(false);
  const [alertMessage, setAlertMessage] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    const res = await getInventory({
      status: filterStatus === 'all' ? undefined : filterStatus
    });
    setItems(res.inventory || []);
    setIsLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [filterStatus]);

  const handleStockAdjust = async (item: InventoryItem, delta: number) => {
    const res = await updateInventoryItem({
      productId: item.productId,
      locationId: item.locationId,
      delta,
      source: 'manual',
      note: 'Ручная корректировка остатка кассиром'
    });

    if (res.alert) {
      setAlertMessage(res.alert.message);
      setTimeout(() => setAlertMessage(null), 4000);
    } else if (!res.success) {
      setAlertMessage(res.error || 'Не удалось обновить остаток');
      setTimeout(() => setAlertMessage(null), 4000);
    }
    await loadData();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'critical':
        return (
          <span className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-400 border border-red-500/30 text-xs font-bold flex items-center space-x-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>КРИТИЧЕСКИЙ</span>
          </span>
        );
      case 'low':
        return (
          <span className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-bold flex items-center space-x-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>МАЛО</span>
          </span>
        );
      case 'surplus':
        return (
          <span className="px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-bold flex items-center space-x-1">
            <span>ИЗБЫТОК</span>
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold flex items-center space-x-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>В НОРМЕ</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Alert Notification Toast */}
      {alertMessage && (
        <div className="p-4 rounded-2xl bg-amber-500/20 border border-amber-500/40 text-amber-300 text-sm font-bold flex items-center space-x-3 shadow-xl animate-bounce">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
          <span>{alertMessage}</span>
        </div>
      )}

      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">
            <Boxes className="w-4 h-4" />
            <span>Складской Учет Точки Абая</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white">Остатки Товаров & ИИ-Ввод</h1>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsAiModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-xs shadow-lg shadow-emerald-600/30 flex items-center space-x-2 transition-all"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>ИИ-Ввод (Фото / Голос)</span>
          </button>

          <button
            onClick={loadData}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            title="Обновить"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {[
          { key: 'all', label: 'Все товары' },
          { key: 'critical', label: 'Критические 🔴' },
          { key: 'low', label: 'Мало 🟡' },
          { key: 'ok', label: 'В норме 🟢' },
          { key: 'surplus', label: 'Избыток 🔵' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setFilterStatus(tab.key)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
              filterStatus === tab.key
                ? 'bg-slate-800 text-white border border-slate-700 shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Table of Inventory Items */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase font-bold text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-4 px-6">Наименование товара</th>
                <th className="py-4 px-6">Категория</th>
                <th className="py-4 px-6">Текущий остаток</th>
                <th className="py-4 px-6">Хватит на</th>
                <th className="py-4 px-6">Статус</th>
                <th className="py-4 px-6 text-right">Быстрый учет</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500 font-medium">
                    Нет товаров по выбранному фильтру
                  </td>
                </tr>
              ) : (
                items.map(item => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-6">
                      <div className="font-extrabold text-white text-sm">{item.product?.name || 'Товар'}</div>
                      <div className="text-[11px] text-slate-500">Мин. порог: {item.product?.minStock} {item.product?.unit}</div>
                    </td>
                    <td className="py-4 px-6">
                      <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 font-medium border border-slate-700">
                        {item.product?.category}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <div className="text-base font-black text-white">
                        {item.currentStock} <span className="text-xs font-normal text-slate-400">{item.product?.unit}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-1.5 text-slate-300 font-semibold">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>~{item.daysRemaining} дн.</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">{getStatusBadge(item.status)}</td>
                    <td className="py-4 px-6 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => handleStockAdjust(item, -1)}
                          className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center justify-center font-bold border border-slate-700"
                          title="Списать 1"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleStockAdjust(item, 1)}
                          className="w-8 h-8 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 flex items-center justify-center font-bold border border-emerald-500/30"
                          title="Пополнить 1"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Modal */}
      <AiSimulatorModal
        isOpen={isAiModalOpen}
        onClose={() => setIsAiModalOpen(false)}
        onSuccess={loadData}
      />
    </div>
  );
}
