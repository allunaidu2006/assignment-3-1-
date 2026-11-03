import React, { useState, useEffect } from 'react';
import { matchService, predictService } from '../services/api';
import { ShieldCheck, MapPin, AlertCircle, Sparkles, CheckCircle2, BarChart2 } from 'lucide-react';

export const Predict = () => {
  const [teams, setTeams] = useState([]);
  const [venues, setVenues] = useState([]);
  const [teamA, setTeamA] = useState('');
  const [teamB, setTeamB] = useState('');
  const [venue, setVenue] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [teamList, venueList] = await Promise.all([
          matchService.getTeams(),
          matchService.getVenues()
        ]);
        setTeams(teamList);
        setVenues(venueList);
        if (teamList.length >= 2) {
          setTeamA(teamList[0]);
          setTeamB(teamList[1]);
        }
      } catch (err) {
        console.error('Failed to load teams/venues:', err);
      }
    };
    fetchData();
  }, []);

  // When Team A changes, automatically suggest their official stadium, but allow manual selection
  useEffect(() => {
    if (teamA) {
      matchService.getDefaultVenue(teamA).then((res) => {
        if (res?.venue) {
          setVenue(res.venue);
        }
      }).catch(() => {});
    }
  }, [teamA]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Strict validation: Venue is mandatory!
    if (!venue || !venue.trim()) {
      setError('Match Venue is strictly mandatory! Please select or enter a valid stadium.');
      return;
    }

    if (teamA === teamB) {
      setError('Home and Away teams must be different clubs.');
      return;
    }

    setLoading(true);
    try {
      const res = await predictService.predictOutcome({
        team_a: teamA,
        team_b: teamB,
        venue: venue.trim()
      });
      setPrediction(res);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed.');
    } finally {
      setLoading(false);
    }
  };

  const getOutcomeLabel = (code) => {
    if (code === 'team_a') return `${teamA} Win`;
    if (code === 'team_b') return `${teamB} Win`;
    return 'Draw';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-black text-white flex items-center gap-2">
          <ShieldCheck className="w-7 h-7 text-blue-500" />
          Match Outcome Predictor
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Predict match results with machine learning using recent form, head-to-head records, and <strong className="text-white">mandatory stadium venue home-advantage modeling</strong>.
        </p>
      </div>

      {/* Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-sm flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Team A (Home) */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Home Team (Team A)
              </label>
              <select
                value={teamA}
                onChange={(e) => setTeamA(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {teams.map((t) => (
                  <option key={t} value={t} disabled={t === teamB}>{t}</option>
                ))}
              </select>
            </div>

            {/* Team B (Away) */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Away Team (Team B)
              </label>
              <select
                value={teamB}
                onChange={(e) => setTeamB(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {teams.map((t) => (
                  <option key={t} value={t} disabled={t === teamA}>{t}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Venue - STRICTLY MANDATORY */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-amber-400" />
                Match Stadium / Venue <span className="text-rose-500 font-bold">* (MANDATORY)</span>
              </label>
              <span className="text-xs text-slate-400">Required for home-field advantage modeling</span>
            </div>

            <div className="relative">
              <input
                type="text"
                list="venues-list"
                value={venue}
                onChange={(e) => setVenue(e.target.value)}
                placeholder="Select or enter official stadium (e.g., Emirates Stadium, Anfield, Etihad Stadium)"
                required
                className="w-full bg-slate-800 border-2 border-amber-500/40 focus:border-amber-500 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/20"
              />
              <datalist id="venues-list">
                {venues.map((v) => (
                  <option key={v.venue} value={v.venue}>{v.venue} ({v.team})</option>
                ))}
              </datalist>
            </div>
            <p className="text-xs text-slate-400">
              Auto-fills to the home team's official ground, or choose any neutral/alternative venue.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 transition flex items-center justify-center gap-2 text-sm disabled:opacity-50"
          >
            {loading ? (
              <span>Running Machine Learning Model...</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Predict Match Outcome</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Prediction Result Display */}
      {prediction && (
        <div className="bg-slate-900 border border-blue-500/30 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Predicted Outcome</span>
              <h2 className="text-3xl font-black text-white mt-1">
                {getOutcomeLabel(prediction.predicted_outcome)}
              </h2>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Model Confidence</span>
              <div className="text-2xl font-black text-emerald-400 mt-1">
                {(prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Probabilities Progress Bar */}
          <div className="space-y-3">
            <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Probability Distribution</div>
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 text-center">
                <div className="text-xs text-slate-400 truncate">{teamA} Win</div>
                <div className="text-xl font-bold text-blue-400 mt-1">
                  {(prediction.prob_team_a * 100).toFixed(1)}%
                </div>
              </div>

              <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 text-center">
                <div className="text-xs text-slate-400">Draw</div>
                <div className="text-xl font-bold text-slate-300 mt-1">
                  {(prediction.prob_draw * 100).toFixed(1)}%
                </div>
              </div>

              <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 text-center">
                <div className="text-xs text-slate-400 truncate">{teamB} Win</div>
                <div className="text-xl font-bold text-amber-400 mt-1">
                  {(prediction.prob_team_b * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>

          {/* Top Feature Importances */}
          {prediction.top_features && prediction.top_features.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-slate-800">
              <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <BarChart2 className="w-4 h-4 text-blue-400" />
                Explainable AI: Key Influencing Factors
              </div>
              <div className="space-y-2">
                {prediction.top_features.map((feat, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs bg-slate-800/60 px-3 py-2 rounded-lg border border-slate-700/40">
                    <span className="text-slate-300 capitalize">
                      {feat.feature_name.replace(/_/g, ' ')}
                    </span>
                    <span className="font-semibold text-blue-400">
                      {(feat.importance * 100).toFixed(1)}% weight
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

