import React from 'react';

const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const isWordLikeToken = (value) => /^[A-Za-z0-9_']+$/.test(value);

const buildTokenPattern = (token) => {
  const escaped = escapeRegex(token);
  if (!isWordLikeToken(token)) {
    return escaped;
  }

  // Allow common inflections so model tokens like "cool" can still match "cools"/"cooling".
  if (token.length >= 4) {
    return `\\b${escaped}(?:s|es|ed|ing)?\\b`;
  }

  return `\\b${escaped}\\b`;
};

const collectHighlights = (text, importantWords) => {
  if (!text || !importantWords?.length) return [];

  const candidates = importantWords
    .filter((item) => Array.isArray(item) && item.length >= 2)
    .map(([word, weight]) => ({
      word: String(word ?? '').trim(),
      weight: Number(weight) || 0,
    }))
    .filter((item) => item.word.length > 0)
    .sort((a, b) => b.word.length - a.word.length || b.weight - a.weight);

  const allMatches = [];

  for (const item of candidates) {
    const pattern = buildTokenPattern(item.word);
    const regex = new RegExp(pattern, 'gi');

    let match;
    while ((match = regex.exec(text)) !== null) {
      allMatches.push({
        start: match.index,
        end: match.index + match[0].length,
        weight: item.weight,
      });

      if (regex.lastIndex === match.index) {
        regex.lastIndex += 1;
      }
    }
  }

  const occupied = new Array(text.length).fill(false);
  const selected = [];

  for (const match of allMatches) {
    let overlaps = false;
    for (let i = match.start; i < match.end; i += 1) {
      if (occupied[i]) {
        overlaps = true;
        break;
      }
    }

    if (overlaps) continue;

    for (let i = match.start; i < match.end; i += 1) {
      occupied[i] = true;
    }
    selected.push(match);
  }

  return selected.sort((a, b) => a.start - b.start);
};

const HighlightText = ({ text, importantWords }) => {
  if (!text) return null;
  if (!importantWords || importantWords.length === 0) return <span className="text-gray-300">{text}</span>;

  const highlights = collectHighlights(text, importantWords);

  if (highlights.length === 0) {
    return <span className="text-gray-300">{text}</span>;
  }

  const parts = [];
  let cursor = 0;

  for (const match of highlights) {
    if (cursor < match.start) {
      parts.push({ type: 'plain', text: text.slice(cursor, match.start) });
    }
    parts.push({
      type: 'highlight',
      text: text.slice(match.start, match.end),
      weight: match.weight,
    });
    cursor = match.end;
  }

  if (cursor < text.length) {
    parts.push({ type: 'plain', text: text.slice(cursor) });
  }

  return (
    <div className="leading-relaxed text-lg text-gray-300 font-light">
      {parts.map((part, index) => {
        if (part.type === 'highlight') {
          const weight = part.weight;
          let styleClasses = 'bg-yellow-500/20 text-yellow-300 border-b border-yellow-400/50';
          if (weight > 0.8) {
            styleClasses = 'bg-rose-500/30 text-rose-300 border-b-2 border-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.3)] font-medium animate-pulse';
          } else if (weight > 0.5) {
            styleClasses = 'bg-amber-500/20 text-amber-300 border-b border-amber-400 font-normal shadow-[0_0_8px_rgba(245,158,11,0.2)]';
          }

          return (
            <span
              key={index}
              className={`px-1 rounded-t-sm transition-all duration-300 ${styleClasses}`}
            >
              {part.text}
            </span>
          );
        }

        return <span key={index} className="px-[1px]">{part.text}</span>;
      })}
    </div>
  );
};

export default HighlightText;
