'use client';

import React from 'react';
import Link from 'next/link';
import { InteractiveMap } from '@/components/InteractiveMap';
import {
  Boxes,
  Zap,
  Waves,
  ShieldCheck,
  TrendingUp,
  ArrowRight,
  Sparkles,
  MapPin,
  CheckCircle2,
  Users
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="space-y-10">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950/60 border border-emerald-500/20 p-8 sm:p-12 shadow-2xl">
        <div className="absolute -right-10 -top-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute right-40 -bottom-20 w-80 h-80 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-4 h-4 animate-spin-slow" />
            <span>B2B Коллективное Снабжение & ИИ-Прогнозирование</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white leading-tight tracking-tight">
            Никогда не доставляйте <br />
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              клиенту дефицит
            </span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            QORJYN Mesh объединяет кофейни, пекарни и малый бизнес Алматы в единую сеть закупа.
            Объединяйте заказы в оптовые волны, запрашивайте ИИ обратный тендер и спасайте остатки у соседей за 15 минут.
          </p>

          {/* Quick Action CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              href="/tender"
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold text-sm shadow-xl shadow-emerald-600/30 flex items-center space-x-2 transition-all hover:scale-105"
            >
              <Zap className="w-4 h-4 text-amber-300" />
              <span>Запустить ИИ-Тендер</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/inventory"
              className="px-6 py-3.5 rounded-2xl bg-slate-800/90 hover:bg-slate-800 text-slate-200 font-bold text-sm border border-slate-700 flex items-center space-x-2 transition-all"
            >
              <Boxes className="w-4 h-4 text-emerald-400" />
              <span>Мой Склад</span>
            </Link>

            <Link
              href="/waves"
              className="px-6 py-3.5 rounded-2xl bg-slate-800/90 hover:bg-slate-800 text-slate-200 font-bold text-sm border border-slate-700 flex items-center space-x-2 transition-all"
            >
              <Waves className="w-4 h-4 text-cyan-400" />
              <span>Волны закупа</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Live Value Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Предотвращено дефицитов</span>
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">12 раз</div>
          <div className="text-[11px] text-emerald-400 mt-1">За последний месяц</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Сэкономлено в волнах</span>
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">45 600 ₸</div>
          <div className="text-[11px] text-amber-400 mt-1">Групповые скидки</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Скорость взаимовыручки</span>
            <div className="w-8 h-8 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">4.2 часа</div>
          <div className="text-[11px] text-cyan-400 mt-1">Среднее время перехвата</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Точки в коалиции</span>
            <div className="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-white">6 заведений</div>
          <div className="text-[11px] text-purple-400 mt-1">Алмалинский & Медеуский</div>
        </div>
      </div>

      {/* Interactive Map Section */}
      <InteractiveMap />
    </div>
  );
}
