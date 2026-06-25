import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, AlertCircle, ShieldAlert, Activity } from 'lucide-react';
import { WS_URL } from '../lib/api';

export default function LiveMonitor() {
  const [isRecording, setIsRecording] = useState(false);
  const [riskScore, setRiskScore] = useState(0);
  const [scamType, setScamType] = useState('Listening...');
  const [indicators, setIndicators] = useState<any[]>([]);
  const [transcripts, setTranscripts] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const simulatorRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  const startRecording = () => {
    setIsRecording(true);
    setTranscripts([{ role: 'SYSTEM', text: "WebSocket stream connected. Simulating audio chunk ingestion...", risk: 0, time: new Date().toLocaleTimeString('en-US', { hour12: false }) }]);
    
    const token = localStorage.getItem('token');
    const wsUrlWithToken = token ? `${WS_URL}?token=${token}` : WS_URL;
    wsRef.current = new WebSocket(wsUrlWithToken);
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        setTranscripts(prev => [...prev, { 
          role: 'CALLER', 
          text: data.transcript, 
          risk: data.risk_score / 100, // Normalized to 0-1
          time: new Date().toLocaleTimeString('en-US', { hour12: false })
        }]);
        
        setRiskScore(data.risk_score / 100);
        setScamType(data.scam_type);
        setIndicators(data.indicators);
        
      } catch (err) {
        console.error("WS parse error", err);
      }
    };

    // Simulate sending audio chunks to the backend
    // Since we don't have a real microphone AudioWorklet setup for MVP,
    // we send dummy bytes that the backend will process (and since it's dummy, whisper might return silence, 
    // so we'll just show the connection is active)
    let count = 0;
    simulatorRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        // We're just sending a dummy byte array to keep the connection alive
        // The real implementation would be capturing PCM from navigator.mediaDevices.getUserMedia
        const dummyAudioChunk = new Uint8Array(1024);
        wsRef.current.send(dummyAudioChunk);
        
        // For visual demonstration, if backend returns nothing on dummy chunks, 
        // we'll inject mock responses periodically to show the UI
        if (count === 1) {
          wsRef.current.dispatchEvent(new MessageEvent('message', {
            data: JSON.stringify({
              transcript: "I am calling from State Bank of India security division.",
              risk_score: 25,
              scam_type: "Suspicious Inquiry",
              indicators: [{ type: "Authority Impersonation" }]
            })
          }));
        } else if (count === 3) {
          wsRef.current.dispatchEvent(new MessageEvent('message', {
            data: JSON.stringify({
              transcript: "We have detected an unauthorized transaction of Rs 49,999 from your account. Please share the OTP sent to your number immediately.",
              risk_score: 98,
              scam_type: "Bank Impersonation / OTP Fraud",
              indicators: [{ type: "Authority Impersonation" }, { type: "OTP Request" }, { type: "Urgency/Threat" }]
            })
          }));
        }
        count++;
      }
    }, 3000);
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (simulatorRef.current) {
      clearInterval(simulatorRef.current);
    }
  };

  const toggleRecording = () => {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex gap-6">
      {/* Main Analysis Area */}
      <div className="flex-1 flex flex-col gap-6">
        <header className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Live Analysis</h1>
            <p className="text-secondary font-mono text-sm">AUDIO STREAM: {isRecording ? <span className="text-primary animate-pulse">ACTIVE</span> : 'INACTIVE'}</p>
          </div>
          <button 
            onClick={toggleRecording}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold tracking-wide transition-all ${
              isRecording 
                ? 'bg-white text-black hover:bg-white/90 shadow-[0_0_20px_rgba(255,255,255,0.3)]' 
                : 'bg-charcoal border border-white/20 text-white hover:bg-white/5'
            }`}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            {isRecording ? 'STOP CAPTURE' : 'START MIC CAPTURE'}
          </button>
        </header>

        {/* Live Transcript Panel */}
        <div className="glass-panel flex-1 p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-4">
            <Activity className="w-5 h-5 text-white" />
            <h2 className="font-mono font-bold tracking-widest text-sm text-white">REAL-TIME TRANSCRIPT</h2>
          </div>

          <div className="flex-1 overflow-y-auto space-y-6 pr-4">
            {transcripts.map((msg, idx) => (
              <div key={idx} className={`flex flex-col ${msg.role === 'SYSTEM' ? 'items-center' : 'items-start'}`}>
                {msg.role !== 'SYSTEM' && (
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-[10px] text-secondary">{msg.time}</span>
                    <span className={`font-mono text-[10px] px-1.5 py-0.5 rounded border border-error/30 text-error`}>
                      {msg.role}
                    </span>
                  </div>
                )}
                <div className={`p-4 max-w-[80%] rounded-2xl ${
                  msg.role === 'SYSTEM' 
                    ? 'bg-transparent border border-white/5 rounded-sm text-secondary text-xs font-mono' 
                    : `bg-[#111111] border ${msg.risk > 0.7 ? 'border-error/50 shadow-[0_0_15px_rgba(255,180,171,0.1)]' : 'border-white/10'} rounded-tl-sm text-white`
                }`}>
                  <p className="leading-relaxed">{msg.text}</p>
                </div>
                {msg.role === 'CALLER' && (
                  <div className="mt-2 flex items-center gap-2">
                    <div className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface border border-white/10 text-secondary">
                      RISK SCORE: {(msg.risk * 100).toFixed(0)}%
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Side Panel: Risk Meter & Indicators */}
      <div className="w-80 flex flex-col gap-6">
        <div className={`glass-panel p-6 flex flex-col items-center justify-center transition-all duration-500 ${
          riskScore > 0.85 ? 'border-error/50 shadow-[0_0_30px_rgba(255,180,171,0.15)] bg-error/5' : ''
        }`}>
          <h3 className="font-mono text-sm tracking-widest text-secondary mb-8">THREAT LEVEL</h3>
          
          <div className="relative w-48 h-48 flex items-center justify-center">
            {/* Background Circle */}
            <svg className="absolute inset-0 w-full h-full transform -rotate-90">
              <circle cx="96" cy="96" r="88" stroke="rgba(255,255,255,0.05)" strokeWidth="12" fill="none" />
              {/* Progress Circle */}
              <circle 
                cx="96" cy="96" r="88" 
                stroke={riskScore > 0.85 ? '#ffb4ab' : '#ffffff'} 
                strokeWidth="12" fill="none" 
                strokeDasharray="552.9" 
                strokeDashoffset={552.9 - (552.9 * riskScore)} 
                strokeLinecap="round"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="text-center z-10">
              <div className={`text-5xl font-bold font-mono tracking-tighter ${riskScore > 0.85 ? 'text-error' : 'text-white'}`}>
                {(riskScore * 100).toFixed(0)}<span className="text-2xl">%</span>
              </div>
              <div className="text-xs text-secondary mt-1 font-mono">RISK</div>
            </div>
          </div>

          <div className="mt-8 w-full text-center">
            <p className="text-sm font-medium text-white mb-2">{scamType}</p>
            {riskScore > 0.85 && (
              <div className="bg-error/10 border border-error/50 text-error p-3 rounded-xl flex items-start gap-3 animate-pulse mt-4 text-left">
                <ShieldAlert className="w-5 h-5 flex-shrink-0" />
                <div className="text-sm font-medium">
                  CRITICAL: Likely Bank Impersonation / OTP Fraud detected. Terminate call.
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="glass-panel p-6 flex-1">
          <h3 className="font-mono text-sm tracking-widest text-secondary mb-4 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" /> SCAM INDICATORS
          </h3>
          
          <div className="space-y-3">
            {indicators.length === 0 && <p className="text-xs text-secondary font-mono">No active indicators.</p>}
            {indicators.map((ind, i) => (
              <div key={i} className="flex items-center justify-between p-3 glass-card border border-error/30 bg-error/5">
                <span className="text-sm text-white font-medium">
                  {ind.type}
                </span>
                <div className="w-2 h-2 rounded-full bg-error shadow-[0_0_8px_#ffb4ab]"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
