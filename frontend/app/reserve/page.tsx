'use client';

import React, { useEffect, useState } from 'react';
import { getRescueTransfers, requestRescueTransfer } from '@/lib/api';
import { RescueTransfer } from '@/types';
import { InteractiveMap } from '@/components/InteractiveMap';
import {
  MapPin,
  Sparkles,
  CheckCircle2,
  Clock,
  ShieldAlert,
  ArrowRight,
  Store
} from 'lucide-react';

export default function ReservePage() {
  const [transfers, setTransfers] = useState<RescueTransfer[]>([]);
  const [requestedId, setRequestedId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async () => {
    const res = await getRescueTransfers();
    setTransfers(res.transfers || []);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRequestRescue = async (id: string) => {
    setErrorMessage(null);
    const res = await requestRescueTransfer(id);
    if (res.success) {
      setRequestedId(id);
      await loadData();
    } else {
      setErrorMessage(res.error || 'Не удалось отправить запрос');
    }
  };

  const formatExpiryDate = (value?: string) => {
    if (!value) return 'не указан';
    const date = new Date(value);
    return Number.isNaN(date.getTime())
      ? value
      : new Intl.DateTimeFormat('ru-RU').format(date);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-1">
          <MapPin className="w-4 h-4" />
          <span>Соседский Резерв & Перехват Излишек</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white">Взаимовыручка Заведений Рядом</h1>
        <p className="text-xs text-slate-400 mt-1">
          Перехватывайте товары у соседей за 15 минут со скидкой или спасайте свои излишки от списания.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm font-bold">
          {errorMessage}
        </div>
      )}

      {/* Neighbor Rescue Offers List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {transfers.map(t => {
          const isAccepted = t.status === 'accepted' || t.status === 'completed' || requestedId === t.id;

          return (
            <div
              key={t.id}
              className="bg-slate-900/90 border border-amber-500/30 rounded-3xl p-6 shadow-xl backdrop-blur-md relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold uppercase flex items-center space-x-1">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>ИЗЛИШЕК У СОСЕДА</span>
                </span>
                <span className="text-xs font-bold text-slate-400 flex items-center space-x-1">
                  <MapPin className="w-3.5 h-3.5 text-amber-400" />
                  <span>{t.distanceKm} км от вас</span>
                </span>
              </div>

              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-xl font-bold">
                  🥐
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-white">{t.fromBusinessName}</h3>
                  <p className="text-xs text-slate-400">Предлагает: {t.productName} ({t.quantity} ед)</p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs text-slate-300 mb-6">
                <div className="flex justify-between">
                  <span className="text-slate-400">Цена со скидкой:</span>
                  <span className="font-bold text-emerald-400 text-sm">{t.pricePerUnit} ₸ / ед (-12%)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Срок годности до:</span>
                  <span className="font-bold text-slate-200">{formatExpiryDate(t.expiryDate)}</span>
                </div>
              </div>

              <button
                onClick={() => handleRequestRescue(t.id)}
                disabled={isAccepted}
                className={`w-full py-3 rounded-xl font-bold text-xs flex items-center justify-center space-x-2 transition-all ${
                  isAccepted
                    ? 'bg-emerald-500 text-slate-950 font-black'
                    : 'bg-gradient-to-r from-amber-600 to-emerald-600 hover:from-amber-500 hover:to-emerald-500 text-white shadow-lg shadow-amber-600/20'
                }`}
              >
                {isAccepted ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Запрос отправлен! Курьер выехал</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-amber-200" />
                    <span>Запросить взаимовыручку ({t.quantity * (t.pricePerUnit || 400)} ₸)</span>
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Map Section */}
      <InteractiveMap />
    </div>
  );
}
