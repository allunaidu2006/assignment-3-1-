import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Trophy, 
  Activity, 
  Calendar, 
  BarChart2, 
  ShieldCheck, 
  MapPin,
  Menu,
  X,
  Radio
} from 'lucide-react';

export const Sidebar = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: Trophy },
    { to: '/predict', label: 'Predict Outcome', icon: ShieldCheck },
    { to: '/live', label: 'Live Matches', icon: Activity, badge: 'Live' },
    { to: '/matches', label: 'Matches', icon: Calendar },
    { to: '/analytics', label: 'Analytics', icon: BarChart2 },
  ];

  const NavContent = () => (
    <div className="h-full flex flex-col justify-between p-4">
      {/* Top Branding & Nav */}
      <div className="space-y-6">
        {/* Brand */}
        <div className="px-2 pt-2">
          <Link 
            to="/" 
            onClick={() => setMobileOpen(false)}
            className="flex items-center space-x-2.5 text-blue-500 font-extrabold text-xl tracking-tight"
          >
            <span className="text-3xl">⚽</span>
            <span className="text-white text-xl">Match<span className="text-blue-500">Predict</span></span>
          </Link>
          <div className="mt-2.5 flex items-center gap-1.5 px-2.5 py-1 bg-blue-950/60 border border-blue-500/20 rounded-lg text-[11px] font-semibold text-blue-400">
            <MapPin className="w-3 h-3 text-amber-400" />
            <span>Mandatory Venue AI</span>
          </div>
        </div>

        {/* Navigation Links in Left Side Panel */}
        <nav className="space-y-1.5">
          <div className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
            Main Menu
          </div>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                    : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{link.label}</span>
                </div>
                {link.badge && (
                  <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Platform Status Card */}
      <div className="pt-4 border-t border-slate-800/80">
        <div className="bg-slate-800/50 border border-slate-700/60 rounded-xl p-3.5 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium">Real-Time Data</span>
            <span className="flex items-center gap-1 text-emerald-400 font-semibold">
              <Radio className="w-3 h-3 animate-pulse" />
              Connected
            </span>
          </div>
          <div className="text-[11px] text-slate-400 leading-relaxed">
            Venue is <strong className="text-amber-400">mandatory</strong> for all outcome predictions.
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Top Header with Hamburger */}
      <div className="md:hidden flex items-center justify-between p-4 bg-slate-900 border-b border-slate-800 sticky top-0 z-40">
        <Link to="/" className="flex items-center space-x-2 text-blue-500 font-bold text-lg">
          <span>⚽</span>
          <span className="text-white">Match<span className="text-blue-500">Predict</span></span>
        </Link>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2 text-slate-400 hover:text-white rounded-lg focus:outline-none"
        >
          {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/60 z-40 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile Sidebar Drawer */}
      <aside
        className={`md:hidden fixed top-0 bottom-0 left-0 w-64 bg-slate-900 border-r border-slate-800 z-50 transform transition-transform duration-200 ease-in-out ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <NavContent />
      </aside>

      {/* Desktop Left Side Panel (Permanent) */}
      <aside className="hidden md:flex flex-col w-64 bg-slate-900/95 border-r border-slate-800/90 min-h-screen sticky top-0 shrink-0 select-none">
        <NavContent />
      </aside>
    </>
  );
};
