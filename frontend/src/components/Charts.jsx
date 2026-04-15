import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const COLORS = ['#a855f7', '#fb7185', '#38bdf8'];

export const FakeVsGenuineChart = ({ data }) => {
  const chartData = data || [
    { name: 'Genuine', value: 87.6 },
    { name: 'Fake', value: 12.4 },
  ];

  return (
    <div className="glass-card p-6 flex flex-col h-full hover:bg-white/[0.07] transition-all duration-300">
      <h3 className="text-lg font-bold text-white mb-6">Prediction Breakdown</h3>
      <div className="flex-1 w-full min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={95}
              paddingAngle={6}
              dataKey="value"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth={2}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === 0 ? COLORS[0] : COLORS[1]} />
              ))}
            </Pie>
            <RechartsTooltip 
              formatter={(value) => `${value}%`}
              contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', backdropFilter: 'blur(10px)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
              itemStyle={{ color: '#fff' }}
            />
            <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#cbd5e1' }}/>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const TrustScoreDistributionChart = ({ data }) => {
  const chartData = data || [
    { range: '0-20', count: 450 },
    { range: '21-40', count: 800 },
    { range: '41-60', count: 1200 },
    { range: '61-80', count: 4500 },
    { range: '81-100', count: 5500 },
  ];

  return (
    <div className="glass-card p-6 flex flex-col h-full lg:col-span-2 hover:bg-white/[0.07] transition-all duration-300">
      <h3 className="text-lg font-bold text-white mb-6">Trust Score Distribution</h3>
      <div className="flex-1 w-full min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <RechartsTooltip 
               cursor={{ fill: 'rgba(255,255,255,0.05)' }}
               contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', backdropFilter: 'blur(10px)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
            />
            <Bar dataKey="count" fill="url(#colorCount)" radius={[6, 6, 0, 0]} />
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity={1}/>
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.6}/>
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const TrendChart = ({ data }) => {
  const chartData = data || [
    { day: 'Mon', fake: 45, genuine: 800 },
    { day: 'Tue', fake: 52, genuine: 950 },
    { day: 'Wed', fake: 38, genuine: 1100 },
    { day: 'Thu', fake: 65, genuine: 1050 },
    { day: 'Fri', fake: 48, genuine: 1200 },
    { day: 'Sat', fake: 85, genuine: 1400 },
    { day: 'Sun', fake: 72, genuine: 1350 },
  ];

  return (
    <div className="glass-card p-6 flex flex-col h-full lg:col-span-3 mt-6 hover:bg-white/[0.07] transition-all duration-300">
      <h3 className="text-lg font-bold text-white mb-6">Review Processing Trend</h3>
      <div className="w-full h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <RechartsTooltip 
               contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', backdropFilter: 'blur(10px)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
            />
            <Legend verticalAlign="top" height={40} wrapperStyle={{ color: '#cbd5e1', paddingBottom: '10px' }}/>
            <Line type="monotone" dataKey="genuine" stroke="#a855f7" strokeWidth={4} dot={{ r: 5, strokeWidth: 2, fill: '#0f172a' }} activeDot={{ r: 8, stroke: '#a855f7', fill: '#fff' }} style={{ filter: `drop-shadow(0px 4px 6px rgba(168, 85, 247, 0.4))` }} />
            <Line type="monotone" dataKey="fake" stroke="#fb7185" strokeWidth={4} dot={{ r: 5, strokeWidth: 2, fill: '#0f172a' }} activeDot={{ r: 8, stroke: '#fb7185', fill: '#fff' }} style={{ filter: `drop-shadow(0px 4px 6px rgba(251, 113, 133, 0.4))` }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
