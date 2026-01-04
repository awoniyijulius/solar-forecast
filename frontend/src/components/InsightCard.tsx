import React from 'react';

interface InsightCardProps {
  totalCo2: number;
  predictions: number[];
  hours: string[];
  currency?: string;
  rate?: number;
  // NEW: Health & Agricultural Metrics
  peakUv?: number;
  peakUvHour?: number;
  uvRiskLevel?: string;
  safeSunExposureMins?: number;
  agriDryingWindows?: number[];
  agriIrrigationAdvice?: string;
}

const InsightCard: React.FC<InsightCardProps> = ({
  totalCo2, predictions, hours, currency = '$', rate = 0.15,
  peakUv = 0, peakUvHour = 12, uvRiskLevel = 'Moderate', safeSunExposureMins = 30,
  agriDryingWindows = [], agriIrrigationAdvice = 'Morning'
}) => {
  const SYSTEM_PEAK_CAPACITY_KW = 10.0;

  // Ensure we are calculating for a single 24-hour cycle for daily impact metrics
  const dailyPredictions = predictions.slice(0, 24);
  const peakValue = Math.max(...dailyPredictions);
  const peakHourIndex = dailyPredictions.indexOf(peakValue);
  const peakTimeRaw = peakHourIndex >= 0 ? hours[peakHourIndex] : 'N/A';
  const peakTime = peakTimeRaw.includes('T') ? peakTimeRaw.split('T')[1].substring(0, 5) : peakTimeRaw;

  const dailyTotalKwh = dailyPredictions.reduce((a, b) => a + b, 0);
  const totalMWh = dailyTotalKwh / 1000;
  const peakMW = peakValue / 1000;

  // Financial ROI Logic
  const dailySavings = dailyTotalKwh * rate;
  const annualSavings = dailySavings * 365;

  // STAKEHOLDER COVERAGE METRICS (Investor Calibrated)
  // We use realistic high-end demand baselines for a 10kWp system
  const RESIDENTIAL_BASELINE = 45.0;  // High-end Smart Home daily demand
  const CORPORATE_BASELINE = 450.0;   // Sustainable Micro-Factory / Office daily demand

  const resSupport = (dailyTotalKwh / RESIDENTIAL_BASELINE) * 100;
  const corpSupport = (dailyTotalKwh / CORPORATE_BASELINE) * 100;
  const cityImpact = (totalMWh * 365).toFixed(2); // Annual Grid Yield

  return (
    <div className="space-y-6 animate-fade-up">
      {/* 🚀 STAKEHOLDER IMPACT ROADMAP */}
      <div className="glass-card p-8 rounded-[32px] border-green-500/20 bg-gradient-to-br from-green-500/5 to-transparent">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-[10px] font-black text-green-500 uppercase tracking-[0.4em]">Strategic Market Impact</h3>
          <span className="text-[10px] font-bold text-slate-500 bg-white/5 px-3 py-1 rounded-full border border-white/5">Daily 24h Cycle</span>
        </div>

        <div className="space-y-8">
          {/* Residential Tier */}
          <div>
            <div className="flex justify-between items-end mb-2">
              <div>
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Individual / Residential</p>
                <p className="text-sm font-bold text-white">Grid Autonomy Index</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-black text-green-500">{Math.min(100, resSupport).toFixed(1)}%</p>
                {resSupport > 100 && <p className="text-[8px] font-black text-green-400/60 uppercase">Surplus Export</p>}
              </div>
            </div>
            <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
              <div className="bg-green-500 h-full rounded-full transition-all duration-1000" style={{ width: `${Math.min(100, resSupport)}%` }}></div>
            </div>
          </div>

          {/* Corporate Tier */}
          <div>
            <div className="flex justify-between items-end mb-2">
              <div>
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Industrial / Corporate</p>
                <p className="text-sm font-bold text-white">ESG Load Offset</p>
              </div>
              <p className="text-xl font-black text-cyan-500">{Math.min(100, corpSupport).toFixed(1)}%</p>
            </div>
            <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
              <div className="bg-cyan-500 h-full rounded-full transition-all duration-1000" style={{ width: `${Math.min(100, corpSupport)}%` }}></div>
            </div>
          </div>

          {/* City Tier */}
          <div>
            <div className="flex justify-between items-end mb-2">
              <div>
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Global City / Government</p>
                <p className="text-sm font-bold text-white">Annual Yield Capacity</p>
              </div>
              <p className="text-xl font-black text-blue-500">{cityImpact} <span className="text-xs">MWh/Yr</span></p>
            </div>
            <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
              <div className="bg-blue-500 h-full rounded-full" style={{ width: '65%' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* 💰 FINANCIAL ROI PROJECTION */}
      <div className="glass-card p-8 rounded-[32px] border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-transparent">
        <h3 className="text-[10px] font-black text-amber-500 uppercase tracking-[0.4em] mb-8">Financial ROI Estimate</h3>
        <div className="flex justify-between items-end">
          <div>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Estimated Annual Savings</p>
            <p className="text-3xl font-black text-white tracking-tighter">
              {currency} {annualSavings.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Daily Value</p>
            <p className="text-xl font-bold text-amber-500">{currency} {dailySavings.toFixed(2)}</p>
          </div>
        </div>
        <p className="text-[9px] font-bold text-slate-500 mt-4 italic">Based on local avg tariff of {currency}{rate}/kWh</p>
      </div>

      {/* 🛡️ CLIMATE RESILIENCE & SOCIAL IMPACT (NEW) */}
      <div className="glass-card p-8 rounded-[32px] border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-transparent">
        <h3 className="text-[10px] font-black text-blue-500 uppercase tracking-[0.4em] mb-8">Resilience & Social Impact</h3>
        <div className="flex items-center space-x-6">
          <div className="bg-blue-500/20 p-4 rounded-3xl text-3xl">🛢️</div>
          <div>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Estimated Diesel Avoidance</p>
            <p className="text-2xl font-black text-white">
              {(dailyTotalKwh / 2.5).toFixed(1)} <span className="text-xs text-blue-400">Liters / Day</span>
            </p>
            <p className="text-[9px] font-bold text-slate-500 mt-1">
              Equivalent to ~{(dailyTotalKwh / 5).toFixed(1)} hours of backup generator run-time
            </p>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-white/5 grid grid-cols-2 gap-4">
          <div>
            <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Energy Access</p>
            <p className="text-xs font-bold text-white">{(dailyTotalKwh * 1.5).toFixed(0)} Home-Hours</p>
          </div>
          <div className="text-right">
            <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Social KPI</p>
            <p className="text-xs font-bold text-white">Low-Carbon Transition</p>
          </div>
        </div>
      </div>

      {/* ☀️ UV HEALTH ADVISORY (SDG 3: Good Health) */}
      <div className="glass-card p-8 rounded-[32px] border-rose-500/20 bg-gradient-to-br from-rose-500/5 to-transparent">
        <h3 className="text-[10px] font-black text-rose-500 uppercase tracking-[0.4em] mb-6">Dermatological Advisory</h3>
        <div className="flex items-center space-x-6">
          <div className={`p-4 rounded-3xl text-3xl ${uvRiskLevel === 'Extreme' || uvRiskLevel === 'Very High' ? 'bg-red-500/20' :
              uvRiskLevel === 'High' ? 'bg-orange-500/20' : 'bg-yellow-500/20'
            }`}>☀️</div>
          <div>
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Peak UV Index</p>
            <p className="text-2xl font-black text-white">
              {peakUv.toFixed(1)} <span className={`text-sm ${uvRiskLevel === 'Extreme' || uvRiskLevel === 'Very High' ? 'text-red-400' :
                  uvRiskLevel === 'High' ? 'text-orange-400' : 'text-yellow-400'
                }`}>({uvRiskLevel})</span>
            </p>
            <p className="text-[9px] font-bold text-slate-500 mt-1">
              Peak occurs at ~{peakUvHour}:00 local time
            </p>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-white/5">
          <div className="flex justify-between items-center">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Safe Unprotected Exposure</p>
            <p className="text-lg font-black text-rose-400">{safeSunExposureMins} mins</p>
          </div>
          <p className="text-[9px] font-bold text-slate-500 mt-2 italic">
            SPF 30+ recommended for outdoor workers during peak hours. (SDG 3: Good Health)
          </p>
        </div>
      </div>

      {/* 🌾 AGRICULTURAL ADVISORY (SDG 2: Zero Hunger) */}
      <div className="glass-card p-8 rounded-[32px] border-emerald-500/20 bg-gradient-to-br from-emerald-500/5 to-transparent">
        <h3 className="text-[10px] font-black text-emerald-500 uppercase tracking-[0.4em] mb-6">Agricultural Intelligence</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="flex items-center space-x-3 mb-3">
              <span className="text-2xl">🌾</span>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Crop Drying Windows</p>
            </div>
            <p className="text-xs font-bold text-white">
              {agriDryingWindows.length > 0
                ? `${agriDryingWindows.length} optimal hours today (${agriDryingWindows.slice(0, 3).map(h => `${h}:00`).join(', ')}${agriDryingWindows.length > 3 ? '...' : ''})`
                : 'No ideal windows - expect cloud cover'}
            </p>
          </div>
          <div>
            <div className="flex items-center space-x-3 mb-3">
              <span className="text-2xl">💧</span>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Irrigation Timing</p>
            </div>
            <p className="text-xs font-bold text-white">{agriIrrigationAdvice}</p>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t border-white/5">
          <p className="text-[9px] font-bold text-slate-500 italic">
            Solar-powered irrigation pumps will have peak efficiency during identified drying windows. (SDG 2: Zero Hunger)
          </p>
        </div>
      </div>

      {/* 📡 ASSET TELEMETRY & REVENUE METERING */}
      <div className="glass-card p-8 rounded-[32px] border-white/5 bg-black/20">
        <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.4em] mb-10">Scientific Telemetry Chain</h3>

        <div className="grid grid-cols-1 gap-6">
          <div className="flex items-center justify-between border-b border-white/5 pb-4">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📡</span>
              <div>
                <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Pyranometer</p>
                <p className="text-xs font-bold text-white">Peak Window: {peakTime}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-black text-amber-500">{(peakValue * 105).toFixed(1)} <span className="text-[10px]">W/m²</span></p>
            </div>
          </div>

          <div className="flex items-center justify-between border-b border-white/5 pb-4">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔌</span>
              <div>
                <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Inverter DC</p>
                <p className="text-xs font-bold text-white">Conversion Peak</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-black text-blue-500">{peakValue.toFixed(2)} <span className="text-[10px]">kW</span></p>
              <p className="text-[9px] font-black text-slate-600">{peakMW.toFixed(4)} MW</p>
            </div>
          </div>

          <div className="flex items-center justify-between border-b border-white/5 pb-4">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🌿</span>
              <div>
                <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Carbon Avoided</p>
                <p className="text-xs font-bold text-white">Net ESG Offset</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-black text-emerald-500">{totalCo2.toFixed(2)} <span className="text-[10px]">kg</span></p>
              <p className="text-[9px] font-black text-slate-600">Daily Total</p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🏦</span>
              <div>
                <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Revenue Meter</p>
                <p className="text-xs font-bold text-white">Settlement Grade</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-black text-green-500">{totalMWh.toFixed(4)} <span className="text-[10px]">MWh</span></p>
              <p className="text-[9px] font-black text-slate-600">{dailyTotalKwh.toFixed(1)} kWh</p>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 py-4 rounded-2xl bg-white/5 border border-white/10 text-center">
        <p className="text-[9px] font-black text-slate-400 uppercase tracking-[0.3em]">
          Engineered for Grid-Scale Deployment
        </p>
      </div>
    </div>
  );
};

export default InsightCard;
