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
    let socket = null;
    let cancelled = false;

    const cancel = () => {
      cancelled = true;
      if (socket) {
        try { socket.close(); } catch (e) {}
      }
    };

    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = API_BASE.replace(/^https?:\/\//, '');
      const wsUrl = `${wsProtocol}//${wsHost}/api/ws/plan`;
      
      socket = new WebSocket(wsUrl);
      let socketOpened = false;

      socket.onopen = () => {
        socketOpened = true;
        if (!cancelled) socket.send(JSON.stringify(inputs));
      };

      socket.onmessage = (event) => {
        if (cancelled) return;
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'node_update') {
            onNodeUpdate(msg.node, 'running', msg.progress, msg.data);
          } else if (msg.type === 'complete') {
            onComplete(msg.result);
          } else if (msg.type === 'error') {
            if (onError) onError(msg.message);
          }
        } catch (e) {
          console.error('Failed to parse WS message:', e);
        }
      };

      socket.onerror = (err) => {
        if (cancelled) return;
        console.warn('WebSocket error, falling back to local simulation:', err);
        if (!socketOpened) {
          fallbackMockStream(onNodeUpdate, onComplete);
        } else if (onError) {
          onError('WebSocket connection error');
        }
      };

      socket.onclose = (event) => {
        if (cancelled) return;
        if (!socketOpened) {
          fallbackMockStream(onNodeUpdate, onComplete);
        }
      };
    } catch (e) {
      if (!cancelled) {
        console.warn('Failed to establish WebSocket, running mock stream:', e);
        fallbackMockStream(onNodeUpdate, onComplete);
      }
    }

    return cancel;
  }
};

function fallbackMockStream(onNodeUpdate, onComplete) {
  const nodes = ['itinerary_agent', 'food_retail_agent', 'hospitality_agent', 'purchasing_agent', 'budget_guardrail', 'agent_as_judge'];
  let delay = 0;
  
  nodes.forEach((node, i) => {
    setTimeout(() => {
      onNodeUpdate(node, 'running', (i + 1) / nodes.length);
    }, delay);
    delay += 1200;
    setTimeout(() => {
      onNodeUpdate(node, 'done', (i + 1) / nodes.length);
    }, delay);
  });

  setTimeout(() => {
    onComplete({
      status: 'approved',
      destination: 'Kyoto, Japan',
      itinerary: '### Day 1: Historic Asakusa\n- 09:00 Senso-ji Temple ($10)\n- 12:00 Nakamise Shopping ($25)',
      food_and_retail: '### Dining\n- **Ichiran Ramen**: $20',
      hotel_recommendations: '### Accommodations\n1. **Kyoto Ryokan Sunset**: $180/night',
      purchasing_guide: '### Logistics\n- **Airfare**: $650 SGD',
      judge_verdict: 'Approved — Pass score 9/10',
      judge_score: 9
    });
  }, delay + 400);
}
