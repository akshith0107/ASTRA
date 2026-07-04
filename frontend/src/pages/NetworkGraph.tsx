import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Network, Search, Filter, ZoomIn, ZoomOut, Maximize, 
  ShieldAlert, Activity, User, Phone, DollarSign, Globe, Award 
} from 'lucide-react';
import { fetchAPI } from '../lib/api';

export default function NetworkGraph() {
  const [data, setData] = useState<{nodes: any[], edges: any[]}>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState<number | string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<number | string | null>(null);
  
  // Interactive navigation states
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [draggedNodeId, setDraggedNodeId] = useState<number | string | null>(null);

  // Filters
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['campaign', 'report', 'phone', 'upi', 'url', 'email']);
  const [minRisk, setMinRisk] = useState<number>(0);

  // Custom node coordinates store
  const [nodePositions, setNodePositions] = useState<{ [key: string]: { x: number, y: number } }>({});
  
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch graph data
  useEffect(() => {
    async function fetchNetwork() {
      try {
        const response = await fetchAPI('/network/graph');
        setData(response);
        initializePositions(response.nodes, response.edges);
      } catch (err) {
        console.error("Failed to load network graph", err);
      } finally {
        setLoading(false);
      }
    }
    fetchNetwork();
  }, []);

  // Initialize node layout positions (concentric circles)
  const initializePositions = (nodes: any[], edges: any[]) => {
    const positions: { [key: string]: { x: number, y: number } } = {};
    const center = { x: 350, y: 300 };

    const campaigns = nodes.filter(n => n.type === 'campaign');
    const reports = nodes.filter(n => n.type === 'report');
    const entities = nodes.filter(n => n.type !== 'campaign' && n.type !== 'report');

    // Place campaigns at the center
    campaigns.forEach((n, idx) => {
      const angle = (idx / Math.max(1, campaigns.length)) * Math.PI * 2;
      const r = campaigns.length > 1 ? 50 : 0;
      positions[n.id] = {
        x: center.x + Math.cos(angle) * r,
        y: center.y + Math.sin(angle) * r
      };
    });

    // Place reports in inner circle
    reports.forEach((n, idx) => {
      const angle = (idx / Math.max(1, reports.length)) * Math.PI * 2;
      positions[n.id] = {
        x: center.x + Math.cos(angle) * 120,
        y: center.y + Math.sin(angle) * 120
      };
    });

    // Place entities in outer circle
    entities.forEach((n, idx) => {
      const angle = (idx / Math.max(1, entities.length)) * Math.PI * 2;
      positions[n.id] = {
        x: center.x + Math.cos(angle) * 220,
        y: center.y + Math.sin(angle) * 220
      };
    });

    setNodePositions(positions);
  };

  // SVG Panning handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    // If clicking a node, don't pan
    if ((e.target as SVGElement).tagName === 'circle' || (e.target as SVGElement).tagName === 'text') {
      return;
    }
    setIsPanning(true);
    setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      });
    } else if (draggedNodeId !== null) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        // Calculate raw coords in container
        const rawX = e.clientX - rect.left - pan.x;
        const rawY = e.clientY - rect.top - pan.y;
        // Transform back from zoom
        setNodePositions(prev => ({
          ...prev,
          [draggedNodeId]: {
            x: rawX / zoom,
            y: rawY / zoom
          }
        }));
      }
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setDraggedNodeId(null);
  };

  const handleNodeDragStart = (nodeId: string | number) => {
    setDraggedNodeId(nodeId);
    setSelectedNodeId(nodeId);
  };

  // Zoom handlers
  const handleZoom = (factor: number) => {
    setZoom(prev => Math.max(0.3, Math.min(3, prev * factor)));
  };

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNodeId(null);
  };

  // Node filtering
  const filteredNodes = useMemo(() => {
    return data.nodes.filter(n => {
      const typeMatch = selectedTypes.includes(n.type);
      const riskMatch = n.risk_score >= minRisk;
      const searchMatch = searchQuery
        ? n.value.toLowerCase().includes(searchQuery.toLowerCase()) || String(n.id).includes(searchQuery)
        : true;
      return typeMatch && riskMatch && searchMatch;
    });
  }, [data.nodes, selectedTypes, minRisk, searchQuery]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  const filteredEdges = useMemo(() => {
    return data.edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));
  }, [data.edges, filteredNodeIds]);

  // Neighbor nodes helper for highlighters
  const connectedNodes = useMemo(() => {
    const activeId = hoveredNodeId || selectedNodeId;
    if (!activeId) return null;
    const connected = new Set<string | number>();
    connected.add(activeId);
    data.edges.forEach(e => {
      if (e.source === activeId) connected.add(e.target);
      if (e.target === activeId) connected.add(e.source);
    });
    return connected;
  }, [data.edges, selectedNodeId, hoveredNodeId]);

  // Node stats summary calculation (Analytics)
  const stats = useMemo(() => {
    if (data.nodes.length === 0) return { highestDegreeNode: 'N/A', largestCampaignSize: 0, avgRisk: 0 };
    
    // Degrees computation
    const degrees: { [key: string]: number } = {};
    data.edges.forEach(e => {
      degrees[e.source] = (degrees[e.source] || 0) + 1;
      degrees[e.target] = (degrees[e.target] || 0) + 1;
    });

    let maxDeg = 0;
    let maxNodeVal = 'N/A';
    data.nodes.forEach(n => {
      const deg = degrees[n.id] || 0;
      if (deg > maxDeg) {
        maxDeg = deg;
        maxNodeVal = `${n.value} (${n.type.toUpperCase()})`;
      }
    });

    // Largest campaign size estimation
    const campaignCounts: { [key: string]: number } = {};
    data.edges.forEach(e => {
      const srcNode = data.nodes.find(n => n.id === e.source);
      const tgtNode = data.nodes.find(n => n.id === e.target);
      if (srcNode?.type === 'campaign') {
        campaignCounts[srcNode.value] = (campaignCounts[srcNode.value] || 0) + 1;
      }
      if (tgtNode?.type === 'campaign') {
        campaignCounts[tgtNode.value] = (campaignCounts[tgtNode.value] || 0) + 1;
      }
    });
    const campaignSizes = Object.values(campaignCounts);
    const largestCampaignSize = campaignSizes.length > 0 ? Math.max(...campaignSizes) : 0;

    const avgRisk = data.nodes.reduce((acc, n) => acc + n.risk_score, 0) / data.nodes.length;

    return {
      highestDegreeNode: maxNodeVal,
      largestCampaignSize,
      avgRisk: avgRisk.toFixed(0)
    };
  }, [data.nodes, data.edges]);

  const selectedNodeDetails = useMemo(() => {
    if (!selectedNodeId) return null;
    const node = data.nodes.find(n => n.id === selectedNodeId);
    if (!node) return null;
    const conns = data.edges.filter(e => e.source === selectedNodeId || e.target === selectedNodeId).length;
    return { ...node, connections: conns };
  }, [selectedNodeId, data.nodes, data.edges]);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'campaign': return <Award className="w-4 h-4 text-error" />;
      case 'report': return <ShieldAlert className="w-4 h-4 text-warning" />;
      case 'phone': return <Phone className="w-4 h-4 text-blue-400" />;
      case 'upi': return <DollarSign className="w-4 h-4 text-green-400" />;
      case 'url': return <Globe className="w-4 h-4 text-indigo-400" />;
      default: return <User className="w-4 h-4 text-silver-gray" />;
    }
  };

  const toggleTypeFilter = (type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col gap-6">
      {/* Top Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Network Intelligence</h1>
          <p className="text-secondary font-mono text-sm">CORRELATION ENGINE • THREAT ACTOR CONNECTIONS</p>
        </div>
        
        {/* Search and Quick controls */}
        <div className="flex flex-wrap gap-3 w-full md:w-auto">
          <div className="glass-card flex items-center px-4 py-2 border-white/10 flex-1 md:flex-none">
            <Search className="w-4 h-4 text-secondary mr-2" />
            <input 
              type="text" 
              placeholder="Search ID, Phone, UPI..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none text-white text-sm focus:outline-none w-full md:w-48 placeholder-secondary"
            />
          </div>
          
          <div className="flex gap-2">
            <button onClick={() => handleZoom(1.2)} className="glass-card p-2 hover:bg-white/5 text-white" title="Zoom In"><ZoomIn className="w-4 h-4" /></button>
            <button onClick={() => handleZoom(0.8)} className="glass-card p-2 hover:bg-white/5 text-white" title="Zoom Out"><ZoomOut className="w-4 h-4" /></button>
            <button onClick={handleReset} className="glass-card p-2 hover:bg-white/5 text-white" title="Fit Screen"><Maximize className="w-4 h-4" /></button>
          </div>
        </div>
      </header>

      {/* Main Sandbox Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-gutter overflow-hidden min-h-0">
        
        {/* Left Filter/Settings panel */}
        <div className="lg:col-span-3 flex flex-col gap-gutter overflow-y-auto">
          {/* Filters card */}
          <div className="glass-panel p-5 flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-white/10 pb-3">
              <Filter className="w-4 h-4 text-silver-gray" />
              <span className="font-mono text-xs text-white uppercase tracking-wider">GRAPH FILTERS</span>
            </div>
            
            {/* Entity Types */}
            <div>
              <span className="text-[10px] text-secondary font-mono uppercase tracking-widest block mb-2">Display Nodes</span>
              <div className="space-y-2">
                {['campaign', 'report', 'phone', 'upi', 'url', 'email'].map(type => (
                  <label key={type} className="flex items-center gap-3 text-xs text-secondary cursor-pointer hover:text-white transition-colors">
                    <input 
                      type="checkbox" 
                      checked={selectedTypes.includes(type)}
                      onChange={() => toggleTypeFilter(type)}
                      className="rounded bg-charcoal border-white/20 accent-white w-3.5 h-3.5"
                    />
                    <span className="capitalize">{type === 'upi' ? 'UPI ID' : type === 'url' ? 'URL address' : type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Risk threshold slider */}
            <div className="pt-2 border-t border-white/5">
              <label className="text-[10px] text-secondary font-mono uppercase tracking-widest flex justify-between mb-2">
                <span>Minimum Risk level</span>
                <span className="text-white">{minRisk}%</span>
              </label>
              <input 
                type="range" max="100" min="0" step="5"
                value={minRisk}
                onChange={(e) => setMinRisk(Number(e.target.value))}
                className="w-full h-1 bg-white/10 rounded cursor-pointer accent-white"
              />
            </div>
          </div>

          {/* Graph Analytics card */}
          <div className="glass-panel p-5 flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-border-subtle pb-3">
              <Activity className="w-4 h-4 text-silver-gray" />
              <span className="font-mono text-xs text-white uppercase tracking-wider">GRAPH ANALYTICS</span>
            </div>
            
            <div className="space-y-4 font-mono text-[10px] text-secondary">
              <div>
                <span className="opacity-70 uppercase block mb-1">Most Connected Hub:</span>
                <span className="text-white text-xs font-semibold block truncate" title={stats.highestDegreeNode}>
                  {stats.highestDegreeNode}
                </span>
              </div>
              
              <div>
                <span className="opacity-70 uppercase block mb-1">Largest Campaign Size:</span>
                <span className="text-white text-xs font-semibold block">
                  {stats.largestCampaignSize} linked entities
                </span>
              </div>

              <div>
                <span className="opacity-70 uppercase block mb-1">Average Risk Quotient:</span>
                <span className="text-white text-xs font-semibold block">
                  {stats.avgRisk}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Center SVG canvas container */}
        <div 
          ref={containerRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="lg:col-span-6 glass-panel relative overflow-hidden flex items-center justify-center cursor-grab active:cursor-grabbing min-h-[400px] lg:min-h-0"
        >
          {/* Grid bg */}
          <div className="absolute inset-0 pointer-events-none" style={{ 
            backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px)',
            backgroundSize: '40px 40px'
          }}></div>

          {loading ? (
            <div className="relative z-10 text-secondary font-mono text-xs animate-pulse uppercase tracking-widest">
              INITIALIZING NETWORK CORRELATION ENGINE...
            </div>
          ) : filteredNodes.length === 0 ? (
            <div className="relative z-10 text-secondary font-mono text-xs uppercase tracking-widest">
              No matching intelligence nodes found.
            </div>
          ) : (
            <svg 
              className="absolute inset-0 w-full h-full"
              style={{ pointerEvents: 'auto' }}
            >
              {/* Transform Group (Zoom & Pan) */}
              <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                
                {/* Edges layer */}
                {filteredEdges.map(edge => {
                  const sPos = nodePositions[edge.source];
                  const tPos = nodePositions[edge.target];
                  if (!sPos || !tPos) return null;
                  
                  const isHighlighted = connectedNodes
                    ? connectedNodes.has(edge.source) && connectedNodes.has(edge.target)
                    : true;
                    
                  return (
                    <line 
                      key={edge.id}
                      x1={sPos.x}
                      y1={sPos.y}
                      x2={tPos.x}
                      y2={tPos.y}
                      stroke={edge.type === 'used_in' ? 'rgba(255, 99, 71, 0.6)' : 'rgba(255, 255, 255, 0.15)'}
                      strokeWidth={isHighlighted ? 2.5 : 0.8}
                      strokeOpacity={isHighlighted ? 0.9 : 0.25}
                      strokeDasharray={edge.type === 'used_in' ? '4 4' : 'none'}
                    />
                  );
                })}

                {/* Nodes layer */}
                {filteredNodes.map(node => {
                  const pos = nodePositions[node.id];
                  if (!pos) return null;

                  const isSelected = selectedNodeId === node.id;
                  const isHighlighted = connectedNodes ? connectedNodes.has(node.id) : true;
                  
                  // Color codes
                  let nodeColor = 'rgb(180,180,180)';
                  if (node.type === 'campaign') nodeColor = 'rgb(239, 68, 68)';
                  else if (node.type === 'report') nodeColor = 'rgb(245, 158, 11)';
                  else if (node.type === 'phone') nodeColor = 'rgb(96, 165, 250)';
                  else if (node.type === 'upi') nodeColor = 'rgb(52, 211, 153)';
                  else if (node.type === 'url') nodeColor = 'rgb(129, 140, 248)';

                  return (
                    <g 
                      key={node.id}
                      transform={`translate(${pos.x}, ${pos.y})`}
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        handleNodeDragStart(node.id);
                      }}
                      onMouseEnter={() => setHoveredNodeId(node.id)}
                      onMouseLeave={() => setHoveredNodeId(null)}
                      className="cursor-pointer"
                    >
                      {/* Pulse shadow for campaigns */}
                      {node.type === 'campaign' && (
                        <circle 
                          r={20} 
                          fill="rgba(239, 68, 68, 0.1)" 
                          className="animate-ping"
                        />
                      )}
                      
                      {/* Base Circle */}
                      <circle 
                        r={node.type === 'campaign' ? 16 : node.type === 'report' ? 13 : 9}
                        fill={nodeColor}
                        fillOpacity={isHighlighted ? 1 : 0.25}
                        stroke="#000"
                        strokeWidth={isSelected ? 3 : 1.5}
                        className="transition-all duration-200"
                      />

                      {/* Display name label */}
                      <text
                        y={node.type === 'campaign' ? 26 : 20}
                        textAnchor="middle"
                        fill={isHighlighted ? '#fff' : 'rgba(255,255,255,0.2)'}
                        fontSize={node.type === 'campaign' ? 9 : 8}
                        fontFamily="monospace"
                        className="pointer-events-none select-none font-bold"
                      >
                        {node.value.length > 15 ? `${node.value.slice(0, 12)}...` : node.value}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>
          )}
        </div>

        {/* Right Info sidebar Panel */}
        <div className="lg:col-span-3 flex flex-col gap-gutter overflow-y-auto">
          <div className="glass-panel p-5 flex flex-col h-full">
            <div className="flex items-center gap-2 border-b border-white/10 pb-3 mb-4">
              <Network className="w-4 h-4 text-silver-gray" />
              <span className="font-mono text-xs text-white uppercase tracking-wider">NODE DETAILS</span>
            </div>

            {selectedNodeDetails ? (
              <div className="flex-1 flex flex-col justify-between">
                <div className="space-y-4">
                  {/* Entity Profile info */}
                  <div className="flex items-center gap-3 bg-white/5 p-3 rounded-xl border border-white/10">
                    <div className="p-2 bg-white/10 rounded-lg">
                      {getNodeIcon(selectedNodeDetails.type)}
                    </div>
                    <div className="min-w-0">
                      <p className="text-[10px] text-secondary font-mono uppercase tracking-widest">{selectedNodeDetails.type}</p>
                      <p className="text-white text-xs font-bold truncate" title={selectedNodeDetails.value}>
                        {selectedNodeDetails.value}
                      </p>
                    </div>
                  </div>

                  <div className="space-y-2.5 font-mono text-[10px] text-secondary">
                    <div className="flex justify-between border-b border-white/5 pb-1.5">
                      <span>Database ID:</span>
                      <span className="text-white">NODE-{selectedNodeDetails.id}</span>
                    </div>
                    
                    <div className="flex justify-between border-b border-white/5 pb-1.5">
                      <span>Connections:</span>
                      <span className="text-white">{selectedNodeDetails.connections} Linked links</span>
                    </div>

                    <div className="flex justify-between border-b border-white/5 pb-1.5">
                      <span>Risk score:</span>
                      <span className={`font-bold ${selectedNodeDetails.risk_score > 70 ? 'text-error' : 'text-primary'}`}>
                        {selectedNodeDetails.risk_score.toFixed(0)}%
                      </span>
                    </div>

                    {selectedNodeDetails.first_seen && (
                      <div className="flex flex-col gap-0.5 border-b border-white/5 pb-1.5">
                        <span>First Detected:</span>
                        <span className="text-white text-[9px] mt-0.5">{selectedNodeDetails.first_seen}</span>
                      </div>
                    )}

                    {selectedNodeDetails.last_seen && (
                      <div className="flex flex-col gap-0.5 pb-1">
                        <span>Last Active Check:</span>
                        <span className="text-white text-[9px] mt-0.5">{selectedNodeDetails.last_seen}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-white/5 mt-6 space-y-2">
                  <span className="text-[9px] text-secondary font-mono uppercase block text-center">
                    Drag nodes to adjust layout manually.
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center text-secondary font-mono text-[10px] py-16">
                <Maximize className="w-5 h-5 text-white/10 mb-2" />
                <span>SELECT AN INTELLIGENCE NODE TO VIEW LINK DETAILS</span>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
