'use client';

import React, { useEffect, useState } from 'react';
import { getWaves, joinWave } from '@/lib/api';
import { PurchaseWave } from '@/types';
import {
  Waves,
  Users,
  TrendingUp,
  Clock,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  RefreshCw
} from 'lucide-react';

export default function WavesPage() {
  const [waves, setWaves] = useState<PurchaseWave[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [myVolume, setMyVolume] = useState<number>(25);
  const [joinedWaveId, setJoinedWaveId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    const res = await getWaves();
    setWaves(res.waves || []);
    setIsLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleJoinWave = async (waveId: string) => {
    setErrorMessage(null);
    const res = await joinWave(waveId, myVolume);
    if (res.success) {
      setJoinedWaveId(waveId);
      await loadData();
    } else {
      setErrorMessage(res.error || 'Не удалось присоединиться к волне');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">
          <Waves className="w-4 h-4" />
          <span>Коллективные Закупочные Волны</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-white">Оптовые Цены за Счет Объединения</h1>
        <p className="text-xs text-slate-400 mt-1">
          Объединяйте объемы закупа с другими заведениями микрорайона и получайте цены крупных сетей.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm font-bold">
          {errorMessage}
        </div>
      )}

      {/* Active Waves Grid */}
      <div className="space-y-6">
        {waves.map(wave => {
          const progressPercent = Math.min(100, Math.round((wave.totalQuantity / wave.targetQuantity) * 100));

          return (
            <div
              key={wave.id}
              className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl backdrop-blur-md relative overflow-hidden"
            >
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-6">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-bold uppercase">
                      СОБРАНО {progressPercent}%
                    </span>
                    <span className="text-xs text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Дедлайн: завтра 18:00</span>
                    </span>
                  </div>
                  <h2 className="text-2xl font-black text-white">{wave.productName}</h2>
                </div>

                {/* Savings Callout Badge */}
                <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-right">
                  <div className="text-xs text-emerald-400 font-bold uppercase">Экономия на 1 литре</div>
                  <div className="text-2xl font-black text-white">
                    {wave.individualPrice} ₸ → <span className="text-emerald-400">{wave.groupPrice} ₸</span>
                  </div>
                  <div className="text-[11px] text-emerald-400 mt-0.5">В выигрыше: -{wave.savingsPerUnit} ₸/ед</div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2 mb-6">
                <div className="flex justify-between text-xs font-bold text-slate-300">
                  <span>Прогресс волны: {wave.totalQuantity} из {wave.targetQuantity} ед</span>
                  <span>Целевой порог опта: {wave.targetQuantity} ед</span>
                </div>
                <div className="w-full h-4 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
                  <div
                    style={{ width: `${progressPercent}%` }}
                    className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-full transition-all duration-500"
                  ></div>
                </div>
              </div>

              {/* Participants List */}
              <div className="mb-6">
                <h4 className="text-xs font-bold text-slate-400 uppercase mb-3 flex items-center space-x-2">
                  <Users className="w-4 h-4 text-cyan-400" />
                  <span>Участники этой волны ({wave.participants.length}):</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {wave.participants.map((p, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs flex justify-between items-center">
                      <span className="font-bold text-slate-200">{p.businessName}</span>
                      <span className="font-mono text-emerald-400 font-extrabold">+{p.quantity} ед</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Join Action Bar */}
              <div className="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center space-x-3 w-full sm:w-auto">
                  <span className="text-xs font-bold text-slate-300 uppercase shrink-0">Мой вклад:</span>
                  <input
                    type="number"
                    value={myVolume}
                    onChange={(e) => setMyVolume(Number(e.target.value))}
                    min={5}
                    max={200}
                    className="w-24 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs font-extrabold text-white text-center"
                  />
                  <span className="text-xs text-slate-400">ед.</span>
                </div>

                <button
                  onClick={() => handleJoinWave(wave.id)}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white font-extrabold text-xs shadow-lg shadow-cyan-600/30 flex items-center justify-center space-x-2 transition-all"
                >
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Присоединиться к волне (+{myVolume} ед)</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
