import React from 'react';
import { User, Mail, ShieldCheck, MapPin, Phone, Award, X } from 'lucide-react';

export default function ProfileModal({ user, onClose }) {
  if (!user) return null;

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-md rounded-2xl border border-brand-500/40 p-6 shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b dark:border-slate-800 border-slate-200 pb-4 mb-4">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-brand-500/10 text-brand-500 border border-brand-500/20">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base dark:text-slate-100 text-slate-800">My Profile</h3>
              <p className="text-[11px] text-slate-400">Account Details & Guardian Membership</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Profile Details Card */}
        <div className="space-y-3 text-xs">
          <div className="p-3.5 rounded-xl dark:bg-slate-900 bg-slate-100 border dark:border-slate-800 border-slate-200 flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-white font-extrabold text-lg shadow-md">
              {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <h4 className="font-bold text-sm dark:text-slate-100 text-slate-800">{user.name}</h4>
              <p className="text-slate-400 text-[11px]">{user.email}</p>
              <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-bold bg-brand-500/20 text-brand-400 border border-brand-500/30">
                {user.tier || 'VIP'} Member
              </span>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between p-2.5 rounded-lg dark:bg-slate-950 bg-white border dark:border-slate-800/80 border-slate-200">
              <span className="text-slate-400 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Account Role</span>
              </span>
              <span className="font-bold dark:text-slate-200 text-slate-700">{user.role}</span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-lg dark:bg-slate-950 bg-white border dark:border-slate-800/80 border-slate-200">
              <span className="text-slate-400 flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-brand-400" />
                <span>Home City</span>
              </span>
              <span className="font-bold dark:text-slate-200 text-slate-700">{user.home_city || 'Delhi / Mumbai'}</span>
            </div>

            <div className="flex items-center justify-between p-2.5 rounded-lg dark:bg-slate-950 bg-white border dark:border-slate-800/80 border-slate-200">
              <span className="text-slate-400 flex items-center space-x-2">
                <Phone className="w-4 h-4 text-cyan-400" />
                <span>Guardian Priority Line</span>
              </span>
              <span className="font-bold dark:text-slate-200 text-slate-700">+91 98765 43210</span>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-3 border-t dark:border-slate-800 border-slate-200">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold shadow-md shadow-brand-600/30"
          >
            Close Profile
          </button>
        </div>
      </div>
    </div>
  );
}
