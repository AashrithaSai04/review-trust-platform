import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReviewTable from '../components/ReviewTable';
import { getModerationData } from '../services/api';
import { ShieldAlert, Info } from 'lucide-react';

const ModerationPage = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchModeration();
  }, []);

  const fetchModeration = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await getModerationData();
      setData(res);
    } catch (error) {
      console.error("Failed to fetch moderation queue:", error);
      setError(error.message || 'Failed to fetch moderation queue.');
      setData([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkSafe = (id) => {
    setData(prev => prev.filter(item => item.id !== id));
  };

  const handleDelete = (id) => {
    setData(prev => prev.filter(item => item.id !== id));
  };

  const pageVariants = {
    initial: { opacity: 0, x: 20 },
    in: { opacity: 1, x: 0 },
    out: { opacity: 0, x: -20 }
  };

  return (
    <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.5 }} className="p-8 lg:p-12 w-full max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-10">
        <div>
          <div className="flex items-center space-x-4">
            <h1 className="text-4xl font-black text-white">Trust Queue</h1>
            <motion.div 
               initial={{ scale: 0 }}
               animate={{ scale: 1 }}
               transition={{ type: "spring", stiffness: 300, delay: 0.3 }}
               className="bg-rose-500/20 text-rose-400 px-4 py-1.5 rounded-full text-sm font-bold font-mono border border-rose-500/30 shadow-[0_0_15px_rgba(244,63,94,0.3)] flex items-center space-x-2"
            >
              <div className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></div>
              <span>{data ? data.length : 0} CRITICAL PENDING</span>
            </motion.div>
          </div>
          <p className="text-gray-400 mt-2 text-lg">Manually review AI-flagged vulnerabilities in incoming data.</p>
        </div>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card bg-indigo-900/20 border-indigo-500/30 p-6 mb-10 flex items-start space-x-4 shadow-[0_0_30px_rgba(99,102,241,0.1)] relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-400 to-purple-500 shadow-[0_0_10px_currentColor]"></div>
        <Info className="text-indigo-400 mt-0.5 flex-shrink-0" size={24} />
        <div className="text-sm text-indigo-100/80">
          <p className="font-bold mb-1 text-indigo-300 text-base tracking-wide uppercase">System Protocol Active</p>
          <p className="leading-relaxed">These records triggered maximum threshold parameters within the deep learning engine. You must manually override or permanently excise the records from the origin database.</p>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="w-full">
         {error && (
           <div className="mb-6 bg-rose-500/10 text-rose-200 border border-rose-500/30 rounded-xl px-4 py-3 text-sm font-medium">
             {error}
           </div>
         )}
         <ReviewTable 
           reviews={data} 
           isLoading={isLoading} 
           isModeration={true} 
           onMarkSafe={handleMarkSafe}
           onDelete={handleDelete}
         />
      </motion.div>
    </motion.div>
  );
};

export default ModerationPage;
