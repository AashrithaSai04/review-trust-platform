import React, { useState } from 'react';
import HighlightText from './HighlightText';
import { Search, ChevronLeft, ChevronRight, CheckCircle, Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ReviewTable = ({ reviews, isLoading, isModeration = false, onMarkSafe, onDelete }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="animate-pulse bg-white/5 border border-white/5 h-24 rounded-2xl w-full"></div>
        ))}
      </div>
    );
  }

  if (!reviews || reviews.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400 glass-card">
        <div className="mx-auto w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
          <Search size={24} className="text-gray-500" />
        </div>
        <p className="text-lg">No reviews found to display.</p>
      </div>
    );
  }

  const filteredReviews = reviews.filter(rev => 
    rev.text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredReviews.length / itemsPerPage);
  const paginatedReviews = filteredReviews.slice(
    (currentPage - 1) * itemsPerPage, 
    currentPage * itemsPerPage
  );

  const getRiskBadge = (risk) => {
    switch (risk) {
      case 'Low Risk': return 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
      case 'Medium Risk': return 'bg-amber-500/10 text-amber-300 border-amber-500/30';
      case 'High Risk': return 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-[0_0_10px_rgba(244,63,94,0.3)]';
      default: return 'bg-white/10 text-gray-300 border-white/20';
    }
  };

  return (
    <div className="glass-card overflow-hidden text-gray-200">
      <div className="p-5 border-b border-white/10 flex justify-between items-center bg-black/20">
        <div className="relative w-72">
          <input 
            type="text" 
            placeholder="Search within reviews..." 
            className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 text-sm text-white placeholder:text-gray-500 transition-all"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
          />
          <Search className="absolute left-3.5 top-3 text-gray-400" size={18} />
        </div>
        {isModeration && (
          <span className="text-sm font-bold text-rose-300 bg-rose-500/20 px-4 py-1.5 rounded-full border border-rose-500/30 shadow-[0_0_10px_rgba(244,63,94,0.2)]">
            Action Required
          </span>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-black/30 text-gray-400 border-b border-white/10 uppercase tracking-wider text-xs font-semibold">
            <tr>
              <th className="px-6 py-5 w-full max-w-sm block">Review Content</th>
              <th className="px-6 py-5">Trust Score</th>
              <th className="px-6 py-5">Risk Level</th>
              {isModeration && <th className="px-6 py-5 text-right">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 bg-black/10">
            {paginatedReviews.map((review, i) => (
              <motion.tr 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                key={review.id || i} 
                className={`hover:bg-white/5 transition-colors ${isModeration ? 'hover:bg-rose-900/10' : ''}`}
              >
                <td className="px-6 py-5 max-w-sm whitespace-normal">
                  <HighlightText text={review.text} importantWords={review.important_words} />
                </td>
                <td className="px-6 py-5">
                  <div className="flex items-center space-x-2 bg-black/30 w-16 px-2 py-1.5 rounded-lg border border-white/5">
                    <span className="font-bold text-white text-base">{review.trust_score}</span>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <span className={`px-3 py-1.5 text-xs font-bold rounded-xl border ${getRiskBadge(review.risk_level)} tracking-wide`}>
                    {review.risk_level}
                  </span>
                </td>
                {isModeration && (
                  <td className="px-6 py-5 text-right">
                    <div className="flex justify-end space-x-3">
                      <button onClick={() => onMarkSafe && onMarkSafe(review.id)} className="p-2 text-emerald-400 hover:bg-emerald-400/20 rounded-lg transition-all border border-transparent hover:border-emerald-500/30" title="Mark as Safe">
                        <CheckCircle size={18} />
                      </button>
                      <button onClick={() => onDelete && onDelete(review.id)} className="p-2 text-rose-400 hover:bg-rose-400/20 rounded-lg transition-all border border-transparent hover:border-rose-500/30" title="Delete Review">
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                )}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="px-6 py-5 border-t border-white/10 flex justify-between items-center text-sm text-gray-400 bg-black/20">
          <span>Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredReviews.length)} of {filteredReviews.length} entries</span>
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-white"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="px-4 font-semibold text-white">Pg {currentPage} of {totalPages}</span>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-white"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewTable;
