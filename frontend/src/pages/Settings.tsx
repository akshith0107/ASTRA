import React, { useState } from 'react';
import { UserCircle, Shield, Radar, Cpu, Download, Trash2, Copy, Bell, HardDrive, ShieldAlert } from 'lucide-react';

export default function Settings() {
  const [threshold, setThreshold] = useState(85);
  const [audioAlerts, setAudioAlerts] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  return (
    <main className="max-w-container-max mx-auto pb-stack-lg">
      <header className="mb-stack-lg">
        <h1 className="text-display-lg font-display-lg text-primary mb-2">System Configuration</h1>
        <p className="text-on-surface-variant text-body-md font-body-md max-w-2xl">
          Manage operator credentials, algorithmic thresholds, and network protocols.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        {/* Left Column: Profile & Privacy */}
        <div className="lg:col-span-4 flex flex-col gap-gutter">
          {/* Profile Section */}
          <section className="bg-matte-black border border-border-subtle rounded-3xl p-6 backdrop-blur-xl">
            <div className="flex items-center gap-4 mb-6">
              <UserCircle className="w-5 h-5 text-silver-gray" />
              <h2 className="text-label-caps font-label-caps text-primary">OPERATOR PROFILE</h2>
            </div>
            
            <div className="flex items-center gap-4 mb-6 pb-6 border-b border-border-subtle">
              <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-border-subtle">
                <img 
                  alt="Profile Avatar" 
                  className="w-full h-full object-cover" 
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuBB65p0_oeZTMWmTuKm0lQBp4mudo8kd_-sh5C9iusFIVmTj0n3XeKjnYoPiDk-Zq812nNwRny9qRkQLfORI1gkXP3J-ptkQDC5l6iYhj4sSIwbF8MTbjykNI8vqLZVte9ZWboWTAxlifvIL7BTFomgDn4ENdWoaX3I0P3kCF_U2f3F-p9aA0vGXrAR_SLYIwW5DXJokVP2RugLhLXBhm5M3NY0dsNa5N4G6O-lReKx6nmvAes73kaAwB9i8TEKams3DUbCPHtAFSM"
                />
              </div>
              <div>
                <div className="text-body-md font-body-md text-primary font-medium">Alex Chen</div>
                <div className="text-label-mono font-label-mono text-on-surface-variant mt-1">alex.chen@sentinelx.net</div>
                <div className="mt-2 inline-block px-2 py-1 bg-surface-container-high rounded text-[10px] text-silver-gray uppercase tracking-wider">
                  Level 4 Clearance
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-label-caps font-label-caps text-silver-gray mb-2">Display Name</label>
                <input 
                  className="bg-charcoal border border-border-subtle rounded-lg text-primary w-full px-3 py-2 text-body-sm font-body-sm focus:border-white focus:outline-none focus:shadow-[0_0_10px_rgba(255,255,255,0.1)] transition-all" 
                  type="text" 
                  defaultValue="OPERATOR_01"
                />
              </div>
              <div>
                <label className="block text-label-caps font-label-caps text-silver-gray mb-2">Role</label>
                <input 
                  className="bg-charcoal border border-border-subtle rounded-lg text-primary w-full px-3 py-2 text-body-sm font-body-sm opacity-50 cursor-not-allowed" 
                  disabled 
                  type="text" 
                  value="Lead Threat Analyst"
                />
              </div>
            </div>
            
            <div className="mt-6 pt-6 border-t border-border-subtle grid grid-cols-2 gap-4">
              <div>
                <div className="text-label-caps font-label-caps text-silver-gray mb-1">Session Time</div>
                <div className="text-label-mono font-label-mono text-primary">04:12:55</div>
              </div>
              <div>
                <div className="text-label-caps font-label-caps text-silver-gray mb-1">Nodes Active</div>
                <div className="text-label-mono font-label-mono text-primary">14,204</div>
              </div>
            </div>
          </section>

          {/* Privacy Section */}
          <section className="bg-matte-black border border-border-subtle rounded-3xl p-6 backdrop-blur-xl">
            <div className="flex items-center gap-4 mb-6">
              <Shield className="w-5 h-5 text-silver-gray" />
              <h2 className="text-label-caps font-label-caps text-primary">PRIVACY & DATA</h2>
            </div>
            <p className="text-body-sm font-body-sm text-on-surface-variant mb-6">
              Manage your local telemetry and audit logs.
            </p>
            <div className="space-y-4">
              <button className="w-full py-2 px-4 bg-transparent border border-silver-gray text-primary rounded-lg hover:border-white hover:shadow-[inset_0_0_10px_rgba(255,255,255,0.05)] transition-all flex items-center justify-between group">
                <span className="text-body-sm font-body-sm">Export Audit Log</span>
                <Download className="w-4 h-4 text-silver-gray group-hover:text-primary transition-colors" />
              </button>
              <button className="w-full py-2 px-4 border border-error text-error rounded-lg hover:bg-error/10 transition-colors flex items-center justify-between group">
                <span className="text-body-sm font-body-sm">Purge Local Cache</span>
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </section>
        </div>

        {/* Right Column: Settings & System */}
        <div className="lg:col-span-8 flex flex-col gap-gutter">
          {/* Detection Preferences */}
          <section className="bg-matte-black border border-border-subtle rounded-3xl p-6 backdrop-blur-xl">
            <div className="flex items-center gap-4 mb-6">
              <Radar className="w-5 h-5 text-silver-gray" />
              <h2 className="text-label-caps font-label-caps text-primary">DETECTION PREFERENCES</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-label-caps font-label-caps text-silver-gray mb-3 flex justify-between">
                    <span>Alert Sensitivity Threshold</span>
                    <span className="text-primary">{threshold}%</span>
                  </label>
                  <input 
                    className="w-full h-1 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-white" 
                    max="100" 
                    min="0" 
                    onChange={(e) => setThreshold(Number(e.target.value))} 
                    type="range" 
                    value={threshold}
                  />
                  <div className="flex justify-between text-[10px] text-on-surface-variant mt-2 font-mono uppercase tracking-widest">
                    <span>Lenient</span>
                    <span>Aggressive</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-body-sm font-body-sm text-primary">Audio Alerts</div>
                    <div className="text-[12px] text-on-surface-variant mt-1">Play sounds for critical events</div>
                  </div>
                  <button 
                    onClick={() => setAudioAlerts(!audioAlerts)}
                    className={`relative inline-flex h-5 w-10 items-center rounded-full transition-colors ${audioAlerts ? 'bg-white' : 'bg-surface-container-high'}`}
                  >
                    <span className={`inline-block h-5 w-5 transform rounded-full bg-charcoal border-2 border-border-subtle transition-transform ${audioAlerts ? 'translate-x-5 border-white' : 'translate-x-0'}`} />
                  </button>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-body-sm font-body-sm text-primary">Auto-Save Telemetry</div>
                    <div className="text-[12px] text-on-surface-variant mt-1">Continuously dump logs to disk</div>
                  </div>
                  <button 
                    onClick={() => setAutoSave(!autoSave)}
                    className={`relative inline-flex h-5 w-10 items-center rounded-full transition-colors ${autoSave ? 'bg-white' : 'bg-surface-container-high'}`}
                  >
                    <span className={`inline-block h-5 w-5 transform rounded-full bg-charcoal border-2 border-border-subtle transition-transform ${autoSave ? 'translate-x-5 border-white' : 'translate-x-0'}`} />
                  </button>
                </div>
                
                <div className="flex items-center justify-between opacity-50">
                  <div>
                    <div className="text-body-sm font-body-sm text-primary flex items-center gap-2">
                      Heuristic Analysis <ShieldAlert className="w-3 h-3 text-silver-gray" />
                    </div>
                    <div className="text-[12px] text-on-surface-variant mt-1">Requires Level 5 Clearance</div>
                  </div>
                  <button disabled className="relative inline-flex h-5 w-10 items-center rounded-full bg-surface-container-high cursor-not-allowed">
                    <span className="inline-block h-5 w-5 transform translate-x-0 rounded-full bg-charcoal border-2 border-border-subtle" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* System Configuration */}
          <section className="bg-matte-black border border-border-subtle rounded-3xl p-6 relative overflow-hidden backdrop-blur-xl">
            {/* Subtle background noise/grid effect for tech feel */}
            <div 
              className="absolute inset-0 opacity-10 pointer-events-none" 
              style={{ backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, #fff 2px, #fff 4px)', backgroundSize: '100% 4px' }}
            ></div>
            
            <div className="relative z-10">
              <div className="flex items-center gap-4 mb-6">
                <Cpu className="w-5 h-5 text-silver-gray" />
                <h2 className="text-label-caps font-label-caps text-primary">NEURAL CORE & API</h2>
              </div>
              
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-label-caps font-label-caps text-silver-gray mb-2">Whisper Model Endpoint</label>
                    <select className="bg-charcoal border border-border-subtle rounded-lg text-primary w-full px-3 py-2 text-body-sm font-body-sm appearance-none focus:border-white focus:outline-none">
                      <option>Local (Fastest)</option>
                      <option selected>Cloud Tier 1 (High Accuracy)</option>
                      <option>Cloud Tier 2 (Experimental)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-label-caps font-label-caps text-silver-gray mb-2">LLM Provider</label>
                    <select className="bg-charcoal border border-border-subtle rounded-lg text-primary w-full px-3 py-2 text-body-sm font-body-sm appearance-none focus:border-white focus:outline-none">
                      <option selected>OpenAI (GPT-4o)</option>
                      <option>Anthropic (Claude 3.5)</option>
                      <option>Local (Llama 3)</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-label-caps font-label-caps text-silver-gray mb-2">Primary API Key</label>
                  <div className="flex gap-2">
                    <input 
                      className="bg-charcoal border border-border-subtle rounded-lg text-primary w-full px-3 py-2 text-label-mono font-label-mono focus:border-white focus:outline-none" 
                      readOnly 
                      type="password" 
                      value="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    />
                    <button className="bg-transparent border border-silver-gray text-primary rounded-lg px-4 py-2 flex items-center justify-center hover:border-white transition-colors" title="Copy Key">
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-[10px] text-on-surface-variant mt-2 font-mono uppercase tracking-widest">
                    Key last rotated on 2023-10-24 14:00 UTC
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Action Bar & About */}
          <div className="flex flex-col-reverse md:flex-row justify-between items-center gap-4 mt-4">
            <div className="flex items-center gap-4 text-label-mono font-label-mono text-[10px] text-on-surface-variant uppercase tracking-widest">
              <span>SENTINELX v2.4.1-alpha</span>
              <span className="w-1 h-1 rounded-full bg-border-subtle"></span>
              <span className="flex items-center gap-1 text-primary">
                <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span> 
                Systems Nominal
              </span>
            </div>
            <div className="flex gap-4 w-full md:w-auto">
              <button className="bg-transparent border border-silver-gray text-primary rounded-lg px-6 py-2 text-body-sm font-body-sm hover:border-white transition-all flex-1 md:flex-none">
                Discard Changes
              </button>
              <button className="bg-white text-black rounded-lg px-6 py-2 text-body-sm font-body-sm font-bold hover:bg-white/90 transition-all flex-1 md:flex-none">
                Deploy Config
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
