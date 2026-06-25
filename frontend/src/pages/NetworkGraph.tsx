import React, { useState, useEffect } from 'react';
import { Network, Search, Filter } from 'lucide-react';
import { fetchAPI } from '../lib/api';

export default function NetworkGraph() {
  const [data, setData] = useState<{nodes: any[], edges: any[]}>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchNetwork() {
      try {
        const response = await fetchAPI('/network/graph');
        setData(response);
      } catch (err) {
        console.error("Failed to load network graph", err);
      } finally {
        setLoading(false);
      }
    }
    fetchNetwork();
  }, []);

  // For MVP, we map specific logical nodes from the backend to our hardcoded visual coordinates
  const mainCampaign = data.nodes.find(n => n.type === 'campaign') || { id: 'N/A', value: 'Unknown Campaign', risk_score: 100 };
  const upiNode = data.nodes.find(n => n.type === 'upi') || { value: 'N/A' };
  const phoneNode = data.nodes.find(n => n.type === 'phone') || { value: 'N/A' };
  const urlNode = data.nodes.find(n => n.type === 'url') || { value: 'N/A' };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col gap-6">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Network Intelligence</h1>
          <p className="text-secondary font-mono text-sm">CORRELATION ENGINE • THREAT ACTOR MAPPING</p>
        </div>
        <div className="flex gap-4">
          <div className="glass-card flex items-center px-4 py-2 border-white/10">
            <Search className="w-4 h-4 text-secondary mr-2" />
            <input 
              type="text" 
              placeholder="Search ID, Phone, UPI..." 
              className="bg-transparent border-none text-white text-sm focus:outline-none w-48 placeholder-secondary"
            />
          </div>
          <button className="glass-card px-4 py-2 flex items-center gap-2 hover:bg-white/5 transition-colors">
            <Filter className="w-4 h-4 text-secondary" />
            <span className="text-sm font-medium text-white">Filter</span>
          </button>
        </div>
      </header>

      <div className="flex-1 glass-panel relative overflow-hidden flex items-center justify-center">
        {/* Decorative Grid Background */}
        <div className="absolute inset-0" style={{ 
          backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)',
          backgroundSize: '40px 40px'
        }}></div>

        {loading ? (
          <div className="relative z-10 text-secondary font-mono text-sm animate-pulse">
            INITIALIZING GRAPH ENGINE...
          </div>
        ) : (
          <div className="relative w-full h-full">
            {/* Central Node */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10">
              <div className="w-20 h-20 rounded-full bg-error/10 border-2 border-error flex items-center justify-center shadow-[0_0_30px_rgba(255,180,171,0.2)] animate-pulse">
                <Network className="w-8 h-8 text-error" />
              </div>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 text-center w-48">
                <p className="text-white font-medium text-sm">{mainCampaign.value}</p>
                <p className="text-error font-mono text-[10px]">CRITICAL THREAT</p>
              </div>
            </div>

            {/* Connected Nodes */}
            {/* Node 1 */}
            <div className="absolute top-[20%] left-[30%]">
              <div className="w-12 h-12 rounded-full bg-surface border border-white/20 flex items-center justify-center">
                <span className="text-white font-mono text-xs">UPI</span>
              </div>
              <p className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 text-secondary text-xs w-max">{upiNode.value}</p>
            </div>
            <svg className="absolute top-0 left-0 w-full h-full pointer-events-none">
              <line x1="50%" y1="50%" x2="30%" y2="20%" stroke="rgba(255,255,255,0.1)" strokeWidth="2" strokeDasharray="4 4" />
            </svg>

            {/* Node 2 */}
            <div className="absolute top-[70%] left-[20%]">
              <div className="w-10 h-10 rounded-full bg-surface border border-white/20 flex items-center justify-center">
                <span className="text-white font-mono text-[10px]">PHN</span>
              </div>
              <p className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 text-secondary text-xs w-max">{phoneNode.value}</p>
            </div>
            <svg className="absolute top-0 left-0 w-full h-full pointer-events-none">
              <line x1="50%" y1="50%" x2="20%" y2="70%" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
            </svg>

            {/* Node 3 */}
            <div className="absolute top-[30%] right-[25%]">
              <div className="w-14 h-14 rounded-full bg-surface border border-white/20 flex items-center justify-center">
                <span className="text-white font-mono text-xs">URL</span>
              </div>
              <p className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 text-secondary text-xs w-max">{urlNode.value}</p>
            </div>
            <svg className="absolute top-0 left-0 w-full h-full pointer-events-none">
              <line x1="50%" y1="50%" x2="75%" y2="30%" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
            </svg>
          </div>
        )}

        {/* Floating Info Panel */}
        <div className="absolute bottom-6 right-6 w-80 glass-card p-4 bg-[#111111]/90">
          <h3 className="font-mono text-sm tracking-widest text-white mb-4">NODE DETAILS</h3>
          <div className="space-y-3">
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-xs text-secondary font-mono">ID</span>
              <span className="text-xs text-white font-mono">CMP-{mainCampaign.id}</span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-xs text-secondary font-mono">TYPE</span>
              <span className="text-xs text-white">Organized Syndicate</span>
            </div>
            <div className="flex justify-between border-b border-white/10 pb-2">
              <span className="text-xs text-secondary font-mono">EDGES</span>
              <span className="text-xs text-white font-mono">{data.edges.length} Correlated Links</span>
            </div>
            <div className="flex justify-between">
              <span className="text-xs text-secondary font-mono">STATUS</span>
              <span className="text-xs text-error font-mono">ACTIVE MONITORING</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
