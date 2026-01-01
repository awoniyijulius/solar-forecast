import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import HourlyChart from './HourlyChart';
import InsightCard from './InsightCard';

interface PredictionData {
  location: string;
  generated_at_utc: string;
  timezone: string;
  timezone_abbr: string;
  hours: string[];
  pred_kwh: number[];
  confidence: number[];
  co2_kg_per_hour: number[];
  co2_kg_total: number;
}

const CITIES = [
  { id: 'lagos', name: 'Lagos, Nigeria', currency: '₦', rate: 225.0 },
  { id: 'nairobi', name: 'Nairobi, Kenya', currency: 'KSh', rate: 28.0 },
  { id: 'cape_town', name: 'Cape Town, South Africa', currency: 'R', rate: 3.50 },
  { id: 'london', name: 'London, UK', currency: '£', rate: 0.34 },
  { id: 'berlin', name: 'Berlin, Germany', currency: '€', rate: 0.42 },
  { id: 'paris', name: 'Paris, France', currency: '€', rate: 0.28 },
  { id: 'tokyo', name: 'Tokyo, Japan', currency: '¥', rate: 32.0 },
  { id: 'new_york', name: 'New York, USA', currency: '$', rate: 0.24 },
  { id: 'dubai', name: 'Dubai, UAE', currency: 'AED', rate: 0.45 },
  { id: 'sydney', name: 'Sydney, Australia', currency: 'A$', rate: 0.38 },
];

const Dashboard: React.FC = () => {
  const [location, setLocation] = useState('lagos');
  const [data, setData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forecastHours, setForecastHours] = useState(24); // 24h default

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Backend handles caching and precompute
      const meta = (import.meta as any).env;
      let apiUrl = meta.VITE_API_URL || '';

      if (apiUrl && !apiUrl.startsWith('http')) {
        apiUrl = `https://${apiUrl}`;
      }
      const response = await axios.get(`${apiUrl}/api/predictions/${location}`);
      setData(response.data);
    } catch (err: any) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;

      if (status === 503) {
        setError(detail || "Inference pending... The system is warming up its models for this location.");
      } else if (status === 429) {
        setError(detail || "The weather data provider is temporarily busy. Please try again shortly.");
      } else {
        setError(err.message || "Failed to fetch prediction data.");
      }
    } finally {
      setLoading(false);
    }
  }, [location]);

  useEffect(() => {
    // Analytics: Record impression on mount
    const trackHit = async () => {
      try {
        const meta = (import.meta as any).env;
        let apiUrl = meta.VITE_API_URL || '';
        if (apiUrl && !apiUrl.startsWith('http')) {
          apiUrl = `https://${apiUrl}`;
        }
        await axios.post(`${apiUrl}/api/analytics/hit`);
      } catch (e) { /* silent fail for analytics */ }
    };
    trackHit();

    fetchData();
    const interval = setInterval(fetchData, 15 * 60 * 1000); // 15 min refresh
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Search & Filter Section */}
      <section className="flex flex-col md:flex-row justify-between items-start md:items-center glass-card p-6 rounded-3xl space-y-4 md:space-y-0">
        <div className="w-full md:w-1/3">
          <label className="block text-xs font-bold text-green-700 uppercase tracking-widest mb-2 ml-1">
            Region Selector
          </label>
          <select
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full bg-white/5 border-0 ring-1 ring-white/10 rounded-2xl p-4 font-semibold text-white focus:ring-2 focus:ring-green-500 transition-all outline-none"
          >
            {CITIES.map(c => <option key={c.id} value={c.id} className="text-slate-900">{c.name}</option>)}
          </select>
        </div>

        <div className="w-full md:w-auto flex bg-white/5 p-1.5 rounded-2xl shadow-inner border border-white/5">
          {[24, 48].map((h) => (
            <button
              key={h}
              onClick={() => setForecastHours(h)}
              className={`px-8 py-3 rounded-xl font-bold transition-all ${forecastHours === h
                ? 'bg-green-600 text-white shadow-lg'
                : 'text-slate-400 hover:bg-white/5'
                }`}
            >
              Plus {h === 24 ? '24h' : '48h'}
            </button>
          ))}
        </div>
      </section>

      {/* Main Stats Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 animate-pulse">
          <div className="w-16 h-16 border-4 border-white/5 border-t-green-500 rounded-full animate-spin mb-4"></div>
          <p className="text-slate-400 font-medium tracking-wide">Synthesizing forecast models...</p>
        </div>
      ) : error ? (
        <div className="glass-card border-amber-500/20 bg-amber-500/5 p-12 rounded-[32px] text-center animate-fade-in">
          <div className="w-20 h-20 bg-amber-500/10 rounded-3xl flex items-center justify-center mx-auto mb-6 border border-amber-500/20">
            <span className="text-4xl">⏳</span>
          </div>
          <h3 className="text-2xl font-black text-white mb-3">Service Temporarily Saturated</h3>
          <p className="text-slate-400 max-w-md mx-auto mb-8 font-medium leading-relaxed">
            {error.includes("429") || error.includes("busy")
              ? "The high volume of global requests has temporarily throttled our weather data stream. We are recalibrating for your region."
              : error}
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={fetchData}
              className="bg-green-600 hover:bg-green-500 text-white px-10 py-4 rounded-2xl font-black transition-all shadow-lg shadow-green-600/20 flex items-center group"
            >
              <span className="mr-2 group-hover:rotate-180 transition-transform duration-500">🔄</span>
              Attempt Reconnection
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-8 py-4 rounded-2xl font-bold text-slate-400 hover:text-white transition-all"
            >
              Refresh Application
            </button>
          </div>

          <div className="mt-10 pt-8 border-t border-white/5">
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mb-4">Diagnostic Context</p>
            <code className="text-[10px] text-amber-500/70 font-mono bg-black/40 px-4 py-2 rounded-xl border border-white/5">
              {location.toUpperCase()} | STATUS_{error.includes("429") ? "429_LIMIT_THROTTLED" : "SERVICE_UNAVAILABLE"}
            </code>
          </div>
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chart Section */}
          <div className="lg:col-span-2 glass-card p-8 rounded-3xl overflow-hidden">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Live Power Forecast</h2>
                {data.timezone && (
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">
                    Displaying in Local Time: {data.timezone} ({data.timezone_abbr})
                  </p>
                )}
              </div>
              <div className="flex items-center text-[10px] font-bold text-green-500 bg-green-500/10 px-3 py-1.5 rounded-full uppercase tracking-widest border border-green-500/20">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-ping"></span>
                Last Sync: {new Date(data.generated_at_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
            <HourlyChart
              hours={data.hours.slice(0, forecastHours)}
              predictions={data.pred_kwh.slice(0, forecastHours)}
              confidence={data.confidence.slice(0, forecastHours)}
              co2Data={data.co2_kg_per_hour.slice(0, forecastHours)}
            />
          </div>

          {/* Details Section */}
          <div className="lg:col-span-1 border-0">
            <InsightCard
              totalCo2={data.co2_kg_total}
              predictions={data.pred_kwh}
              hours={data.hours}
              currency={CITIES.find(c => c.id === location)?.currency}
              rate={CITIES.find(c => c.id === location)?.rate}
            />
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default Dashboard;
