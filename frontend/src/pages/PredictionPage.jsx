import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReviewInput from '../components/ReviewInput';
import HighlightText from '../components/HighlightText';
import { predictReview } from '../services/api';
import { ShieldAlert, ShieldCheck, Shield, AlertTriangle } from 'lucide-react';

const PredictionPage = () => {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async (text) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predictReview(text);
      setResult(data);
    } catch (err) {
      setError('Failed to analyze the review. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskDetails = (risk) => {
    switch (risk) {
      case 'Low Risk': return { color: 'text-emerald-400', glow: 'shadow-[0_0_50px_rgba(16,185,129,0.3)]', border: 'border-emerald-400/50', icon: ShieldCheck };
      case 'Medium Risk': return { color: 'text-amber-400', glow: 'shadow-[0_0_50px_rgba(245,158,11,0.3)]', border: 'border-amber-400/50', icon: Shield };
      case 'High Risk': return { color: 'text-rose-500', glow: 'shadow-[0_0_50px_rgba(244,63,94,0.4)]', border: 'border-rose-500/50', icon: ShieldAlert };
      default: return { color: 'text-gray-400', glow: 'shadow-lg', border: 'border-white/10', icon: Shield };
    }
  };

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 }
  };

  return (
    <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.5 }} className="p-8 lg:p-12 w-full max-w-5xl mx-auto">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-purple-100 to-indigo-300 inline-block mb-2">Deep Analyze Review</h1>
        <p className="text-purple-300/70 text-lg">Harness transformer attention heads to decode semantic risk factors instantly.</p>
      </div>

      <div className="mb-10 w-full max-w-4xl mx-auto">
        <ReviewInput onSubmit={handlePredict} isLoading={isLoading} />
      </div>

      <AnimatePresence>
        {error && (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="bg-rose-500/10 text-rose-300 p-4 rounded-xl flex items-center justify-center space-x-3 mb-10 border border-rose-500/30 backdrop-blur-md shadow-[0_0_15px_rgba(244,63,94,0.2)]">
            <AlertTriangle size={22} className="animate-pulse" />
            <span className="font-semibold tracking-wide">{error}</span>
          </motion.div>
        )}

        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ type: "spring", stiffness: 100, damping: 20 }}
            className={`glass-card overflow-hidden relative ${getRiskDetails(result.risk_level).glow}`}
          >
            <div className={`absolute top-0 left-0 w-1 h-full ${getRiskDetails(result.risk_level).color.replace('text', 'bg')} drop-shadow-[0_0_10px_currentColor]`} />
            
            <div className="grid grid-cols-1 md:grid-cols-3">
              {/* Score Display (Left) */}
              <div className="p-10 flex flex-col items-center justify-center text-center border-b md:border-b-0 md:border-r border-white/5 relative overflow-hidden group">
                <div className={`absolute inset-0 bg-gradient-to-b ${result.risk_level === 'High Risk' ? 'from-rose-500/5' : 'from-emerald-500/5'} to-transparent`} />
                <p className="text-sm font-bold text-gray-400 uppercase tracking-[0.2em] mb-4">Trust Factor</p>
                
                <div className="relative flex items-center justify-center mb-8 perspective-1000">
                   {React.createElement(getRiskDetails(result.risk_level).icon, { 
                     size: 160, 
                     className: `${getRiskDetails(result.risk_level).color} opacity-10 absolute filter blur-md transform group-hover:scale-110 transition-transform duration-700` 
                   })}
                   <motion.span 
                     initial={{ scale: 0 }}
                     animate={{ scale: 1 }}
                     transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                     className={`text-8xl font-black ${getRiskDetails(result.risk_level).color} z-10 relative drop-shadow-2xl font-mono`}
                   >
                     {result.trust_score}
                   </motion.span>
                </div>
                
                <div className={`inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl border bg-black/40 ${getRiskDetails(result.risk_level).border} shadow-lg backdrop-blur-md`}>
                  {React.createElement(getRiskDetails(result.risk_level).icon, { size: 20, className: getRiskDetails(result.risk_level).color })}
                  <span className={`text-base font-black uppercase tracking-wider ${getRiskDetails(result.risk_level).color}`}>{result.risk_level}</span>
                </div>
              </div>

              {/* Analysis Display (Right) */}
              <div className="p-10 md:col-span-2 flex flex-col bg-black/10">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center space-x-2">
                  <Shield size={20} className="text-purple-400" />
                  <span>Explainable AI Insights</span>
                </h3>
                
                {/* Progress */}
                <div className="mb-8 p-6 glass-card bg-black/20">
                  <div className="flex justify-between text-sm mb-3">
                    <span className="text-gray-300 font-semibold tracking-wide">Deception Probability</span>
                    <span className="text-rose-400 font-black">{(result.fake_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-3 overflow-hidden shadow-inner border border-white/5">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${result.fake_probability * 100}%` }}
                      transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
                      className="h-full rounded-full bg-gradient-to-r from-rose-600 to-rose-400 relative"
                    >
                       <div className="absolute top-0 right-0 bottom-0 w-20 bg-gradient-to-r from-transparent to-white/30 truncate"></div>
                    </motion.div>
                  </div>
                </div>

                {/* Highlight text */}
                <div className="flex-1 flex flex-col">
                  <h4 className="text-sm font-semibold text-purple-300/80 uppercase tracking-widest mb-3">Contextual Analysis</h4>
                  <div className="flex-1 glass-card bg-black/30 p-6 !rounded-xl overflow-y-auto max-h-[300px] border border-white/10 shadow-inner">
                    <HighlightText text={result.text} importantWords={result.important_words} />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default PredictionPage;
