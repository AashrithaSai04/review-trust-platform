import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import SummaryCards from '../components/SummaryCards';
import { FakeVsGenuineChart, TrustScoreDistributionChart, TrendChart } from '../components/Charts';
import { getDashboardStats } from '../services/api';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const stats = await getDashboardStats();
        setData(stats);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
        setData(null); // Will use defaults in SummaryCards
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 }
  };

  if (isLoading) {
    return (
      <div className="p-8 lg:p-12 w-full max-w-screen-2xl mx-auto space-y-8">
        <div className="h-10 w-72 bg-white/10 animate-pulse rounded-lg border border-white/5"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-40 bg-white/5 border border-white/5 animate-pulse rounded-2xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           <div className="h-72 bg-white/5 border border-white/5 animate-pulse rounded-2xl" />
           <div className="h-72 bg-white/5 border border-white/5 animate-pulse rounded-2xl lg:col-span-2" />
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.5 }}
      className="p-8 lg:p-12 w-full max-w-screen-2xl mx-auto"
    >
      <div className="mb-10">
        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-indigo-300">
          Platform Overview
        </h1>
        <p className="text-purple-300/80 mt-2 text-lg font-medium tracking-wide">Real-time AI evaluation and risk metrics.</p>
      </div>

      <SummaryCards />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3, duration: 0.5 }}>
          <FakeVsGenuineChart />
        </motion.div>
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4, duration: 0.5 }} className="lg:col-span-2 relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-20 object-cover"></div>
          <div className="relative h-full"><TrustScoreDistributionChart /></div>
        </motion.div>
      </div>
      
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5, duration: 0.5 }} className="mt-6 relative">
         <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 rounded-2xl blur opacity-10"></div>
         <div className="relative h-full"><TrendChart /></div>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
