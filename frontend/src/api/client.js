const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchJSON(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

export const apiClient = {
  planTrip: (inputs) => fetchJSON('/api/trips/plan', { method: 'POST', body: JSON.stringify(inputs) }),
  getSavedTrips: () => fetchJSON('/api/trips/saved'),
  getTripPlan: (tripId) => fetchJSON(`/api/trips/${tripId}`),
  saveTripPlan: (planId, data) => fetchJSON(`/api/trips/${planId}/save`, { method: 'POST', body: JSON.stringify(data) }),
  getProfile: () => fetchJSON('/api/profile'),
  saveProfile: (data) => fetchJSON('/api/profile', { method: 'PUT', body: JSON.stringify(data) }),
  getPersonas: () => fetchJSON('/api/personas'),
  getSeasonalSurprise: () => fetchJSON('/api/surprise/seasonal'),
  getSeasonalPackages: () => fetchJSON('/api/surprise/packages'),
  fetchLiveSeasonalPicks: () => fetchJSON('/api/surprise/refresh', { method: 'POST' }),
  sendConciergeMessage: (messages, context) => fetchJSON('/api/concierge/chat', { method: 'POST', body: JSON.stringify({ messages, context }) }),
  extractPlanFromChat: (messages) => fetchJSON('/api/concierge/extract-plan', { method: 'POST', body: JSON.stringify({ messages }) }),
  getLocations: (result, destination) => fetchJSON('/api/trips/export/locations', { method: 'POST', body: JSON.stringify({ result, destination }) }),

  connectPlanStream: (inputs, onNodeUpdate, onComplete, onError) => {
    // Mocking websocket with setTimeout for the frontend implementation since backend might not be up yet
    const nodes = ['planner', 'researcher', 'judge', 'finalizer'];
    let delay = 0;
    
    nodes.forEach((node, i) => {
      setTimeout(() => {
        onNodeUpdate(node, 'running');
      }, delay);
      delay += 1500;
      setTimeout(() => {
        onNodeUpdate(node, 'done');
      }, delay);
    });

    setTimeout(() => {
      onComplete({
        id: 'mock-123',
        status: 'approved',
        plan: {
          days: [
            { day: 1, theme: 'Arrival', activities: [{ id: 1, time: '10:00 AM', title: 'Check in', cost: 0, category: 'hotel' }] }
          ]
        },
        hotel_recommendations: '## Hotels\n\n1. **Grand Plaza** - $200/night',
        purchasing_guide: '## Flights\n\nFlight $500',
        judge_verdict: 'Approved',
        judge_score: 95
      });
    }, delay + 500);
  }
};
