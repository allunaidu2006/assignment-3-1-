import React, { useState, useEffect } from 'react';
import { matchService } from '../services/api';
import { Activity, RefreshCw, MapPin, Clock } from 'lucide-react';

export const LiveMatches = () => {
  const [liveMatches, setLiveMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const fetchLive = async () => {
    try {
      const data = await matchService.getLiveMatches();
      setLiveMatches(data);
    } catch (err) {
      console.error('Failed to load live matches:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLive();
    const interval = setInterval(fetchLive, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await matchService.syncRealtime();
      await fetchLive();
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Activity className="w-7 h-7 text-rose-500 animate-pulse" />
            Real-Time Live Matches
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time matchday updates streaming live possession, shots, minute counters, and <strong className="text-white">mandatory stadium venues</strong>.
          </p>
        </div>

        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl shadow transition self-start sm:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
          <span>Sync Live State</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading live matches...</div>
      ) : liveMatches.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center text-slate-400">
          No live matches active at this moment. Click "Sync Live State" to start a live simulation.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {liveMatches.map((m) => (
            <div
              key={m.match_id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-6 shadow-xl space-y-4 transition"
            >
              {/* Header */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="flex items-center gap-1.5 px-2.5 py-1 bg-rose-500/10 text-rose-400 font-bold rounded-md border border-rose-500/20">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                    LIVE • {m.minute ? `${m.minute}'` : 'In Play'}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-amber-400 bg-amber-500/10 px-3 py-1 rounded-md border border-amber-500/20 font-semibold">
                  <MapPin className="w-3.5 h-3.5 text-amber-400" />
                  <span>{m.venue}</span>
                </div>
              </div>

              {/* Scoreboard */}
              <div className="flex items-center justify-between py-4 border-y border-slate-800">
                <div className="flex-1 text-center font-bold text-white text-lg">
                  {m.team_1}
                </div>
                <div className="px-5 py-2 bg-slate-800 rounded-xl text-2xl font-black text-amber-400 border border-slate-700 mx-4">
                  {m.team_1_score} - {m.team_2_score}
                </div>
                <div className="flex-1 text-center font-bold text-white text-lg">
                  {m.team_2}
                </div>
              </div>

              {/* In-game stats */}
              <div className="space-y-3 pt-1">
                <div>
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>Possession</span>
                    <span className="text-slate-200 font-semibold">{m.possession_a || 50}% - {m.possession_b || 50}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden flex">
                    <div className="bg-blue-500 h-full transition-all duration-500" style={{ width: `${m.possession_a || 50}%` }}></div>
                    <div className="bg-amber-500 h-full transition-all duration-500" style={{ width: `${m.possession_b || 50}%` }}></div>
                  </div>
                </div>

                <div className="flex justify-between text-xs text-slate-400 pt-1">
                  <span>Total Shots: <strong className="text-white">{m.shots || (m.shots_a || 0) + (m.shots_b || 0)}</strong></span>
                  <span>Match ID: <strong className="text-slate-300 font-mono">{m.match_id}</strong></span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

