import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, FileAudio, Play, Pause, Activity, ShieldAlert, 
  CheckCircle2, Copy, Download, FileText, ExternalLink, HelpCircle 
} from 'lucide-react';
import { fetchAPI } from '../lib/api';

export default function AudioAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysisStage, setAnalysisStage] = useState('');
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);

  // Status timeline stages during ML evaluation
  const stages = [
    { label: "Initializing Neural core components", pct: 15 },
    { label: "Executing Whisper Audio Transcription", pct: 40 },
    { label: "Running MiniLM Scam-Type Classification", pct: 65 },
    { label: "Evaluating Risk via BiLSTM Estimator", pct: 80 },
    { label: "Querying RAG Threat Campaign Knowledgebase", pct: 90 },
    { label: "Compiling Threat Indicators & Report", pct: 100 }
  ];

  useEffect(() => {
    let timer: any;
    if (isAnalyzing) {
      setProgress(0);
      let currentStageIndex = 0;
      setAnalysisStage(stages[0].label);

      timer = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(timer);
            return 100;
          }
          const next = prev + 1;
          const matchingStage = stages.find(s => next <= s.pct);
          if (matchingStage && matchingStage.label !== analysisStage) {
            setAnalysisStage(matchingStage.label);
          }
          return next;
        });
      }, 150);
    } else {
      setProgress(0);
      setAnalysisStage('');
    }
    return () => clearInterval(timer);
  }, [isAnalyzing]);

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
    setResults(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetchAPI('/analyze/audio', {
        method: 'POST',
        body: formData
      });
      setResults(response);
    } catch (err: any) {
      setError(err.message || "Audio analysis failed due to system constraint.");
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCopyTranscript = () => {
    if (!results || !results.transcript) return;
    navigator.clipboard.writeText(results.transcript);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleDownloadReport = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ASTRA_Threat_Intel_${results.id || 'report'}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Audio Intelligence</h1>
        <p className="text-secondary font-mono text-sm">BATCH CORRELATION MODULE • UPLOAD RECORDINGS FOR THREAT CLASSIFICATION</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload & Signal Waveform Panel */}
        <div className="glass-panel p-6 flex flex-col min-h-[480px]">
          {!file ? (
            <div 
              className="border-2 border-dashed border-white/10 rounded-2xl p-12 flex flex-col items-center justify-center text-center hover:border-white/20 hover:bg-white/5 transition-all cursor-pointer h-full"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => document.getElementById('audio-upload')?.click()}
            >
              <div className="bg-white/5 p-4 rounded-full mb-4 border border-white/10">
                <UploadCloud className="w-8 h-8 text-secondary" />
              </div>
              <h3 className="text-lg font-medium text-white mb-2">Upload Audio Recording</h3>
              <p className="text-sm text-secondary mb-6 max-w-sm">
                Drag and drop your MP3, WAV, AAC, M4A, or OGG file here, or click to browse.
              </p>
              <button className="bg-white text-black px-6 py-2 rounded-lg font-medium hover:bg-white/90 transition-colors">
                Select Audio File
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
            <div className="flex flex-col h-full justify-between">
              {/* File Info Header */}
              <div className="glass-card p-4 flex items-center gap-4 border border-white/10 bg-white/5 rounded-xl">
                <div className="bg-white/10 p-3 rounded-lg">
                  <FileAudio className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-white truncate">{file.name}</h3>
                  <p className="text-xs text-secondary font-mono">{(file.size / 1024 / 1024).toFixed(2)} MB • Audio Signal</p>
                </div>
                <button 
                  onClick={() => { setFile(null); setResults(null); }}
                  className="text-xs text-secondary hover:text-white font-mono uppercase tracking-wider"
                >
                  REMOVE
                </button>
              </div>

              {error && <p className="my-4 text-center text-error text-xs font-mono">{error}</p>}

              {/* Waveform Visualization area */}
              <div className="flex-1 flex flex-col items-center justify-center py-8">
                {isAnalyzing ? (
                  <div className="flex flex-col items-center w-full">
                    {/* Simulated live visualizer bars */}
                    <div className="flex items-center gap-1.5 h-16 mb-6">
                      {[...Array(14)].map((_, i) => (
                        <div 
                          key={i} 
                          className="w-1 bg-white rounded-full animate-waveform" 
                          style={{ 
                            height: '100%', 
                            animationDelay: `${i * 0.1}s`,
                            animationDuration: `${0.6 + Math.random() * 0.4}s`
                          }}
                        />
                      ))}
                    </div>
                    <div className="w-full max-w-xs bg-white/5 rounded-full h-1.5 mb-2 overflow-hidden">
                      <div 
                        className="bg-white h-full transition-all duration-300" 
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <h3 className="text-white font-mono text-xs uppercase tracking-widest">{analysisStage}...</h3>
                    <p className="text-[10px] text-secondary font-mono mt-1">{progress}% Complete</p>
                  </div>
                ) : !results ? (
                  <div className="text-center">
                    <button 
                      onClick={analyzeAudio}
                      className="bg-white text-black px-8 py-3 rounded-xl font-bold tracking-wide hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all font-mono uppercase text-xs"
                    >
                      START ML PIPELINE
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-center">
                    <div className="bg-white/10 p-4 rounded-full mb-4 border border-white/20">
                      <CheckCircle2 className="w-8 h-8 text-primary" />
                    </div>
                    <h3 className="text-white font-medium mb-1">Signal Processing Complete</h3>
                    <p className="text-sm text-secondary">Neural classification results extracted.</p>
                  </div>
                )}
              </div>

              {/* Progress Stage Timeline */}
              {isAnalyzing && (
                <div className="border-t border-white/5 pt-4 space-y-2">
                  <span className="text-[10px] text-secondary font-mono uppercase tracking-widest block mb-2">Analysis Timeline:</span>
                  <div className="grid grid-cols-6 gap-2">
                    {stages.map((stg, i) => (
                      <div key={i} className="flex flex-col gap-1">
                        <div className={`h-1 rounded ${progress >= stg.pct ? 'bg-primary' : 'bg-white/10'}`} />
                        <span className="text-[8px] text-secondary font-mono text-center truncate">STAGE_{i+1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Intelligence Report Result Panel */}
        <div className={`glass-panel p-6 flex flex-col transition-all duration-500 overflow-y-auto max-h-[640px] ${results && results.risk_score > 70 ? 'border-error/30 shadow-[0_0_30px_rgba(255,180,171,0.05)]' : ''}`}>
          <div className="flex justify-between items-center mb-6 border-b border-white/10 pb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-white" />
              <h2 className="font-mono font-bold tracking-widest text-sm text-white">INTELLIGENCE REPORT</h2>
            </div>
            {results && (
              <div className="flex gap-2">
                <button 
                  onClick={handleDownloadReport}
                  className="bg-transparent border border-white/15 hover:border-white text-white p-1.5 rounded-lg transition-all"
                  title="Download JSON Payload"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button 
                  onClick={handleCopyTranscript}
                  className="bg-transparent border border-white/15 hover:border-white text-white p-1.5 rounded-lg transition-all"
                  title="Copy Transcript"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {!results && !isAnalyzing && (
            <div className="flex-1 flex flex-col items-center justify-center text-secondary font-mono text-sm text-center py-20">
              <Activity className="w-8 h-8 text-white/20 mb-3 animate-pulse" />
              <span>WAITING FOR AUDIO SIGNAL INPUT...</span>
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
              {/* Top Summary Widgets */}
              <div className="flex gap-4">
                <div className="flex-1 glass-card p-4">
                  <p className="text-[10px] text-secondary font-mono mb-1">CLASSIFIED SCAM CATEGORY</p>
                  <p className="text-white font-medium">{results.scam_type}</p>
                </div>
                <div className={`glass-card p-4 w-32 flex flex-col items-center justify-center border ${results.risk_score > 70 ? 'border-error/50 bg-error/10 text-error' : 'border-white/20 text-white'}`}>
                  <p className="text-[10px] font-mono mb-1 opacity-70">RISK INDEX</p>
                  <p className="text-2xl font-bold font-mono">{(results.risk_score).toFixed(0)}%</p>
                </div>
              </div>

              {/* RAG Knowledge base Matches */}
              {results.similar_scams && results.similar_scams.length > 0 && (
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <h3 className="text-xs font-mono text-primary mb-2">RAG SIMILAR THREAT CAMPAIGNS</h3>
                  <div className="space-y-2">
                    {results.similar_scams.map((s: any, idx: number) => (
                      <div key={idx} className="flex justify-between items-center text-sm border-b border-white/5 pb-1.5 last:border-b-0 last:pb-0">
                        <span className="text-white font-medium">{s.campaign_name}</span>
                        <span className="text-secondary font-mono">{(s.similarity_score * 100).toFixed(1)}% Core Match</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Transcript */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-sm font-medium text-white">Whisper Neural Transcript</h3>
                  {copySuccess && <span className="text-[10px] text-green-400 font-mono">COPIED TO CLIPBOARD</span>}
                </div>
                <div className="bg-[#111111] p-4 rounded-xl border border-white/10 text-secondary leading-relaxed text-sm max-h-[160px] overflow-y-auto">
                  {results.transcript || "Empty transcript."}
                </div>
              </div>

              {/* AI Threat Explanation */}
              {results.explanation && (
                <div>
                  <h3 className="text-sm font-medium text-white mb-2">Neural Core Explanation</h3>
                  <div className="bg-[#111111] p-4 rounded-xl border border-white/10 text-secondary leading-relaxed text-sm font-mono text-[12px]">
                    {results.explanation}
                  </div>
                </div>
              )}

              {/* Threat Indicators */}
              {results.indicators && results.indicators.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-white mb-3">Threat Key Indicators</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.indicators.map((ind: any, i: number) => (
                      <span 
                        key={i} 
                        className="px-3 py-1 bg-white/5 border border-white/10 rounded-md text-xs font-mono text-white" 
                        title={ind.description}
                      >
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
