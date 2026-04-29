import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReviewTable from '../components/ReviewTable';
import { uploadCSV } from '../services/api';
import { UploadCloud, File, AlertCircle, Loader2 } from 'lucide-react';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [xaiMethod, setXaiMethod] = useState('attention');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type === 'text/csv' || selected?.name.endsWith('.csv')) {
      setFile(selected);
      setError(null);
    } else if (selected) {
      setFile(null);
      setError('Please upload a valid CSV file.');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedInfo = e.dataTransfer.files[0];
    if (droppedInfo && droppedInfo.type === 'text/csv' || droppedInfo?.name.endsWith('.csv')) {
      setFile(droppedInfo);
      setError(null);
    } else {
      setError('Please upload a valid CSV file.');
    }
  };

  const processFile = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await uploadCSV(file, xaiMethod);
      setResults(data);
    } catch (err) {
      setError(err.message || 'Failed to process the uploaded file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const pageVariants = {
    initial: { opacity: 0, scale: 0.98 },
    in: { opacity: 1, scale: 1 },
    out: { opacity: 0, scale: 0.98 }
  };

  return (
    <motion.div initial="initial" animate="in" exit="out" variants={pageVariants} transition={{ duration: 0.5 }} className="p-8 lg:p-12 w-full max-w-6xl mx-auto">
      <div className="mb-10">
        <h1 className="text-4xl font-black text-white">Batch Analyzer</h1>
        <p className="text-gray-400 mt-2 text-lg">Process thousands of reviews instantly by uploading a CSV payload.</p>
      </div>

      <div className="grid grid-cols-1 gap-10">
        <div className="glass-card p-1">
          <div className="bg-black/20 rounded-[15px] p-8 md:p-12">
            <div 
              className={`border-2 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center transition-all duration-300 relative overflow-hidden group cursor-pointer ${
                file ? 'border-purple-500/50 bg-gradient-to-b from-purple-500/10 to-transparent' : 'border-white/20 hover:border-purple-500/70 hover:bg-white/5'
              }`}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              
              <input 
                type="file" 
                accept=".csv" 
                className="hidden" 
                ref={fileInputRef} 
                onChange={handleFileChange}
              />
              
              <AnimatePresence mode="wait">
                {file ? (
                  <motion.div key="file" initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }} className="text-center relative z-10">
                    <div className="mx-auto w-20 h-20 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(168,85,247,0.4)]">
                      <File size={36} className="text-white drop-shadow-md" />
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2">{file.name}</h3>
                    <p className="text-purple-300 font-medium font-mono bg-black/30 inline-block px-4 py-1 rounded-full">{(file.size / 1024).toFixed(2)} KB • Ready to process</p>
                  </motion.div>
                ) : (
                  <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center relative z-10">
                    <div className="mx-auto w-20 h-20 bg-white/5 border border-white/10 rounded-full flex items-center justify-center mb-6 transition-transform group-hover:scale-110 duration-500 group-hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]">
                      <UploadCloud size={36} className="text-gray-400 group-hover:text-purple-400 transition-colors" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">Drag and drop your payload</h3>
                    <p className="text-gray-400">CSV files only. Must contain a "text" column.</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {error && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-6 flex items-center justify-center space-x-3 text-rose-300 bg-rose-500/10 p-4 rounded-xl text-sm font-semibold border border-rose-500/20">
                <AlertCircle size={18} />
                <span>{error}</span>
              </motion.div>
            )}

            <div className="mt-8 flex justify-center">
               <div className="w-full max-w-md mb-6">
                 <label htmlFor="xai-method" className="block text-sm font-semibold text-gray-300 mb-2 text-center">Explanation Method</label>
                 <select
                   id="xai-method"
                   value={xaiMethod}
                   onChange={(e) => setXaiMethod(e.target.value)}
                   className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20"
                 >
                   <option value="attention" className="text-black">Attention</option>
                   <option value="shap" className="text-black">SHAP</option>
                 </select>
                 <p className="text-xs text-gray-500 mt-2 text-center">SHAP can be slower but usually gives more meaningful token importance.</p>
               </div>
            </div>

            <div className="flex justify-center">
               <button
                  onClick={(e) => { e.stopPropagation(); processFile(); }}
                  disabled={!file || isLoading}
                  className="flex items-center space-x-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-gray-500 disabled:cursor-not-allowed text-white px-10 py-4 rounded-xl font-bold shadow-[0_0_20px_rgba(168,85,247,0.3)] hover:shadow-[0_0_30px_rgba(168,85,247,0.5)] transform hover:-translate-y-1 transition-all duration-300"
                >
                  {isLoading ? (
                    <>
                      <Loader2 size={22} className="animate-spin text-white" />
                      <span className="tracking-widest uppercase">Processing Array...</span>
                    </>
                  ) : (
                    <span className="tracking-widest uppercase">Analyze Payload</span>
                  )}
                </button>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {(results || isLoading) && (
            <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 30 }} transition={{ duration: 0.6 }} className="w-full">
              <div className="flex items-center space-x-3 mb-6">
                 <div className="w-2 h-6 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                 <h2 className="text-2xl font-bold text-white">Analysis Output</h2>
              </div>
              <ReviewTable reviews={results} isLoading={isLoading} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default UploadPage;
