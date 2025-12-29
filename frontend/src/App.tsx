import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import './styles/tailwind.css';

const App: React.FC = () => {
  const [activeInfo, setActiveInfo] = useState<string | null>(null);

  const infoContent: Record<string, { title: string; body: string }> = {
    forecasting: {
      title: "AI Forecasting Methodology",
      body: "Our system utilizes LightGBM (Light Gradient Boosting Machine) to process multi-dimensional weather leads. By analyzing shortwave radiation, cloud cover, and thermal gradients, the AI predicts the precise photon-to-electron conversion potential for each specific geographic coordinate."
    },
    insights: {
      title: "Global Energy Insights",
      body: "SolarSight monitors 10 strategic global hubs. We analyze regional grid emission factors to calculate real-time carbon avoidance. Our data shows that optimal solar harvesting peak hours vary significantly by latitude, providing a blueprint for sustainable city planning."
    },
    methodology: {
      title: "Technical Stack & Guardrails",
      body: "Built on a robust Python/React stack with FastAPI and Redis caching. We implement strict physical guardrails: generation is automatically zeroed during astronomical night hours to ensure 100% data integrity and thermodynamic realism."
    }
  };

  return (
    <div className="bg-nature-overlay font-sans text-slate-200 overflow-x-hidden min-h-screen">
      {/* Header */}
      <nav className="sticky top-0 z-50 glass-card px-8 py-5 mx-6 mt-4 rounded-3xl flex justify-between items-center border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="bg-green-600 p-2 rounded-2xl shadow-lg shadow-green-600/40">
            <span className="text-2xl">🌞</span>
          </div>
          <h1 className="text-3xl font-black text-gradient tracking-tighter">SolarSight</h1>
        </div>

        <div className="hidden md:flex items-center space-x-8 text-xs font-bold text-slate-400 uppercase tracking-widest">
          <button onClick={() => setActiveInfo('forecasting')} className="hover:text-green-400 transition-colors">Forecasting</button>
          <button onClick={() => setActiveInfo('insights')} className="hover:text-green-400 transition-colors">Global Insights</button>
          <button onClick={() => setActiveInfo('methodology')} className="hover:text-green-400 transition-colors">Methodology</button>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-12">
        <header className="mb-16 max-w-4xl animate-fade-up">
          <h2 className="text-5xl md:text-6xl font-extrabold text-white mb-8 leading-[1.05] tracking-tight">
            Advancing the Global <br />
            <span className="text-green-500">Energy Transition.</span>
          </h2>
          <p className="text-xl text-slate-400 font-medium leading-relaxed max-w-3xl">
            SolarSight integrates high-resolution satellite irradiance telemetry with advanced LightGBM
            gradient boosting to deliver sub-meter precision in solar yield forecasting.
            Our multi-tier data pipeline empowers residential energy autonomy, institutional ESG compliance,
            and the engineering of carbon-neutral, grid-resilient municipal infrastructures.
          </p>
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
                Empowering the global energy transition with data-driven AI models.
                Optimizing renewable harvesting through satellite leads and LightGBM regression.
              </p>
            </div>

            {/* RESTORED SDG GOALS - Enhanced Presence */}
            <div>
              <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.4em] mb-10">United Nations Impact</h4>
              <div className="grid grid-cols-1 gap-6">
                <div className="group flex items-center space-x-4 bg-white/5 p-4 rounded-3xl border border-white/5 hover:border-green-500/30 transition-all">
                  <div className="bg-green-600/20 p-3 rounded-2xl text-2xl group-hover:scale-110 transition-transform">⚡</div>
                  <div>
                    <p className="text-[10px] font-black text-green-500 uppercase tracking-widest">Goal 7</p>
                    <p className="text-xs font-bold text-slate-200">Affordable & Clean Energy</p>
                  </div>
                </div>
                <div className="group flex items-center space-x-4 bg-white/5 p-4 rounded-3xl border border-white/5 hover:border-green-500/30 transition-all">
                  <div className="bg-cyan-600/20 p-3 rounded-2xl text-2xl group-hover:scale-110 transition-transform">🏘️</div>
                  <div>
                    <p className="text-[10px] font-black text-cyan-500 uppercase tracking-widest">Goal 11</p>
                    <p className="text-xs font-bold text-slate-200">Sustainable Cities</p>
                  </div>
                </div>
                <div className="group flex items-center space-x-4 bg-white/5 p-4 rounded-3xl border border-white/5 hover:border-green-500/30 transition-all">
                  <div className="bg-blue-600/20 p-3 rounded-2xl text-2xl group-hover:scale-110 transition-transform">🌍</div>
                  <div>
                    <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest">Goal 13</p>
                    <p className="text-xs font-bold text-slate-200">Climate Action</p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              {/* Dev Console link removed for production security */}
            </div>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-center border-t border-white/5 pt-10">
            <p className="text-slate-500 text-[10px] font-bold uppercase tracking-[0.3em]">
              © {new Date().getFullYear()} SolarSight Intelligent Systems.
            </p>
            <p className="text-white text-sm font-black tracking-tight mt-6 md:mt-0">
              Developed by <span className="text-green-500 underline underline-offset-8 decoration-green-900/50">Olayinka Julius</span>, Full-Stack Data Scientist
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
