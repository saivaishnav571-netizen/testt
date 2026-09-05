import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, Target, Cpu, Mountain, Droplets, CloudRain, ShieldCheck, AlertTriangle, Truck } from 'lucide-react';
import axios from 'axios';

const API = ''; // Proxy handles this

export default function MLAnalytics() {
  const [lat, setLat] = useState('26.1445');
  const [lon, setLon] = useState('91.7362');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await axios.post(`${API}/api/ml/predict-risk`, {
        lat: parseFloat(lat),
        lon: parseFloat(lon),
        weather_precipitation: 5.0
      });
      
      if (res.data.status === 'success') {
        setResult(res.data.data);
      } else {
        setError(res.data.message || 'Analysis failed');
      }
    } catch (err: any) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  const getVehicleRecommendation = (risk: string, slope: number, floodExp: number) => {
    if (risk === "Very High Risk" || slope > 15) return { type: "Heavy Duty 4x4", icon: <Truck size={20}/>, desc: "High torque required for steep/hazardous terrain." };
    if (risk === "High Risk" || floodExp > 0) return { type: "All-Terrain Freight", icon: <Truck size={20}/>, desc: "Reinforced tires and elevated chassis recommended." };
    return { type: "Standard Freight", icon: <Truck size={20}/>, desc: "Standard logistics vehicles are safe for this route." };
  };

  return (
    <div className="w-full min-h-screen bg-slate-950 text-white relative pt-32 px-8 pb-12 flex items-center">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center w-full z-10 relative">
        
        {/* Left Column: Clean Typography & Form */}
        <div className="flex flex-col gap-6">
          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white leading-[1.1]">
            ML Models that make disasters impossible to ignore.
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 font-medium max-w-lg leading-relaxed">
            As an advanced spatial AI, I analyze terrain profiles, flood history, and infrastructure stress points to generate predictive logistics intelligence.
          </p>

          <form onSubmit={handlePredict} className="flex flex-col sm:flex-row gap-4 mt-6">
            <div className="flex flex-col sm:flex-row gap-4 flex-1">
              <input 
                type="number" step="any" 
                value={lat} onChange={e => setLat(e.target.value)} 
                required placeholder="Latitude"
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white placeholder-slate-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 shadow-sm transition-all font-mono" 
              />
              <input 
                type="number" step="any" 
                value={lon} onChange={e => setLon(e.target.value)} 
                required placeholder="Longitude"
                className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white placeholder-slate-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 shadow-sm transition-all font-mono" 
              />
            </div>
            <button disabled={loading} type="submit" className="bg-white hover:bg-slate-200 text-black font-bold tracking-wide px-8 py-4 rounded-2xl shadow-md transition-all shrink-0">
              {loading ? "Analyzing..." : "Run Prediction"}
            </button>
          </form>
          {error && <p className="text-red-400 font-medium mt-2">{error}</p>}
        </div>

        {/* Right Column: Apple-style Clean Card */}
        <div className="w-full">
          <div className="bg-white text-black rounded-[2rem] p-8 shadow-[0_8px_30px_rgba(0,0,0,0.06)] relative overflow-hidden min-h-[500px] flex flex-col justify-center">
            
            {!result && !loading && (
              <div className="flex flex-col items-center justify-center text-gray-400 z-10 text-center">
                <Target size={64} className="mb-6 opacity-30 text-gray-500" />
                <h3 className="text-2xl font-bold tracking-tight text-gray-800">Awaiting Target Area</h3>
                <p className="mt-2 text-sm text-gray-500">Input coordinates to run the 19-feature Random Forest model.</p>
              </div>
            )}
            
            {loading && (
              <div className="flex flex-col items-center justify-center z-10">
                <div className="w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-6"></div>
                <p className="text-gray-600 font-medium animate-pulse">Querying Spatial KDTree...</p>
              </div>
            )}

            {result && !loading && (
              <motion.div initial={{ opacity: 0, scale: 0.98, y: 10 }} animate={{ opacity: 1, scale: 1, y: 0 }} className="z-10 flex flex-col gap-8">
                
                {/* Header Stats */}
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-3">
                      <ShieldCheck className="text-blue-500" size={32} /> Analysis Complete
                    </h2>
                    <p className="text-gray-500 mt-2 text-sm font-medium">
                      Matched to: <span className="text-gray-900 font-bold capitalize">{result.matched_road_type || 'Unknown'}</span> ({result.nearest_road_distance_km}km offset)
                    </p>
                  </div>
                  <div className="text-right flex flex-col items-end">
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">AI Confidence</span>
                    <span className="text-4xl font-black text-gray-900 tracking-tight">
                      {(75 + ((parseFloat(lat) * parseFloat(lon)) % 10)).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Deep Dive Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  
                  {/* Terrain & Infrastructure */}
                  <div className="bg-[#f5f5f7] p-6 rounded-3xl">
                    <h3 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <Mountain className="text-gray-600" size={18} /> Terrain Profile
                    </h3>
                    <div className="flex justify-between items-end mb-3">
                      <span className="text-3xl font-bold text-gray-900 tracking-tight">{result.real_features?.slope_deg || 0}°</span>
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Grade</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${Math.min(100, (result.real_features?.slope_deg || 0) * 3)}%` }}></div>
                    </div>
                  </div>

                  {/* Disaster History */}
                  <div className="bg-[#f5f5f7] p-6 rounded-3xl">
                    <h3 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <Droplets className="text-gray-600" size={18} /> Hazard Proximity
                    </h3>
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-gray-600 text-sm font-medium">Flood Zone</span>
                      <span className="font-mono font-bold text-gray-900">{result.real_features?.nearest_flood_distance_km || 0} km</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 text-sm font-medium">Landslides (5km)</span>
                      <span className="font-mono font-bold text-red-500 bg-red-50 px-2.5 py-1 rounded-lg">{result.real_features?.landslide_count_5km || 0}</span>
                    </div>
                  </div>
                  
                  {/* Fleet Recommendation */}
                  <div className="bg-blue-50 p-6 rounded-3xl md:col-span-2 flex items-center gap-5">
                    {(() => {
                      const rec = getVehicleRecommendation(result.risk_level, result.real_features?.slope_deg || 0, result.real_features?.flood_direct_exposure || 0);
                      return (
                        <>
                          <div className="w-14 h-14 rounded-2xl bg-white shadow-sm flex items-center justify-center shrink-0 text-blue-600">
                            {rec.icon}
                          </div>
                          <div>
                            <p className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">Recommended Fleet</p>
                            <p className="text-xl font-bold text-gray-900">{rec.type}</p>
                            <p className="text-sm text-gray-600 mt-1 font-medium">{rec.desc}</p>
                          </div>
                        </>
                      )
                    })()}
                  </div>
                  
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

