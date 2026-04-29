import React, { useState } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const ReviewInput = ({ onSubmit, isLoading }) => {
  const [text, setText] = useState('');
  const [verifiedPurchase, setVerifiedPurchase] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !isLoading) {
      onSubmit(text, verifiedPurchase);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full relative group">
      <motion.div 
        whileHover={{ scale: 1.01 }}
        transition={{ type: "spring", stiffness: 300 }}
        className="relative glass-card bg-black/20 focus-within:bg-black/40 border border-white/10 focus-within:border-purple-500/50 focus-within:ring-4 focus-within:ring-purple-500/20 transition-all duration-300"
      >
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a review here to analyze its trust score using our advanced AI model..."
          className="w-full min-h-[160px] p-6 bg-transparent resize-none outline-none text-white placeholder:text-gray-500 text-lg leading-relaxed focus:ring-0"
          disabled={isLoading}
        />
        <div className="absolute bottom-5 right-5">
          <button
            type="submit"
            disabled={!text.trim() || isLoading}
            className="flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:from-slate-700 disabled:to-slate-800 disabled:cursor-not-allowed text-white px-8 py-3 rounded-xl font-bold shadow-[0_0_15px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(168,85,247,0.6)] transform hover:-translate-y-0.5 transition-all duration-300"
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin text-white" />
                <span className="tracking-wide">Analyzing AI...</span>
              </>
            ) : (
              <>
                <Sparkles size={18} className="text-purple-200" />
                <span className="tracking-wide">Analyze Review</span>
                <Send size={18} className="ml-1 opacity-70" />
              </>
            )}
          </button>
        </div>

        <label className="absolute bottom-6 left-6 flex items-center gap-2 text-sm text-gray-300 select-none">
          <input
            type="checkbox"
            checked={verifiedPurchase}
            onChange={(e) => setVerifiedPurchase(e.target.checked)}
            disabled={isLoading}
            className="h-4 w-4 rounded border-white/20 bg-black/40 text-emerald-500 focus:ring-emerald-500"
          />
          Verified purchase
        </label>
      </motion.div>
    </form>
  );
};

export default ReviewInput;
