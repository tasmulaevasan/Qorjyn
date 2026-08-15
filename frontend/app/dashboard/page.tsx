'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { getDashboard } from '@/lib/api';
import { InventoryTrendChart, SavingsBarChart } from '@/components/RechartsWrapper';
import {
  AlertTriangle,
  TrendingUp,
  ShieldCheck,
  PackageCheck,
  Zap,
  ArrowRight,
  Clock,
  Sparkles,
  RefreshCw
} from 'lucide-react';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    const res = await getDashboard();
    setData(res);
    setIsLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  if (isLoading || !data) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-center">
        <RefreshCw className="w-10 h-10 text-emerald-400 animate-spin mb-4" />
        <h3 className="text-base font-bold text-white">Загрузка аналитики QORJYN...</h3>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header Title */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Кабинет Управления Запасами</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white">Аналитика & Прогнозирование Рисков</h1>
        </div>
        <button
          onClick={loadData}
          className="flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Обновить данные</span>
        </button>
      </div>

      {/* 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-amber-500/30 rounded-2xl p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase">Под риском дефицита</span>
            <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white">{data.kpis.itemsAtRisk} позиции</div>
          <p className="text-xs text-amber-400 mt-1 flex items-center space-x-1">
            <span>Молоко 3.2% и Сливки 10%</span>
          </p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase">Заказы в пути</span>
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <PackageCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white">{data.kpis.activeOrders} заказ</div>
          <p className="text-xs text-cyan-400 mt-1">Almaty Milk (доставка сегодня к 14:00)</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase">Сэкономлено в сети</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white">{data.kpis.monthlySavings.toLocaleString()} ₸</div>
          <p className="text-xs text-emerald-400 mt-1">За счет волн и соседского резерва</p>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-400 uppercase">Предотвращено дефицитов</span>
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-black text-white">{data.kpis.preventedStockouts} стопа</div>
          <p className="text-xs text-purple-400 mt-1">Сохранена выручка ~180 000 ₸</p>
        </div>
      </div>

      {/* AI Risk Recommendation Widget */}
      {data.risks && data.risks.length > 0 && (
        <div className="bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 border border-amber-500/40 rounded-3xl p-6 shadow-xl relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
                <Zap className="w-4 h-4" />
                <span>ИИ-ПРЕДУПРЕЖДЕНИЕ О ДЕФИЦИТЕ</span>
              </div>
              <h3 className="text-lg font-extrabold text-white">
                {data.risks[0].productName} — Осталось на {data.risks[0].daysRemaining} дня
              </h3>
              <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                {data.risks[0].recommendation}
              </p>
            </div>
            <div className="flex items-center space-x-3 shrink-0">
              <Link
                href="/tender?productId=prod-001"
                className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs shadow-md shadow-amber-500/20 transition-all flex items-center space-x-1.5"
              >
                <span>Запросить ИИ-Тендер</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/reserve"
                className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700"
              >
                Соседи рядом
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h3 className="text-base font-extrabold text-white mb-1">Динамика остатков молока (7 дней)</h3>
          <p className="text-xs text-slate-400 mb-4">Автоматический учет расхода по дням недели</p>
          <InventoryTrendChart data={data.inventoryChart} />
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h3 className="text-base font-extrabold text-white mb-1">Источники экономии (₸)</h3>
          <p className="text-xs text-slate-400 mb-4">Выгода от волн закупа, резерва и тендеров</p>
          <SavingsBarChart data={data.savingsChart} />
        </div>
      </div>

      {/* Recent Activity Log */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <h3 className="text-base font-extrabold text-white mb-4">Журнал событий сети QORJYN</h3>
        <div className="space-y-3">
          {data.recentActivity.map((act: any) => (
            <div key={act.id} className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-xs">
              <div className="flex items-center space-x-3">
                <span className="text-lg">{act.icon}</span>
                <span className="font-semibold text-slate-200">{act.message}</span>
              </div>
              <span className="text-slate-500 font-medium">{act.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
