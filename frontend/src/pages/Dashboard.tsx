import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, TrendingUp, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { fetchAPI } from '../lib/api';

const chartData = [
  { name: 'Mon', scams: 40, intercepted: 24 },
  { name: 'Tue', scams: 30, intercepted: 13 },
  { name: 'Wed', scams: 20, intercepted: 98 },
  { name: 'Thu', scams: 27, intercepted: 39 },
  { name: 'Fri', scams: 18, intercepted: 48 },
  { name: 'Sat', scams: 23, intercepted: 38 },
  { name: 'Sun', scams: 34, intercepted: 43 },
];

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [statsRes, reportsRes] = await Promise.all([
          fetchAPI('/dashboard/stats'),
          fetchAPI('/dashboard/reports?limit=5')
        ]);
        setStats(statsRes);
        setReports(reportsRes);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Threat Intelligence</h1>
          <p className="text-secondary font-mono text-sm">SYSTEM STATUS: <span className="text-primary">NOMINAL</span> • LAST UPDATE: JUST NOW</p>
        </div>
        <div className="glass-card px-4 py-2 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-white animate-pulse"></div>
          <span className="font-mono text-sm">LIVE API CONNECTED</span>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-white/10 p-3 rounded-xl">
              <Shield className="w-6 h-6 text-white" />
            </div>
          </div>
          <h3 className="text-secondary text-sm font-medium mb-1">Total Reports</h3>
          <p className="text-3xl font-bold text-white font-mono">{loading ? '-' : stats?.total_reports}</p>
        </div>
        <div className="glass-panel p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-white/10 p-3 rounded-xl border border-error/30">
              <AlertTriangle className="w-6 h-6 text-error" />
            </div>
          </div>
          <h3 className="text-secondary text-sm font-medium mb-1">Critical Alerts</h3>
          <p className="text-3xl font-bold text-white font-mono">{loading ? '-' : stats?.critical_alerts}</p>
        </div>
        <div className="glass-panel p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-white/10 p-3 rounded-xl">
              <Users className="w-6 h-6 text-white" />
            </div>
          </div>
          <h3 className="text-secondary text-sm font-medium mb-1">Active Campaigns</h3>
          <p className="text-3xl font-bold text-white font-mono">{loading ? '-' : stats?.active_campaigns}</p>
        </div>
        <div className="glass-panel p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-white/10 p-3 rounded-xl">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
          </div>
          <h3 className="text-secondary text-sm font-medium mb-1">Detection Rate</h3>
          <p className="text-3xl font-bold text-white font-mono">{loading ? '-' : stats?.detection_rate}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Chart */}
        <div className="glass-panel p-6 lg:col-span-2">
          <h2 className="text-lg font-bold text-white mb-6">Threat Volume Trends</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorScams" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ffffff" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ffffff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="#B8B8B8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#B8B8B8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111111', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="scams" stroke="#ffffff" fillOpacity={1} fill="url(#colorScams)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Scams Feed */}
        <div className="glass-panel p-6 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold text-white">Recent Intercepts</h2>
            <button className="text-xs text-secondary hover:text-white transition-colors">VIEW ALL</button>
          </div>
          
          <div className="space-y-4 flex-1 overflow-y-auto pr-2">
            {reports.map((scam, i) => (
              <div key={i} className="glass-card p-4 hover:bg-white/5 transition-colors cursor-pointer group">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-mono text-xs text-secondary group-hover:text-white transition-colors">RPT-{scam.id}</span>
                  <span className="text-xs text-secondary">{new Date(scam.created_at).toLocaleTimeString()}</span>
                </div>
                <h3 className="font-medium text-white mb-2">{scam.scam_type}</h3>
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-surface rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${scam.risk_score > 80 ? 'bg-error' : 'bg-white'}`} 
                        style={{ width: `${scam.risk_score}%` }}
                      ></div>
                    </div>
                    <span className="font-mono text-xs font-bold">{scam.risk_score.toFixed(0)}% RISK</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-1 rounded border ${scam.risk_level === 'CRITICAL' ? 'border-error/50 text-error bg-error/10' : 'border-white/20 text-white bg-white/10'}`}>
                    {scam.risk_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
