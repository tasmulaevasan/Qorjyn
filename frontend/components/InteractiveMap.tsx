'use client';

import React, { useState } from 'react';
import { MapPin, Navigation as NavIcon, Store, Zap, ShieldAlert } from 'lucide-react';

interface MapNode {
  id: string;
  name: string;
  type: string;
  address: string;
  district: string;
  surplusItem?: string;
  surplusQty?: string;
  discount?: string;
  coordinates: { lat: number; lng: number };
  status: 'active' | 'surplus' | 'supplying';
  emoji: string;
}

const mockNetworkNodes: MapNode[] = [
  {
    id: 'node-1',
    name: 'Арома Coffee (Абая)',
    type: 'Кофейня',
    address: 'ул. Абая 44',
    district: 'Алмалинский',
    coordinates: { lat: 43.238, lng: 76.945 },
    status: 'active',
    emoji: '☕'
  },
  {
    id: 'node-2',
    name: 'Пекарня Нан (Гоголя)',
    type: 'Пекарня',
    address: 'ул. Гоголя 78',
    district: 'Медеуский',
    surplusItem: 'Молоко 3.2%',
    surplusQty: '15 л',
    discount: '400 ₸/л (-12%)',
    coordinates: { lat: 43.2565, lng: 76.9284 },
    status: 'surplus',
    emoji: '🥐'
  },
  {
    id: 'node-3',
    name: 'Мини-маркет Береке',
    type: 'Мини-маркет',
    address: 'пр. Аль-Фараби 15',
    district: 'Бостандыкский',
    surplusItem: 'Молоко 3.2%',
    surplusQty: '40 л',
    discount: '420 ₸/л (-7%)',
    coordinates: { lat: 43.218, lng: 76.928 },
    status: 'surplus',
    emoji: '🛒'
  },
  {
    id: 'node-4',
    name: 'Almaty Milk (Склад №1)',
    type: 'Поставщик',
    address: 'ул. Рыскулова 103',
    district: 'Жетысуский',
    coordinates: { lat: 43.278, lng: 76.91 },
    status: 'supplying',
    emoji: '🥛'
  }
];

export function InteractiveMap() {
  const [selectedNode, setSelectedNode] = useState<MapNode | null>(mockNetworkNodes[0]);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
        <div>
          <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase tracking-wider mb-1">
            <Zap className="w-4 h-4" />
            <span>Сеть Соседской Взаимовыручки</span>
          </div>
          <h3 className="text-xl font-extrabold text-white">Интерактивная карта узлов сети Алматы</h3>
        </div>
        <div className="flex items-center space-x-2 bg-slate-800/80 p-1.5 rounded-xl border border-slate-700 text-xs">
          <span className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Кофейни</span>
          </span>
          <span className="flex items-center space-x-1 px-2 py-1 rounded-lg bg-amber-500/20 text-amber-300 font-semibold">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>Резервы излишек</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulated Map Container */}
        <div className="lg:col-span-2 relative h-[360px] bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden flex items-center justify-center p-4">
          {/* Map Grid Background Effect */}
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:16px_16px]"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent"></div>

          {/* Node Pins Simulation */}
          <div className="relative w-full h-full">
            {mockNetworkNodes.map((node, index) => {
              const positions = [
                { top: '55%', left: '45%' },
                { top: '30%', left: '60%' },
                { top: '75%', left: '35%' },
                { top: '20%', left: '25%' }
              ];
              const isSelected = selectedNode?.id === node.id;

              return (
                <button
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  style={positions[index]}
                  className={`absolute transform -translate-x-1/2 -translate-y-1/2 group transition-all duration-300 z-10 ${
                    isSelected ? 'scale-125 z-30' : 'hover:scale-110'
                  }`}
                >
                  <div
                    className={`relative flex items-center justify-center w-10 h-10 rounded-2xl shadow-lg border backdrop-blur-md transition-all ${
                      node.status === 'surplus'
                        ? 'bg-amber-500/20 border-amber-400 text-amber-300 shadow-amber-500/30'
                        : node.status === 'supplying'
                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-cyan-500/30'
                        : 'bg-emerald-500/20 border-emerald-400 text-emerald-300 shadow-emerald-500/30'
                    }`}
                  >
                    <span className="text-lg">{node.emoji}</span>
                    {node.status === 'surplus' && (
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 rounded-full animate-ping"></span>
                    )}
                  </div>
                  <div className="mt-1 bg-slate-900/90 text-[10px] font-bold text-slate-200 px-2 py-0.5 rounded-md border border-slate-700 whitespace-nowrap shadow-md">
                    {node.name.split(' ')[0]}
                  </div>
                </button>
              );
            })}
          </div>

          <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 text-[11px] text-slate-400 flex items-center space-x-2">
            <NavIcon className="w-3.5 h-3.5 text-emerald-400" />
            <span>Алматы, Алмалинский / Медеуский районы</span>
          </div>
        </div>

        {/* Selected Node Details Side Card */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          {selectedNode ? (
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-700 flex items-center justify-center text-2xl shadow-inner">
                  {selectedNode.emoji}
                </div>
                <div>
                  <h4 className="font-extrabold text-white text-base">{selectedNode.name}</h4>
                  <p className="text-xs text-slate-400">{selectedNode.address} • {selectedNode.district}</p>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center text-xs">
                  <span className="text-slate-400">Тип заведения</span>
                  <span className="font-bold text-slate-200">{selectedNode.type}</span>
                </div>

                {selectedNode.surplusItem ? (
                  <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200">
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-amber-400 mb-1">
                      <ShieldAlert className="w-4 h-4" />
                      <span>ИЗЛИШКИ ДЛЯ СПАСЕНИЯ</span>
                    </div>
                    <div className="text-sm font-extrabold text-white">{selectedNode.surplusItem}</div>
                    <div className="text-xs text-amber-300 mt-1 flex justify-between">
                      <span>В наличии: <strong>{selectedNode.surplusQty}</strong></span>
                      <span>Цена: <strong>{selectedNode.discount}</strong></span>
                    </div>
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300">
                    ✅ Активный узел сети QORJYN. Работает в штатном режиме.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-10">Выберите точку на карте</div>
          )}

          <button className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-all shadow-md shadow-emerald-600/20">
            Запросить взаимовыручку
          </button>
        </div>
      </div>
    </div>
  );
}
