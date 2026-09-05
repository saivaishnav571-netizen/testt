import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldAlert, TrendingUp, Radio, AlertTriangle, CheckCircle2, BarChart3, PieChart } from 'lucide-react';

export default function CommandCenter() {
  const [activeFleets, setActiveFleets] = useState(1248);
  const [hazardsAvoided, setHazardsAvoided] = useState(342);
  const [latency, setLatency] = useState(42);
  const [throughput, setThroughput] = useState(1.23);
  
  const initialAlerts = [
    { id: 1, time: "2 mins ago", msg: "Landslide risk elevated on NH-27 (Silchar route). Traffic rerouted.", type: "critical" },
    { id: 2, time: "14 mins ago", msg: "Heavy rainfall detected near Jorabat node. Decreasing speed limits.", type: "warning" },
    { id: 3, time: "1 hr ago", msg: "Fleet #402 successfully bypassed flooded sector in Nagaon.", type: "success" },
  ];
  
  const [liveAlerts, setLiveAlerts] = useState(initialAlerts);

  useEffect(() => {
    const simInterval = setInterval(() => {
      // 1. Tick up stats
      if (Math.random() > 0.4) {
        setActiveFleets(prev => prev + Math.floor(Math.random() * 4));
      }
      if (Math.random() > 0.8) {
        setHazardsAvoided(prev => prev + 1);
      }
      
      // 2. Fluctuate server telemetry
      setLatency(Math.floor(Math.random() * 15) + 35); // 35 to 50ms
      setThroughput(Number((Math.random() * 0.4 + 1.1).toFixed(2))); // 1.10 to 1.50
      
      // 3. Generate new alerts occasionally
      if (Math.random() > 0.8) {
        const possibleAlerts = [
          { msg: "Sudden heavy rainfall reported on NH-37. Speed limits reduced.", type: "warning" },
          { msg: "Landslide detected near Tura. Alternate routes activated.", type: "critical" },
          { msg: "Fleet #892 successfully rerouted around flood zone.", type: "success" },
          { msg: "Bridge structural warning at Brahmaputra crossing. Monitoring.", type: "warning" },
          { msg: "Clear weather detected ahead of Fleet #210. Resuming normal speed.", type: "success" }
        ];
        const randomAlert = possibleAlerts[Math.floor(Math.random() * possibleAlerts.length)];
        const newAlert = { 
          id: Date.now(), 
          time: "Just now", 
          ...randomAlert 
        };
        
        setLiveAlerts(prev => {
          const updated = [newAlert, ...prev];
          return updated.slice(0, 3).map((a, idx) => ({
            ...a,
            time: idx === 0 ? "Just now" : idx === 1 ? "1 min ago" : "Few mins ago"
          }));
        });
      }
    }, 2500);

    return () => clearInterval(simInterval);
  }, []);

  const stats = [
    { label: "Active Fleets", value: activeFleets.toLocaleString(), icon: <Radio size={32} className="text-emerald-500" /> },
    { label: "Hazards Avoided", value: hazardsAvoided.toLocaleString(), icon: <ShieldAlert size={32} className="text-amber-500" /> },
    { label: "Random Forest Accuracy", value: "94.8%", icon: <TrendingUp size={32} className="text-blue-500" /> }
  ];

  return (
    <div className="relative min-h-screen w-full flex flex-col pt-28 px-12 md:px-24 pb-16 font-sans text-white bg-slate-950">

      <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col gap-8">
        
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="flex flex-col gap-2"
        >
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <h1 className="text-5xl font-bold tracking-tight text-white">Command Center</h1>
            <span className="bg-blue-900/30 text-blue-400 border border-blue-500/30 text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded-full w-fit">
              Simulated Telemetry Demo
            </span>
          </div>
          <p className="text-lg text-slate-400 font-medium">Live Network Telemetry & ML Analytics</p>
        </motion.div>

        {/* Top Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat, i) => (
            <motion.div 
              key={stat.label}
              initial={{ opacity: 0, scale: 0.98 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ delay: i * 0.15, duration: 0.5 }}
              className="bg-white text-black p-8 rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] flex items-center gap-6"
            >
              <div className="p-4 bg-[#f5f5f7] rounded-2xl shrink-0 text-blue-600">
                {stat.icon}
              </div>
              <div className="flex flex-col">
                <span className="text-xs font-bold text-gray-500 tracking-wider uppercase mb-1">{stat.label}</span>
                <motion.span 
                  key={stat.value}
                  initial={{ opacity: 0.5, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-bold tracking-tight text-gray-900"
                >
                  {stat.value}
                </motion.span>
              </div>
            </motion.div>
          ))}
        </div>

        {/* ML Visualizations Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Risk Distribution */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="bg-white text-black p-8 rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] flex flex-col"
          >
            <h2 className="text-xl font-bold tracking-tight text-gray-900 mb-8 flex items-center gap-3">
              <PieChart className="text-blue-500" size={24} /> Risk Distribution
            </h2>
            <div className="flex flex-col gap-6 w-full">
              <div className="flex justify-between items-center font-bold text-lg">
                <span className="flex items-center gap-3 text-gray-700">
                  <div className="w-4 h-4 rounded-full bg-emerald-500"></div> Low Risk
                </span> 
                <span className="text-2xl">68%</span>
              </div>
              <div className="flex justify-between items-center font-bold text-lg">
                <span className="flex items-center gap-3 text-gray-700">
                  <div className="w-4 h-4 rounded-full bg-amber-500"></div> Moderate Risk
                </span> 
                <span className="text-2xl text-gray-900">23%</span>
              </div>
              <div className="flex justify-between items-center font-bold text-lg">
                <span className="flex items-center gap-3 text-gray-700">
                  <div className="w-4 h-4 rounded-full bg-red-500"></div> High Risk
                </span> 
                <span className="text-2xl text-gray-900">9%</span>
              </div>
              
              {/* Stacked Bar */}
              <div className="w-full h-3 rounded-full flex overflow-hidden mt-4 bg-gray-100">
                <motion.div initial={{width:0}} whileInView={{width:'68%'}} transition={{duration:1, ease:"easeOut"}} className="h-full bg-emerald-500"></motion.div>
                <motion.div initial={{width:0}} whileInView={{width:'23%'}} transition={{duration:1, ease:"easeOut"}} className="h-full bg-amber-500"></motion.div>
                <motion.div initial={{width:0}} whileInView={{width:'9%'}} transition={{duration:1, ease:"easeOut"}} className="h-full bg-red-500"></motion.div>
              </div>
            </div>
          </motion.div>

          {/* Route Analytics */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="bg-white text-black p-8 rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] flex flex-col"
          >
            <h2 className="text-xl font-bold tracking-tight text-gray-900 mb-6 flex items-center gap-3">
              <BarChart3 className="text-blue-500" size={24} /> Route Analytics
            </h2>
            
            {/* Simple Bar Chart */}
            <div className="flex-1 flex w-full h-48 pl-8 pt-4 pb-6 relative">
              {/* Y Axis Labels */}
              <div className="absolute left-0 top-4 bottom-6 w-8 flex flex-col justify-between text-xs font-bold text-gray-400 items-end pr-2">
                <span>100</span>
                <span>75</span>
                <span>50</span>
                <span>25</span>
                <span>0</span>
              </div>
              
              {/* Chart Area */}
              <div className="flex-1 flex items-end justify-around border-b border-l border-gray-200 h-full relative">
                {/* Grid Lines */}
                <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                  <div className="w-full h-px bg-gray-100"></div>
                  <div className="w-full h-px bg-gray-100"></div>
                  <div className="w-full h-px bg-gray-100"></div>
                  <div className="w-full h-px bg-gray-100"></div>
                  <div className="w-full h-px"></div>
                </div>

                <div className="relative flex flex-col items-center justify-end w-12 md:w-16 h-full group z-10">
                  <span className="absolute -top-6 text-gray-900 font-bold opacity-0 group-hover:opacity-100 transition-opacity">85</span>
                  <motion.div initial={{height:0}} whileInView={{height:'85%'}} transition={{duration:1, delay:0.2}} className="w-full bg-red-500 rounded-t-md"></motion.div>
                  <span className="absolute -bottom-7 text-xs text-gray-500 font-bold tracking-wider">Rt A</span>
                </div>
                <div className="relative flex flex-col items-center justify-end w-12 md:w-16 h-full group z-10">
                  <span className="absolute -top-6 text-gray-900 font-bold opacity-0 group-hover:opacity-100 transition-opacity">60</span>
                  <motion.div initial={{height:0}} whileInView={{height:'60%'}} transition={{duration:1, delay:0.3}} className="w-full bg-amber-500 rounded-t-md"></motion.div>
                  <span className="absolute -bottom-7 text-xs text-gray-500 font-bold tracking-wider">Rt B</span>
                </div>
                <div className="relative flex flex-col items-center justify-end w-12 md:w-16 h-full group z-10">
                  <span className="absolute -top-6 text-gray-900 font-bold opacity-0 group-hover:opacity-100 transition-opacity">40</span>
                  <motion.div initial={{height:0}} whileInView={{height:'40%'}} transition={{duration:1, delay:0.4}} className="w-full bg-blue-500 rounded-t-md"></motion.div>
                  <span className="absolute -bottom-7 text-xs text-gray-500 font-bold tracking-wider">Rt C</span>
                </div>
                <div className="relative flex flex-col items-center justify-end w-12 md:w-16 h-full group z-10">
                  <span className="absolute -top-6 text-gray-900 font-bold opacity-0 group-hover:opacity-100 transition-opacity">20</span>
                  <motion.div initial={{height:0}} whileInView={{height:'20%'}} transition={{duration:1, delay:0.5}} className="w-full bg-emerald-500 rounded-t-md"></motion.div>
                  <span className="absolute -bottom-7 text-xs text-gray-500 font-bold tracking-wider">Rt D</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
          
          {/* Live Map / ML Graph Placeholder */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="bg-white text-black rounded-3xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.04)] flex flex-col"
          >
            <div className="flex items-center gap-3 mb-6">
              <Activity size={24} className="text-blue-500" />
              <h2 className="text-xl font-bold tracking-tight text-gray-900">System Status</h2>
            </div>
            
            <div className="flex-1 bg-[#f5f5f7] rounded-3xl flex flex-col items-center justify-center p-8 text-center min-h-[250px]">
              <div className="relative w-24 h-24 mb-6">
                <div className="absolute inset-0 border-4 border-emerald-500/20 rounded-full animate-ping"></div>
                <div className="absolute inset-0 border-4 border-emerald-400 rounded-full border-t-transparent animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center bg-white rounded-full m-2 shadow-sm">
                  <span className="font-bold text-lg text-emerald-600">OK</span>
                </div>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">Neural Engine Online</h3>
              <p className="text-gray-500 font-medium max-w-sm text-sm">
                Latency: <span className="text-blue-600 font-bold">{latency}ms</span> | 
                Throughput: <span className="text-blue-600 font-bold">{throughput}GB/s</span>
              </p>
            </div>
          </motion.div>

          {/* Active Alerts Feed */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="bg-white text-black rounded-3xl p-8 shadow-[0_8px_30px_rgba(0,0,0,0.04)] flex flex-col"
          >
            <h2 className="text-xl font-bold tracking-tight text-gray-900 mb-6 flex items-center gap-3">
              <AlertTriangle className="text-red-500" size={24} /> Live Incident Feed
            </h2>
            
            <div className="flex flex-col gap-3 overflow-hidden flex-1 min-h-[250px]">
              <AnimatePresence>
                {liveAlerts.map(alert => (
                  <motion.div 
                    key={alert.id}
                    initial={{ opacity: 0, height: 0, x: 20 }}
                    animate={{ opacity: 1, height: 'auto', x: 0 }}
                    exit={{ opacity: 0, height: 0, x: -20 }}
                    className={`p-4 rounded-2xl flex gap-4 ${
                      alert.type === 'critical' ? 'bg-red-50 text-red-900' : 
                      alert.type === 'warning' ? 'bg-amber-50 text-amber-900' : 'bg-emerald-50 text-emerald-900'
                    }`}
                  >
                    <div className="shrink-0 mt-0.5">
                      {alert.type === 'critical' && <AlertTriangle size={18} className="text-red-500" />}
                      {alert.type === 'warning' && <AlertTriangle size={18} className="text-amber-500" />}
                      {alert.type === 'success' && <CheckCircle2 size={18} className="text-emerald-500" />}
                    </div>
                    <div>
                      <p className={`text-xs font-bold uppercase tracking-wider mb-0.5 ${
                        alert.type === 'critical' ? 'text-red-400' : 
                        alert.type === 'warning' ? 'text-amber-400' : 'text-emerald-400'
                      }`}>{alert.time}</p>
                      <p className="text-sm font-medium">{alert.msg}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
