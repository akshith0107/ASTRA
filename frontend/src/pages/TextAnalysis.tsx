import React, { useState } from 'react';
import { MessageSquare, Send, ShieldCheck, AlertOctagon } from 'lucide-react';
import { fetchAPI } from '../lib/api';

export default function TextAnalysis() {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeText = async () => {
    if (!text.trim()) return;
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await fetchAPI('/analyze/text', {
        method: 'POST',
        body: JSON.stringify({ text_content: text })
      });

      setResult({
        text,
        scamType: response.scam_type,
        riskScore: response.risk_score / 100, // Backend returns 0-100, we use 0-1
        timestamp: new Date().toLocaleTimeString(),
        indicators: response.indicators
      });
      setText('');
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend');
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Text Analysis</h1>
        <p className="text-secondary font-mono text-sm">BERT MULTILINGUAL CLASSIFIER • SMS / WHATSAPP / EMAIL</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="glass-panel p-6 flex flex-col h-[500px]">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare className="w-5 h-5 text-white" />
            <h2 className="font-mono font-bold tracking-widest text-sm text-white">INPUT MESSAGE</h2>
          </div>
          
          <textarea 
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste suspicious SMS, WhatsApp message, or email content here..."
            className="flex-1 w-full bg-surface border border-white/10 rounded-xl p-4 text-white placeholder-secondary focus:outline-none focus:border-white/30 resize-none transition-colors"
          />
          
          {error && <p className="mt-4 text-sm text-error">{error}</p>}

          <div className="mt-4 flex justify-end">
            <button 
              onClick={analyzeText}
              disabled={!text.trim() || isAnalyzing}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold tracking-wide transition-all ${
                !text.trim() || isAnalyzing
                  ? 'bg-surface text-secondary cursor-not-allowed'
                  : 'bg-white text-black hover:bg-white/90 shadow-[0_0_20px_rgba(255,255,255,0.3)]'
              }`}
            >
              {isAnalyzing ? 'CLASSIFYING...' : 'ANALYZE TEXT'}
              {!isAnalyzing && <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="glass-panel p-6 flex flex-col h-[500px] overflow-y-auto">
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-4 sticky top-0 bg-[#111111]/80 backdrop-blur-md z-10">
            <h2 className="font-mono font-bold tracking-widest text-sm text-white">ANALYSIS LOG</h2>
          </div>

          {!result && !isAnalyzing && (
             <div className="flex-1 flex items-center justify-center text-secondary font-mono text-sm text-center">
               AWAITING TEXT INPUT
             </div>
          )}

          <div className="space-y-4">
            {isAnalyzing && (
              <div className="glass-card p-4 border-dashed border-white/20 animate-pulse flex items-center justify-center h-24">
                <span className="font-mono text-xs text-secondary">RUNNING BERT CLASSIFICATION...</span>
              </div>
            )}
            
            {result && (
              <div className="glass-card p-4 flex flex-col gap-3 animate-in slide-in-from-right duration-300">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-mono text-secondary">{result.timestamp}</span>
                  {result.riskScore > 0.5 ? (
                    <span className="flex items-center gap-1 text-[10px] font-mono bg-error/10 text-error px-2 py-1 rounded border border-error/30">
                      <AlertOctagon className="w-3 h-3" /> HIGH RISK
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[10px] font-mono bg-primary/10 text-primary px-2 py-1 rounded border border-primary/30">
                      <ShieldCheck className="w-3 h-3" /> SAFE
                    </span>
                  )}
                </div>
                
                <p className="text-sm text-white italic">"{result.text}"</p>
                
                <div className="mt-2 pt-3 border-t border-white/10 flex justify-between items-center">
                  <div>
                    <p className="text-[10px] text-secondary font-mono">CLASSIFICATION</p>
                    <p className="text-sm font-medium text-white">{result.scamType}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-secondary font-mono">CONFIDENCE</p>
                    <p className="text-sm font-bold font-mono text-white">{(result.riskScore * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {result.indicators && result.indicators.length > 0 && (
                   <div className="mt-2 flex flex-wrap gap-2">
                     {result.indicators.map((ind: any, i: number) => (
                        <span key={i} className="px-2 py-1 bg-white/10 rounded text-[10px] font-mono text-white">
                          {ind.type}
                        </span>
                     ))}
                   </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
