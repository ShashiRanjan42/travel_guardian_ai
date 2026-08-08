import React, { useState } from 'react';
import { ShieldCheck, User, Lock, Mail, UserPlus, Headset, Sparkles, ArrowRight, X } from 'lucide-react';
import { api } from '../api';

export default function AuthModal({ onLoginSuccess, onCancel, canClose = false }) {
  const [isSignup, setIsSignup] = useState(false);
  const [role, setRole] = useState('CUSTOMER');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const demoAccounts = [
    { label: 'Traveller: Rohan Desai (Mumbai - Kasol)', email: 'rohan@example.com', pass: 'demo', role: 'CUSTOMER' },
    { label: 'Ops Agent: Meera Iyer', email: 'meera@wayfare.in', pass: 'demo', role: 'OPS' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      if (isSignup) throw new Error('Account creation is not available in this demo backend. Use a demo account below.');
      onLoginSuccess(await api.login(email, password));
    } catch (e) {
      setErrorMsg(e.message || 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demo) => {
    setEmail(demo.email);
    setPassword(demo.pass);
    setRole(demo.role);
    setIsSignup(false);
    // Instant login submit for seamless demo experience
    submitQuickLogin(demo.email, demo.pass, demo.role);
  };

  const submitQuickLogin = async (eMail, passWord, rOle) => {
    setLoading(true);
    try {
      onLoginSuccess(await api.login(eMail, passWord));
    } catch (e) {
      setErrorMsg(e.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-lg z-50 flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md rounded-2xl border border-brand-500/40 p-6 shadow-2xl relative overflow-hidden">
        {/* Close Button if user allowed to dismiss */}
        {canClose && onCancel && (
          <button onClick={onCancel} className="absolute top-4 right-4 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        )}

        <div className="absolute -top-12 -right-12 w-40 h-40 bg-brand-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="text-center mb-6">
          <div className="inline-flex p-3.5 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-500 text-white mb-2 shadow-lg shadow-brand-500/30 animate-pulse">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-extrabold dark:text-slate-100 text-slate-800">Travel Guardian AI</h2>
          <p className="text-xs text-slate-400 mt-1">Please sign in to access your protected travel portal</p>
        </div>

        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 mb-6">
          <button
            type="button"
            onClick={() => setIsSignup(false)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              !isSignup ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => setIsSignup(true)}
            className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              isSignup ? 'bg-brand-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Create Account
          </button>
        </div>

        {isSignup && (
          <div className="mb-4">
            <label className="text-[11px] text-slate-400 font-semibold mb-1 block">Account Role</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setRole('CUSTOMER')}
                className={`p-2 rounded-lg border text-xs font-medium flex items-center justify-center space-x-1.5 ${
                  role === 'CUSTOMER' ? 'bg-slate-800 border-brand-500 text-brand-400' : 'bg-slate-900 border-slate-800 text-slate-400'
                }`}
              >
                <User className="w-3.5 h-3.5" />
                <span>Customer</span>
              </button>
              <button
                type="button"
                onClick={() => setRole('OPS')}
                className={`p-2 rounded-lg border text-xs font-medium flex items-center justify-center space-x-1.5 ${
                  role === 'OPS' ? 'bg-slate-800 border-brand-500 text-brand-400' : 'bg-slate-900 border-slate-800 text-slate-400'
                }`}
              >
                <Headset className="w-3.5 h-3.5" />
                <span>Operations Team</span>
              </button>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="mb-4 p-2.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs text-center font-medium">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          {isSignup && (
            <div>
              <label className="text-[11px] text-slate-400 font-semibold block mb-1">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Aarav Singhania"
                  className="w-full bg-slate-950 text-xs text-slate-100 rounded-lg pl-9 pr-3 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="text-[11px] text-slate-400 font-semibold block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="customer@reliance.com or ops@guardian.ai"
                className="w-full bg-slate-950 text-xs text-slate-100 rounded-lg pl-9 pr-3 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="text-[11px] text-slate-400 font-semibold block mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 text-xs text-slate-100 rounded-lg pl-9 pr-3 py-2 border border-slate-800 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center justify-center space-x-1.5 shadow-lg shadow-brand-600/30 transition-all mt-4"
          >
            <span>{isSignup ? 'Create Guardian Account' : 'Sign In to Dashboard'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-800/80">
          <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-2 text-center">
            ⚡ Quick Demo 1-Click Logins
          </span>
          <div className="space-y-1.5">
            {demoAccounts.map((demo, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleQuickLogin(demo)}
                className="w-full text-left p-2 rounded-lg bg-slate-900/60 hover:bg-slate-800 border border-slate-800 text-[11px] flex items-center justify-between text-slate-300 transition-all"
              >
                <span className="font-semibold text-slate-200">{demo.label}</span>
                <span className="text-[10px] font-mono text-emerald-400">Instant Login →</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
