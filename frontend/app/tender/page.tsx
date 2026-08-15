'use client';

import React, { useState } from 'react';
import { runReverseTender, createOrder } from '@/lib/api';
import { TenderOffer } from '@/types';
import {
  Zap,
  Sparkles,
  Loader2,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Award,
  TrendingDown,
  MessageSquare,
  ArrowRight
} from 'lucide-react';

export default function TenderPage() {
  const [selectedProduct, setSelectedProduct] = useState<string>('prod-001');
  const [quantity, setQuantity] = useState<number>(50);
  const [isCalculating, setIsCalculating] = useState<boolean>(false);
  const [tenderResult, setTenderResult] = useState<{
    offers: TenderOffer[];
    aiExplanation: string;
  } | null>(null);
  const [orderedOfferId, setOrderedOfferId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleRunTender = async () => {
    setIsCalculating(true);
    setTenderResult(null);
    setOrderedOfferId(null);
    setErrorMessage(null);

    const res = await runReverseTender(selectedProduct, quantity);
    setIsCalculating(false);
    if (res.success) {
      setTenderResult({
        offers: res.offers,
        aiExplanation: res.aiExplanation
      });
    } else {
      setErrorMessage(res.aiExplanation || 'Не удалось запустить тендер');
    }
  };

  const handleSelectOffer = async (offer: TenderOffer) => {
    setErrorMessage(null);
    const res = await createOrder({
      businessId: 'biz-001',
      supplierId: offer.supplierId,
      items: [{ productId: selectedProduct, quantity }],
      source: 'tender'
    });
    if (res.success) {
      setOrderedOfferId(offer.id);
    } else {
      setErrorMessage(res.error || 'Не удалось создать заказ');
    }
  };

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'best_balance':
        return (
          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold flex items-center space-x-1">
            <Award className="w-3.5 h-3.5" />
            <span>ЛУЧШИЙ БАЛАНС</span>
          </span>
        );
      case 'cheapest':
        return (
          <span className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-bold flex items-center space-x-1">
            <TrendingDown className="w-3.5 h-3.5" />
            <span>САМЫЙ ДЕШЕВЫЙ</span>
          </span>
        );
      case 'fastest':
        return (
          <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-bold flex items-center space-x-1">
            <Clock className="w-3.5 h-3.5" />
            <span>ЭКСПРЕСС (4 ЧАСА)</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-1">
          <Zap className="w-4 h-4" />
          <span>Обратный ИИ-Аукцион Снабжения</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white">Тендер Поставщиков за 2 Секунды</h1>
        <p className="text-xs text-slate-400 mt-1">
          Запросите лучшую цену на товар — ИИ сопоставит предложения 3 оптовиков Алматы с учётом истории надежности.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm font-bold">
          {errorMessage}
        </div>
      )}

      {/* Tender Generator Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl backdrop-blur-md">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-2">Выберите товар</label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white font-semibold focus:outline-none focus:border-emerald-500"
            >
              <option value="prod-001">Молоко 3.2% (л)</option>
              <option value="prod-002">Кофе арабика зерно (кг)</option>
              <option value="prod-003">Стаканы 250 мл (шт)</option>
              <option value="prod-005">Сливки 10% (л)</option>
              <option value="prod-008">Мука пшеничная в/с (кг)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase mb-2">Требуемый объем</label>
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              min={5}
              max={1000}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white font-extrabold focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <button
              onClick={handleRunTender}
              disabled={isCalculating}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-sm shadow-xl shadow-emerald-600/30 flex items-center justify-center space-x-2 transition-all"
            >
              {isCalculating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-amber-300" />
                  <span>ИИ Анализирует рынки...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Запросить ИИ-Тендер</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Loading Animation State */}
      {isCalculating && (
        <div className="py-16 bg-slate-900/60 border border-slate-800 rounded-3xl text-center space-y-3">
          <Loader2 className="w-10 h-10 text-emerald-400 animate-spin mx-auto" />
          <h3 className="text-base font-bold text-white">ИИ Сопоставляет предложения 3 оптовиков...</h3>
          <p className="text-xs text-slate-400">Расчет весовых коэффициентов: Цена (40%) + Надежность (40%) + Доставка (20%)</p>
        </div>
      )}

      {/* Results Comparison Grid */}
      {tenderResult && (
        <div className="space-y-6">
          {/* AI Explanation Banner */}
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-xs leading-relaxed flex items-start space-x-3">
            <Sparkles className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white block mb-1">Заключение ИИ-Ассистента QORJYN:</span>
              <span>{tenderResult.aiExplanation}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {tenderResult.offers.map(offer => {
              const isOrdered = orderedOfferId === offer.id;

              return (
                <div
                  key={offer.id}
                  className={`bg-slate-900/90 border rounded-3xl p-6 shadow-xl flex flex-col justify-between transition-all ${
                    offer.recommendation === 'best_balance'
                      ? 'border-emerald-500/50 bg-gradient-to-b from-emerald-950/20 to-slate-900 shadow-emerald-500/10'
                      : 'border-slate-800'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      {getRecommendationBadge(offer.recommendation)}
                      <div className="flex items-center space-x-1 text-xs font-bold text-slate-300">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        <span>{offer.reliabilityScore}%</span>
                      </div>
                    </div>

                    <h3 className="text-lg font-black text-white mb-1">{offer.supplierName}</h3>
                    <div className="text-2xl font-black text-emerald-400 mb-4">
                      {offer.pricePerUnit} ₸ <span className="text-xs font-normal text-slate-400">/ ед</span>
                    </div>

                    <div className="space-y-2 text-xs text-slate-300 mb-6 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Итого за {quantity} ед:</span>
                        <span className="font-bold text-white">{offer.totalPrice.toLocaleString()} ₸</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Срок доставки:</span>
                        <span className="font-bold text-white">{offer.deliveryHours} ч</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-400 leading-relaxed mb-6">
                      {offer.recommendationReason}
                    </p>
                  </div>

                  <button
                    onClick={() => handleSelectOffer(offer)}
                    disabled={isOrdered}
                    className={`w-full py-3 rounded-xl font-bold text-xs flex items-center justify-center space-x-2 transition-all ${
                      isOrdered
                        ? 'bg-emerald-500 text-slate-950 font-black'
                        : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20'
                    }`}
                  >
                    {isOrdered ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Заказ оформлен в WhatsApp!</span>
                      </>
                    ) : (
                      <>
                        <MessageSquare className="w-4 h-4" />
                        <span>Выбрать & Заказать</span>
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
