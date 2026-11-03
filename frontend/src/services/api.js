import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const matchService = {
  getMatches: async (params = {}) => {
    const res = await api.get('/matches/', { params });
    return res.data;
  },
  getTeams: async () => {
    const res = await api.get('/matches/teams/list');
    return res.data;
  },
  getVenues: async () => {
    const res = await api.get('/matches/venues');
    return res.data;
  },
  getDefaultVenue: async (team) => {
    const res = await api.get(`/matches/venues/default/${encodeURIComponent(team)}`);
    return res.data;
  },
  getLiveMatches: async () => {
    const res = await api.get('/matches/realtime/live');
    return res.data;
  },
  syncRealtime: async () => {
    const res = await api.post('/matches/realtime/sync');
    return res.data;
  },
  createMatch: async (matchData) => {
    const res = await api.post('/matches/', matchData);
    return res.data;
  }
};

export const predictService = {
  predictOutcome: async (data) => {
    // Venue is mandatory
    if (!data.venue || !data.venue.trim()) {
      throw new Error("Match Venue is mandatory for outcome prediction.");
    }
    const res = await api.post('/predict/', data);
    return res.data;
  },
  getHistory: async () => {
    const res = await api.get('/predict/history');
    return res.data;
  },
  getMetrics: async () => {
    const res = await api.get('/predict/metrics');
    return res.data;
  },
  trainModel: async () => {
    const res = await api.post('/predict/train');
    return res.data;
  }
};

export const analyticsService = {
  getDashboard: async () => {
    const res = await api.get('/analytics/dashboard');
    return res.data;
  },
  getTeamForm: async (team) => {
    const res = await api.get(`/analytics/team-form/${encodeURIComponent(team)}`);
    return res.data;
  },
  getHeadToHead: async (teamA, teamB) => {
    const res = await api.get('/analytics/head-to-head', {
      params: { team_a: teamA, team_b: teamB }
    });
    return res.data;
  }
};

export default api;

