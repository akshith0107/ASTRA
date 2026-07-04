import React, { useState } from 'react';
import { Shield, Mail, Lock, ArrowRight, EyeOff, Eye, Verified } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { fetchAPI } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', email); // OAuth2 form uses 'username' field for email/username
      formData.append('password', password);
      
      const response = await fetchAPI('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });
      
      await login(response.access_token, response.refresh_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-background text-primary min-h-screen flex overflow-hidden font-body-md selection:bg-surface-variant selection:text-primary relative -mx-8 -my-8 w-[calc(100%+4rem)] h-[calc(100vh)]">
      {/* Absolute positioning overlays */}
      <div 
        className="absolute inset-0 pointer-events-none z-10 opacity-5"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}
      ></div>
      <div 
        className="absolute inset-0 pointer-events-none z-0"
        style={{
          backgroundSize: '40px 40px',
          backgroundImage: 'linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px)'
        }}
      ></div>

      <div className="flex w-full h-screen relative z-20">
        {/* Left Panel: Branding & Intelligence Network */}
        <div className="hidden lg:flex w-1/2 flex-col relative overflow-hidden bg-matte-black border-r border-border-subtle p-edge-margin-desktop">
          <div className="absolute inset-0 w-full h-full opacity-60 mix-blend-screen z-0"></div>
          
          <div className="relative z-10 flex flex-col h-full justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-primary" />
              <h1 className="font-headline-lg text-headline-lg font-bold tracking-tighter uppercase text-primary">ASTRA</h1>
            </div>
            
            <div className="flex flex-col gap-stack-md max-w-lg mb-20">
              <h2 className="font-display-lg text-display-lg text-primary leading-tight">Predict.<br/>Detect.<br/>Protect.</h2>
              <p className="font-body-md text-body-md text-secondary border-l-2 border-border-subtle pl-4 py-1">AI-Powered Scam Intelligence Platform.</p>
            </div>
            
            <div className="flex justify-between items-end">
              <div className="font-label-mono text-label-mono text-on-surface-variant flex flex-col gap-1 uppercase">
                <span>SYS.STATUS: ONLINE</span>
                <span>NODE: GLOBAL_DEFENSE_NET</span>
              </div>
              <div className="flex gap-2">
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                <div className="w-2 h-2 rounded-full bg-surface-variant"></div>
                <div className="w-2 h-2 rounded-full bg-surface-variant"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel: Login / Signup */}
        <div className="w-full lg:w-1/2 flex items-center justify-center relative p-edge-margin-mobile lg:p-edge-margin-desktop bg-background z-20">
          
          <div className="absolute top-edge-margin-mobile left-edge-margin-mobile lg:hidden flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary" />
            <span className="font-label-caps text-label-caps font-bold tracking-wider uppercase">ASTRA</span>
          </div>
          
          <div className="bg-[#111111]/60 backdrop-blur-xl border border-border-subtle w-full max-w-[440px] rounded-[24px] p-8 md:p-10 flex flex-col gap-stack-lg shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-b from-border-subtle to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
            
            <div className="flex items-center border-b border-border-subtle pb-4 gap-6 relative">
              <button className="font-label-caps text-label-caps text-primary border-b-2 border-primary pb-4 -mb-[17px] uppercase tracking-wider relative z-10 transition-colors">Login</button>
              <Link to="/register" className="font-label-caps text-label-caps text-on-surface-variant hover:text-primary pb-4 -mb-[17px] border-b-2 border-transparent uppercase tracking-wider transition-colors">Signup</Link>
            </div>
            
            <form onSubmit={handleLogin} className="flex flex-col gap-stack-md relative z-10">
              {error && (
                <div className="bg-error/10 border border-error/30 text-error p-3 rounded-lg text-sm font-mono">
                  {error}
                </div>
              )}

              <div className="flex flex-col gap-2">
                <label className="font-label-mono text-label-mono text-secondary uppercase" htmlFor="email">Email or Username</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-[18px] h-[18px]" />
                  <input 
                    id="email" 
                    type="text" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="operator@astra.net" 
                    className="bg-[#111111] border border-border-subtle w-full h-12 rounded-lg pl-10 pr-4 font-body-md text-body-md text-primary placeholder-on-surface-variant focus:border-white focus:shadow-[0_0_15px_rgba(255,255,255,0.1)] focus:outline-none transition-all" 
                    required
                  />
                </div>
              </div>
              
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-center">
                  <label className="font-label-mono text-label-mono text-secondary uppercase" htmlFor="password">Password</label>
                  <a href="#" className="font-label-mono text-label-mono text-on-surface-variant hover:text-primary transition-colors text-[10px] underline underline-offset-2">FORGOT?</a>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-[18px] h-[18px]" />
                  <input 
                    id="password" 
                    type={showPassword ? "text" : "password"} 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••" 
                    className="bg-[#111111] border border-border-subtle w-full h-12 rounded-lg pl-10 pr-10 font-body-md text-body-md text-primary placeholder-on-surface-variant focus:border-white focus:shadow-[0_0_15px_rgba(255,255,255,0.1)] focus:outline-none transition-all" 
                    required
                  />
                  <button 
                    type="button" 
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center"
                  >
                    {showPassword ? <Eye className="w-[18px] h-[18px]" /> : <EyeOff className="w-[18px] h-[18px]" />}
                  </button>
                </div>
              </div>
              
              <div className="pt-2 flex flex-col gap-3">
                <button 
                  type="submit" 
                  disabled={isLoading}
                  className="bg-white text-[#050505] hover:opacity-90 hover:-translate-y-[1px] disabled:opacity-50 transition-all w-full h-12 rounded-lg font-label-caps text-label-caps tracking-wider uppercase flex items-center justify-center gap-2"
                >
                  {isLoading ? 'Authenticating...' : 'Continue'}
                  {!isLoading && <ArrowRight className="w-4 h-4" />}
                </button>
              </div>
            </form>
            
            <div className="mt-4 text-center z-10 relative">
              <p className="font-label-mono text-label-mono text-on-surface-variant flex items-center justify-center gap-1 text-[10px]">
                <Verified className="w-[14px] h-[14px]" />
                Protecting users from fraud in real time.
              </p>
            </div>
            
            {/* Corner decorative brackets */}
            <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-border-subtle pointer-events-none"></div>
            <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-border-subtle pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-border-subtle pointer-events-none"></div>
            <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-border-subtle pointer-events-none"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
