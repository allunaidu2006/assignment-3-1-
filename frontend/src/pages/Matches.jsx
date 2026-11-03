import React, { useState, useEffect } from 'react';
import { matchService } from '../services/api';
import { Calendar, MapPin, Filter } from 'lucide-react';

export const Matches = () => {
  const [matches, setMatches] = useState([]);
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        const [teamList, matchList] = await Promise.all([
          matchService.getTeams(),
          matchService.getMatches({ limit: 40 })
        ]);
        setTeams(teamList);
        setMatches(matchList);
      } catch (err) {
        console.error('Failed to load matches:', err);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const handleFilter = async (team) => {
    setSelectedTeam(team);
    setLoading(true);
    try {
      const data = await matchService.getMatches({
        limit: 40,
        team: team || undefined
      });
      setMatches(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Calendar className="w-7 h-7 text-blue-500" />
            Match Schedule & Results
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Historical and current match database with verified authentic stadiums.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedTeam}
            onChange={(e) => handleFilter(e.target.value)}
            className="bg-transparent text-sm text-white focus:outline-none"
          >
            <option value="">All Teams</option>
            {teams.map((t) => (
              <option key={t} value={t} className="bg-slate-900 text-white">{t}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-400">Loading matches...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {matches.map((m) => (
            <div
              key={m.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between hover:border-slate-700 transition"
            >
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span>{new Date(m.match_date).toLocaleDateString()}</span>
                  <span>•</span>
                  <span className="flex items-center gap-1 text-slate-300 font-medium">
                    <MapPin className="w-3 h-3 text-amber-400" />
                    {m.venue}
                  </span>
                </div>
                <div className="text-sm font-bold text-white flex items-center gap-2">
                  <span className={m.outcome === 'team_a' ? 'text-blue-400 font-extrabold' : ''}>{m.team_a}</span>
                  <span className="text-slate-500">vs</span>
                  <span className={m.outcome === 'team_b' ? 'text-blue-400 font-extrabold' : ''}>{m.team_b}</span>
                </div>
              </div>

              <div className="px-3 py-1.5 bg-slate-800 rounded-lg text-sm font-black text-white border border-slate-700">
                {m.goals_a !== null && m.goals_b !== null ? (
                  `${m.goals_a} - ${m.goals_b}`
                ) : (
                  <span className="text-xs text-slate-400 font-normal">Upcoming</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

