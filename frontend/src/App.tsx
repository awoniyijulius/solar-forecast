import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import './styles/tailwind.css';

const App: React.FC = () => {
  const [activeInfo, setActiveInfo] = useState<string | null>(null);

  const infoContent: Record<string, { title: string; body: string }> = {
    forecasting: {
      title: "AI Forecasting Intelligence",
      body: "Our system utilizes LightGBM to process multi-dimensional weather leads. By analyzing shortwave radiation and thermal gradients, we predict solar potential with sub-meter precision, enabling accurate planning for both energy and agricultural yields."
    },
    sdg: {
      title: "Multi-SDG Impact Framework",
      body: "SolarSight maps data to 5 UN Sustainable Development Goals. We go beyond energy (SDG 7) to provide critical health advisories for UV protection (SDG 3) and agricultural drying/irrigation windows (SDG 2), maximizing social impact per watt."
    },
    resilience: {
      title: "Grid-Resilience & Diesel Offset",
      body: "Built for energy autonomy in any infrastructure. Our engine calculates the direct displacement of backup diesel generators, providing a roadmap for carbon-neutrality and humanitarian energy access in grid-fragile regions."
    }
  };


  return (
    <div className="bg-nature-overlay font-sans text-slate-200 overflow-x-hidden min-h-screen">
      {/* Migration Banner - Only visible on Legacy Domain */}
      {typeof window !== 'undefined' && window.location.hostname.includes('solarsight-frontend') && (
        <div className="bg-gradient-to-r from-emerald-600 to-green-600 text-white text-[10px] md:text-xs font-bold uppercase tracking-widest py-2 text-center cursor-pointer hover:underline"
          onClick={() => window.location.href = 'https://solarsight-intel.onrender.com'}>
          🚀 Upgrade to the new SolarSight Intelligence Engine →
        </div>
      )}

      {/* Header */}
      <nav className="sticky top-0 z-50 glass-card px-4 md:px-8 py-4 mx-4 md:mx-6 mt-4 rounded-3xl flex flex-col md:flex-row justify-between items-center border-b border-white/10 space-y-4 md:space-y-0">
        <div className="flex items-center space-x-3 w-full md:w-auto justify-center md:justify-start">
          <div className="bg-green-600 p-2 rounded-2xl shadow-lg shadow-green-600/40">
            <span className="text-2xl">🌞</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-gradient tracking-tighter">SolarSight</h1>
        </div>

        <div className="flex items-center space-x-4 md:space-x-8 text-[10px] md:text-xs font-bold text-slate-400 uppercase tracking-widest w-full md:w-auto justify-center">
          <button onClick={() => setActiveInfo('forecasting')} className="hover:text-green-400 transition-colors whitespace-nowrap">Forecasting</button>
          <button onClick={() => setActiveInfo('sdg')} className="hover:text-green-400 transition-colors whitespace-nowrap">SDG Impact</button>
          <button onClick={() => setActiveInfo('resilience')} className="hover:text-green-400 transition-colors whitespace-nowrap">Resilience Hub</button>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-12">
        <header className="mb-16 max-w-4xl animate-fade-up">
          <h2 className="text-5xl md:text-6xl font-extrabold text-white mb-8 leading-[1.05] tracking-tight">
            Intelligence for a <br />
            <span className="text-green-500">Resilient Future.</span>
          </h2>
          <div className="glass-card p-8 rounded-3xl border border-green-500/20 bg-gradient-to-br from-green-500/5 to-transparent">
            <p className="text-lg text-slate-300 font-medium leading-relaxed">
              SolarSight combines satellite telemetry with gradient boosting to deliver high-precision
              yield intelligence. By bridging the gap between renewable energy, dermatological health,
              and agricultural security, we empower communities to leapfrog grid-fragility towards
              a sustainable, multi-dimensional energy transition.
            </p>
          </div>
        </header>

        <Dashboard />
      </main>

      {/* Info Modal */}
      {activeInfo && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 modal-overlay" onClick={() => setActiveInfo(null)}>
          <div className="glass-card max-w-lg p-10 rounded-[32px] border-green-500/30 relative" onClick={e => e.stopPropagation()}>
            <button onClick={() => setActiveInfo(null)} className="absolute top-6 right-6 text-slate-400 hover:text-white text-2xl">✕</button>
            <h3 className="text-2xl font-black text-white mb-4">{infoContent[activeInfo].title}</h3>
            <p className="text-slate-300 leading-relaxed font-medium">{infoContent[activeInfo].body}</p>
            <div className="mt-8">
              <button
                onClick={() => setActiveInfo(null)}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-2xl font-bold transition-all"
              >
                Dismiss Intelligence
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Corporate Sustainable Footer */}
      <footer className="mt-32 border-t border-white/5 bg-black/20 backdrop-blur-xl py-20">
        <div className="container mx-auto px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
            <div className="col-span-2">
              <div className="flex items-center space-x-2 mb-6 opacity-50">
                <span className="text-xl">🌞</span>
                <span className="font-black tracking-tighter text-xl text-white">SolarSight</span>
              </div>
              <p className="text-slate-500 max-w-sm text-sm font-medium leading-relaxed">
                Empowering the Global South with open-source, high-precision renewable energy telemetries.
                Built for resilience, engineered for impact.
              </p>
            </div>

            {/* SDG GOALS - Horizontal Grid Tray */}
            <div className="col-span-2">
              <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] mb-6">United Nations Impact</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {/* SDG 2 */}
                <div className="group flex flex-col items-center text-center bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-emerald-500/30 transition-all">
                  <div className="bg-emerald-600/20 p-3 rounded-xl text-2xl group-hover:scale-110 transition-transform mb-2">🌾</div>
                  <p className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Goal 2</p>
                  <p className="text-[10px] font-bold text-slate-300">Zero Hunger</p>
                </div>
                {/* SDG 3 */}
                <div className="group flex flex-col items-center text-center bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-rose-500/30 transition-all">
                  <div className="bg-rose-600/20 p-3 rounded-xl text-2xl group-hover:scale-110 transition-transform mb-2">❤️</div>
                  <p className="text-[9px] font-black text-rose-500 uppercase tracking-widest">Goal 3</p>
                  <p className="text-[10px] font-bold text-slate-300">Good Health</p>
                </div>
                {/* SDG 7 */}
                <div className="group flex flex-col items-center text-center bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-green-500/30 transition-all">
                  <div className="bg-green-600/20 p-3 rounded-xl text-2xl group-hover:scale-110 transition-transform mb-2">⚡</div>
                  <p className="text-[9px] font-black text-green-500 uppercase tracking-widest">Goal 7</p>
                  <p className="text-[10px] font-bold text-slate-300">Clean Energy</p>
                </div>
                {/* SDG 11 */}
                <div className="group flex flex-col items-center text-center bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-cyan-500/30 transition-all">
                  <div className="bg-cyan-600/20 p-3 rounded-xl text-2xl group-hover:scale-110 transition-transform mb-2">🏘️</div>
                  <p className="text-[9px] font-black text-cyan-500 uppercase tracking-widest">Goal 11</p>
                  <p className="text-[10px] font-bold text-slate-300">Sustainable Cities</p>
                </div>
                {/* SDG 13 */}
                <div className="group flex flex-col items-center text-center bg-white/5 p-4 rounded-2xl border border-white/5 hover:border-blue-500/30 transition-all">
                  <div className="bg-blue-600/20 p-3 rounded-xl text-2xl group-hover:scale-110 transition-transform mb-2">🌍</div>
                  <p className="text-[9px] font-black text-blue-500 uppercase tracking-widest">Goal 13</p>
                  <p className="text-[10px] font-bold text-slate-300">Climate Action</p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-center border-t border-white/5 pt-10">
            <div className="mb-6 md:mb-0">
              <p className="text-slate-500 text-[10px] font-bold uppercase tracking-[0.3em] mb-2">
                © {new Date().getFullYear()} SolarSight Intelligent Systems.
              </p>
            </div>
            <p className="text-white text-sm font-black tracking-tight mt-6 md:mt-0">
              Developed by <span className="text-green-500 underline underline-offset-8 decoration-green-900/50">Olayinka Julius</span>
            </p>
          </div>
        </div>
      </footer>
    </div >
  );
};

export default App;
