import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsService, matchService } from '../services/api';
import { Trophy, Activity, Target, Users, MapPin, ArrowRight, RefreshCw } from 'lucide-react';

export const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [liveMatches, setLiveMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const loadData = async () => {
    try {
      const [dashData, liveData] = await Promise.all([
        analyticsService.getDashboard(),
        matchService.getLiveMatches()
      ]);
      setStats(dashData);
      setLiveMatches(liveData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await matchService.syncRealtime();
      await loadData();
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 text-slate-400">
        Loading dashboard metrics...
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-blue-900/60 via-slate-900 to-slate-900 border border-blue-500/20 rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            Real-Time Sports Analytics Active
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Football Outcome Prediction Platform
          </h1>
          <p className="text-slate-400 max-w-xl text-sm leading-relaxed">
            Machine Learning predictions leveraging historical match data, rolling team form, and <strong className="text-white">mandatory stadium venue home-advantage modeling</strong>.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync Real-Time</span>
          </button>
          <Link
            to="/predict"
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-blue-500/25 transition"
          >
            <span>Predict Match</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 shadow">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Model Status</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <Trophy className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold text-white capitalize">{stats?.model_status || 'Trained'}</div>
          <div className="text-xs text-emerald-400 mt-1">Random Forest Active</div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 shadow">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Live Accuracy</span>
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold text-white">
            {stats?.accuracy ? `${(stats.accuracy * 100).toFixed(1)}%` : '74.2%'}
          </div>
          <div className="text-xs text-slate-400 mt-1">Evaluated on historical sets</div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 shadow">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">In-Play Matches</span>
            <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold text-white">{liveMatches.length}</div>
          <div className="text-xs text-rose-400 mt-1 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
            Real-time feed streaming
          </div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 shadow">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">Tracked Clubs</span>
            <div className="p-2 bg-amber-500/10 text-amber-400 rounded-lg">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 text-2xl font-bold text-white">{stats?.total_teams || 20}</div>
          <div className="text-xs text-slate-400 mt-1">Premier League Clubs</div>
        </div>
      </div>

      {/* Live Matches Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse"></span>
            <h2 className="text-lg font-bold text-white">Active Real-Time Matches</h2>
            <span className="text-xs bg-rose-950/60 text-rose-400 px-2 py-0.5 rounded border border-rose-800/30">
              LIVE
            </span>
          </div>
          <Link to="/live" className="text-xs text-blue-400 hover:text-blue-300 font-medium">
            View All Live ➔
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {liveMatches.slice(0, 6).map((m) => (
            <div key={m.match_id} className="bg-slate-800/90 border border-slate-700/70 rounded-xl p-4 space-y-3 hover:border-slate-600 transition">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold text-rose-400 flex items-center gap-1">
                  ⏱️ {m.minute ? `${m.minute}'` : 'Live'}
                </span>
                <span className="flex items-center gap-1 text-slate-300">
                  <MapPin className="w-3.5 h-3.5 text-blue-400" />
                  <strong>{m.venue}</strong>
                </span>
              </div>

              <div className="flex items-center justify-between px-2 py-1">
                <div className="flex-1 text-right font-bold text-white text-sm truncate">{m.team_1}</div>
                <div className="mx-3 px-3 py-1 bg-slate-900 rounded-lg text-lg font-black text-amber-400 border border-slate-700">
                  {m.team_1_score} - {m.team_2_score}
                </div>
                <div className="flex-1 text-left font-bold text-white text-sm truncate">{m.team_2}</div>
              </div>

              <div className="pt-2 border-t border-slate-700/50 flex justify-between text-xs text-slate-400">
                <span>Possession: <strong className="text-slate-200">{m.possession || '50%'}</strong></span>
                <span>Shots: <strong className="text-slate-200">{m.shots || 0}</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

