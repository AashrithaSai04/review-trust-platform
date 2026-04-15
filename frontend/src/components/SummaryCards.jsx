import React from 'react';
import { ShieldCheck, AlertTriangle, FileText, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const Card = ({ title, value, icon: Icon, colorClass, subtitle, delay }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: delay }}
    whileHover={{ y: -5, scale: 1.02 }}
    className="glass-card p-6 flex items-start space-x-5 transition-all duration-300 hover:bg-white/10 group cursor-default relative overflow-hidden"
  >
    <div className={`absolute -right-10 -top-10 w-32 h-32 rounded-full blur-3xl opacity-20 group-hover:opacity-40 transition-opacity duration-500 bg-current ${colorClass}`}></div>
    
    <div className={`p-4 rounded-2xl flex items-center justify-center border border-white/10 shadow-lg ${colorClass} bg-white/5 backdrop-blur-md relative z-10`}>
      <Icon size={26} className="text-current drop-shadow-md" />
    </div>
    <div className="relative z-10">
      <p className="text-sm font-semibold text-gray-400 tracking-wide uppercase">{title}</p>
      <h3 className="text-3xl font-black text-white mt-1 drop-shadow-md">{value}</h3>
      {subtitle && <p className="text-[11px] font-medium text-emerald-400 mt-2">{subtitle}</p>}
    </div>
  </motion.div>
);

const SummaryCards = ({ data }) => {
  const stats = data || {
    total: 12450,
    avgTrust: 87,
    fakePercent: 12.4,
    highRisk: 342
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      <Card
        delay={0.1}
        title="Total Reviews"
        value={stats.total.toLocaleString()}
        icon={FileText}
        colorClass="text-blue-400"
        subtitle="+12% from last week"
      />
      <Card
        delay={0.2}
        title="Avg Trust Score"
        value={`${stats.avgTrust}/100`}
        icon={ShieldCheck}
        colorClass="text-emerald-400"
        subtitle="Healthy Platform Status"
      />
      <Card
        delay={0.3}
        title="Fake Probability"
        value={`${stats.fakePercent}%`}
        icon={Activity}
        colorClass="text-amber-400"
        subtitle="-2% anomaly detection"
      />
      <Card
        delay={0.4}
        title="High Risk Count"
        value={stats.highRisk.toLocaleString()}
        icon={AlertTriangle}
        colorClass="text-rose-400"
        subtitle="Requires immediate action"
      />
    </div>
  );
};

export default SummaryCards;
