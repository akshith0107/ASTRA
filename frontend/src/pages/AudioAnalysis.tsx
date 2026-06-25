import React, { useState } from 'react';
import { UploadCloud, FileAudio, Play, Pause, Activity, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { fetchAPI } from '../lib/api';

export default function AudioAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const analyzeAudio = async () => {
    if (!file) return;
    setIsAnalyzing(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetchAPI('/analyze/audio', {
        method: 'POST',
        body: formData
      });
      setResults(response);
    } catch (err: any) {
      setError(err.message || "Audio analysis failed.");
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Audio Analysis</h1>
        <p className="text-secondary font-mono text-sm">BATCH PROCESSING MODULE • UPLOAD RECORDINGS FOR ANALYSIS</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="glass-panel p-6 flex flex-col justify-center min-h-[400px]">
          {!file ? (
            <div 
              className="border-2 border-dashed border-white/20 rounded-2xl p-12 flex flex-col items-center justify-center text-center hover:border-white/40 hover:bg-white/5 transition-all cursor-pointer h-full"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              <div className="bg-white/10 p-4 rounded-full mb-4">
                <UploadCloud className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">Upload Audio Recording</h3>
              <p className="text-sm text-secondary mb-6 max-w-sm">
                Drag and drop your MP3, WAV, or AAC file here, or click to browse files.
              </p>
              <button 
                className="bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-white/90 transition-colors"
                onClick={() => document.getElementById('audio-upload')?.click()}
              >
                Select File
              </button>
              <input 
                id="audio-upload" 
                type="file" 
                accept="audio/*" 
                className="hidden" 
                onChange={(e) => e.target.files && setFile(e.target.files[0])} 
              />
            </div>
          ) : (
            <div className="flex flex-col h-full">
              <div className="glass-card p-6 flex items-center gap-4 mb-8 border border-primary/30 bg-primary/5">
                <div className="bg-primary/20 p-3 rounded-lg">
                  <FileAudio className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">{file.name}</h3>
                  <p className="text-xs text-secondary font-mono">{(file.size / 1024 / 1024).toFixed(2)} MB • Audio File</p>
                </div>
                <button 
                  onClick={() => { setFile(null); setResults(null); }}
                  className="text-xs text-secondary hover:text-white"
                >
                  REMOVE
                </button>
              </div>

              {error && <p className="mb-4 text-center text-error text-sm">{error}</p>}

              <div className="flex-1 flex flex-col items-center justify-center">
                {isAnalyzing ? (
                  <div className="flex flex-col items-center">
                    <Activity className="w-12 h-12 text-primary animate-pulse mb-4" />
                    <h3 className="text-white font-medium mb-2">Analyzing Recording...</h3>
                    <p className="text-sm text-secondary font-mono text-center max-w-xs">
                      Running Whisper transcription and multi-stage BERT threat evaluation.
                    </p>
                  </div>
                ) : !results ? (
                  <button 
                    onClick={analyzeAudio}
                    className="bg-white text-black px-8 py-3 rounded-xl font-bold tracking-wide hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all"
                  >
                    START ANALYSIS
                  </button>
                ) : (
                  <div className="flex flex-col items-center text-center">
                    <div className="bg-white/10 p-4 rounded-full mb-4 border border-white/20">
                      <CheckCircle2 className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-white font-medium mb-1">Analysis Complete</h3>
                    <p className="text-sm text-secondary">Results are displayed in the intelligence panel.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className={`glass-panel p-6 flex flex-col transition-all duration-500 overflow-y-auto max-h-[600px] ${results && results.risk_score > 80 ? 'border-error/50 shadow-[0_0_30px_rgba(255,180,171,0.1)]' : ''}`}>
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-4">
            <ShieldAlert className="w-5 h-5 text-white" />
            <h2 className="font-mono font-bold tracking-widest text-sm text-white">INTELLIGENCE REPORT</h2>
          </div>

          {!results && !isAnalyzing && (
            <div className="flex-1 flex items-center justify-center text-secondary font-mono text-sm text-center">
              WAITING FOR AUDIO INPUT...
            </div>
          )}

          {isAnalyzing && (
            <div className="flex-1 flex flex-col gap-4">
              <div className="h-4 bg-white/5 rounded w-3/4 animate-pulse"></div>
              <div className="h-4 bg-white/5 rounded w-full animate-pulse"></div>
              <div className="h-4 bg-white/5 rounded w-5/6 animate-pulse"></div>
              <div className="mt-8 h-32 bg-white/5 rounded-xl animate-pulse"></div>
            </div>
          )}

          {results && (
            <div className="flex-1 flex flex-col gap-6 animate-in fade-in duration-500">
              <div className="flex gap-4">
                <div className="flex-1 glass-card p-4">
                  <p className="text-xs text-secondary font-mono mb-1">DETECTED THREAT</p>
                  <p className="text-white font-medium">{results.scam_type}</p>
                </div>
                <div className={`glass-card p-4 w-32 flex flex-col items-center justify-center border ${results.risk_score > 80 ? 'border-error/50 bg-error/10 text-error' : 'border-white/20 text-white'}`}>
                  <p className="text-xs font-mono mb-1 opacity-70">RISK SCORE</p>
                  <p className="text-2xl font-bold font-mono">{(results.risk_score).toFixed(0)}%</p>
                </div>
              </div>

              {results.similar_scams && results.similar_scams.length > 0 && (
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <h3 className="text-xs font-mono text-primary mb-2">RAG KNOWLEDGE BASE MATCHES</h3>
                  {results.similar_scams.map((s: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-sm">
                      <span className="text-white">{s.campaign_name}</span>
                      <span className="text-secondary font-mono">{(s.similarity_score * 100).toFixed(1)}% Match</span>
                    </div>
                  ))}
                </div>
              )}

              <div>
                <h3 className="text-sm font-medium text-white mb-3">Transcription</h3>
                <div className="bg-[#111111] p-4 rounded-xl border border-white/10 text-secondary leading-relaxed text-sm">
                  {results.transcript || "No transcript returned."}
                </div>
              </div>

              {results.indicators && results.indicators.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-white mb-3">Key Threat Indicators</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.indicators.map((ind: any, i: number) => (
                      <span key={i} className="px-3 py-1 bg-surface border border-white/10 rounded-md text-xs font-mono text-white" title={ind.description}>
                        {ind.type}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
