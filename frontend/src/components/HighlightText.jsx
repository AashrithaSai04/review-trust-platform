import React from 'react';

const HighlightText = ({ text, importantWords }) => {
  if (!text) return null;
  if (!importantWords || importantWords.length === 0) return <span className="text-gray-300">{text}</span>;

  const wordMap = new Map(importantWords.map(([word, weight]) => [word.toLowerCase(), weight]));
  const tokens = text.split(/(\b[\w']+\b)/g);

  return (
    <div className="leading-relaxed text-lg text-gray-300 font-light">
      {tokens.map((token, index) => {
        const lowerToken = token.toLowerCase();
        const weight = wordMap.get(lowerToken);

        if (weight !== undefined) {
          let styleClasses = 'bg-yellow-500/20 text-yellow-300 border-b border-yellow-400/50';
          if (weight > 0.8) {
            styleClasses = 'bg-rose-500/30 text-rose-300 border-b-2 border-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.3)] font-medium animate-pulse';
          } else if (weight > 0.5) {
            styleClasses = 'bg-amber-500/20 text-amber-300 border-b border-amber-400 font-normal shadow-[0_0_8px_rgba(245,158,11,0.2)]';
          }

          return (
            <span
              key={index}
              className={`relative group px-1 rounded-t-sm cursor-crosshair transition-all duration-300 hover:bg-opacity-50 ${styleClasses}`}
            >
              {token}
              <span className="absolute bottom-[110%] left-1/2 -translate-x-1/2 mb-1 px-3 py-1.5 text-xs font-bold text-white bg-slate-800 rounded-lg opacity-0 -translate-y-2 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-200 whitespace-nowrap z-50 shadow-xl border border-white/10 backdrop-blur-md pointer-events-none">
                AI Score: {(weight * 100).toFixed(0)}%
                <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-slate-800"></div>
              </span>
            </span>
          );
        }

        return <span key={index} className="px-[1px]">{token}</span>;
      })}
    </div>
  );
};

export default HighlightText;
