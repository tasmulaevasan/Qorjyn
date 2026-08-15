'use client';

import React, { useState } from 'react';
import { Camera, Mic, Sparkles, CheckCircle2, Loader2, X, AlertCircle } from 'lucide-react';
import { updateInventoryItem } from '@/lib/api';

interface AiSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function AiSimulatorModal({ isOpen, onClose, onSuccess }: AiSimulatorModalProps) {
  const [mode, setMode] = useState<'photo' | 'voice'>('photo');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<{
    productName: string;
    productId: string;
    quantity: number;
    unit: string;
    confidence: number;
    locationId: string;
  } | null>(null);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSimulateAi = (type: 'photo' | 'voice') => {
    setMode(type);
    setIsAnalyzing(true);
    setResult(null);
    setErrorMessage(null);

    setTimeout(() => {
      setIsAnalyzing(false);
      if (type === 'photo') {
        setResult({
          productName: 'Молоко 3.2%',
          productId: 'prod-001',
          quantity: 12,
          unit: 'л',
          confidence: 98.4,
          locationId: 'loc-001'
        });
      } else {
        setResult({
          productName: 'Стаканы 250 мл',
          productId: 'prod-003',
          quantity: 500,
          unit: 'шт',
          confidence: 96.2,
          locationId: 'loc-001'
        });
      }
    }, 2000);
  };

  const handleConfirmStockUpdate = async () => {
    if (!result) return;
    setIsUpdating(true);
    setErrorMessage(null);
    const response = await updateInventoryItem({
      productId: result.productId,
      locationId: result.locationId,
      delta: result.quantity,
      source: mode === 'photo' ? 'manual' : 'manual',
      note: mode === 'photo' ? 'Распознано ИИ по фото остатков' : 'Голосовой ввод ИИ (WhatsApp)'
    });
    setIsUpdating(false);
    if (!response.success) {
      setErrorMessage(response.error || 'Не удалось обновить остаток');
      return;
    }
    onSuccess();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="bg-slate-900 border border-emerald-500/30 rounded-3xl max-w-lg w-full p-6 shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center text-white">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-white">ИИ-Распознавание остатков</h3>
              <p className="text-xs text-slate-400">Фото чека/склада или Голосовая заметка</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Input Mode Selection */}
        {!isAnalyzing && !result && (
          <div className="space-y-4 py-4">
            <p className="text-xs text-slate-300">
              Выберите способ симуляции мультимодального распознавания Gemini / WhatsApp бота:
            </p>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleSimulateAi('photo')}
                className="flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-800/80 border border-slate-700 hover:border-emerald-500/50 hover:bg-slate-800 transition-all text-center group"
              >
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Camera className="w-6 h-6" />
                </div>
                <span className="text-sm font-bold text-white mb-1">Фото чека / склада</span>
                <span className="text-[11px] text-slate-400">Симуляция сканирования</span>
              </button>

              <button
                onClick={() => handleSimulateAi('voice')}
                className="flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-800/80 border border-slate-700 hover:border-teal-500/50 hover:bg-slate-800 transition-all text-center group"
              >
                <div className="w-12 h-12 rounded-2xl bg-teal-500/10 text-teal-400 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Mic className="w-6 h-6" />
                </div>
                <span className="text-sm font-bold text-white mb-1">Голосовая запись</span>
                <span className="text-[11px] text-slate-400">"Привезли 500 стаканов"</span>
              </button>
            </div>
          </div>
        )}

        {/* Loading Spinner */}
        {isAnalyzing && (
          <div className="py-12 flex flex-col items-center justify-center text-center">
            <Loader2 className="w-10 h-10 text-emerald-400 animate-spin mb-4" />
            <h4 className="text-sm font-bold text-white">ИИ Обрабатывает данные...</h4>
            <p className="text-xs text-slate-400 mt-1">
              {mode === 'photo' ? 'Анализ изобржения коробок молока...' : 'Распознавание аудиосообщения...'}
            </p>
          </div>
        )}

        {/* Recognition Result Preview */}
        {result && (
          <div className="py-2 space-y-4">
            {errorMessage && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs font-bold flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}
            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  ✅ ИИ Успешно распознал
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold">
                  Точность: {result.confidence}%
                </span>
              </div>
              <div className="flex items-center justify-between mt-3">
                <div>
                  <div className="text-base font-extrabold text-white">{result.productName}</div>
                  <div className="text-xs text-slate-400">Приход на склад: Точка Абая</div>
                </div>
                <div className="text-xl font-black text-emerald-400">
                  +{result.quantity} {result.unit}
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setResult(null)}
                className="w-1/3 py-2.5 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs hover:bg-slate-700"
              >
                Отмена
              </button>
              <button
                onClick={handleConfirmStockUpdate}
                disabled={isUpdating}
                className="w-2/3 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30 flex items-center justify-center space-x-2"
              >
                {isUpdating ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                <span>Внести на склад</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
