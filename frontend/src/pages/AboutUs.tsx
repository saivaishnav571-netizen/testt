import React from 'react';
import { motion } from 'framer-motion';
import { Shield, BrainCircuit, Globe2, Truck } from 'lucide-react';

export default function AboutUs() {
  const values = [
    {
      icon: <BrainCircuit size={32} className="text-blue-500" />,
      title: "Predictive Intelligence",
      desc: "We leverage a 19-feature Random Forest model to analyze terrain gradients, flood histories, and infrastructure weak points before disasters strike."
    },
    {
      icon: <Shield size={32} className="text-emerald-500" />,
      title: "Resilient Supply Chains",
      desc: "When natural disasters disrupt traditional routes, our spatial algorithms instantly reroute critical supplies to ensure zero downtime in crisis zones."
    },
    {
      icon: <Globe2 size={32} className="text-amber-500" />,
      title: "Spatial Mapping",
      desc: "By integrating real-time KDTree spatial querying, we match your fleets to the safest possible roads with millimeter precision."
    },
    {
      icon: <Truck size={32} className="text-red-500" />,
      title: "Dynamic Fleet Allocation",
      desc: "We don't just find the route; we recommend the exact vehicle type—from Heavy Duty 4x4s to nimble supply vans—needed to survive it."
    }
  ];

  return (
    <div className="w-full min-h-screen bg-slate-950 text-white relative pt-32 px-8 pb-16">
      <div className="max-w-7xl mx-auto flex flex-col gap-16 relative z-10">
        
        {/* Hero Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white mb-6 leading-[1.1]">
            Engineering resilience for a <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">volatile world.</span>
          </h1>
          <p className="text-xl text-slate-400 font-medium leading-relaxed">
            Built for SIH Hackathon 2k26, our platform merges cutting-edge spatial AI with real-time logistics networks. We ensure that critical supplies reach their destinations, no matter what nature throws in the way.
          </p>
        </motion.div>

        {/* Values Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
          {values.map((val, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ delay: idx * 0.15, duration: 0.5 }}
              className="bg-white text-black p-10 rounded-[2rem] shadow-[0_8px_30px_rgba(0,0,0,0.06)] flex flex-col items-start gap-4"
            >
              <div className="p-4 bg-[#f5f5f7] rounded-2xl">
                {val.icon}
              </div>
              <h2 className="text-2xl font-bold tracking-tight text-gray-900 mt-2">{val.title}</h2>
              <p className="text-gray-600 font-medium leading-relaxed">
                {val.desc}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="w-full bg-gradient-to-br from-blue-600 to-blue-900 rounded-[2rem] p-12 text-center mt-8 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
          <h2 className="text-3xl md:text-5xl font-black tracking-tight text-white mb-6 relative z-10">
            Ready to secure your logistics?
          </h2>
          <button className="bg-white text-blue-900 font-bold tracking-wide px-8 py-4 rounded-2xl shadow-lg hover:shadow-xl transition-all relative z-10 hover:scale-105">
            Access The Platform
          </button>
        </motion.div>

      </div>
    </div>
  );
}

