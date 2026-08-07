import { create } from 'zustand';

export const useTripStore = create((set) => ({
  // Logistics
  origin: 'Singapore',
  destination: '',
  startDate: '',
  endDate: '',
  numAdults: 2,
  numChildren: 1,
  numInfants: 0,
  selfDrive: false,
  noBudget: true,
  budget: 5000,
  currency: 'SGD',
  setLogistics: (updates) => set((state) => ({ ...state, ...updates })),

  // Persona
  selectedPersona: 'Solo',
  customPersona: {
    title: '',
    tempo: 'Medium',
    mobility: 'Average',
    dining: 'Casual',
    lodging: 'Comfortable',
    rules: ''
  },
  setPersona: (selected, customUpdates = {}) => set((state) => ({
    selectedPersona: selected,
    customPersona: { ...state.customPersona, ...customUpdates }
  })),

  // Selected location sync (Timeline <-> Map) & Modifications
  selectedLocation: null,
  setSelectedLocation: (loc) => set({ selectedLocation: loc }),
  locationsList: [],
  setLocationsList: (locs) => set({ locationsList: locs }),
  updateItineraryText: (newText, newHotels) => set((state) => ({
    planResult: state.planResult ? { 
      ...state.planResult, 
      itinerary: newText,
      ...(newHotels ? { hotel_recommendations: newHotels } : {})
    } : { 
      destination: state.destination || 'Tokyo, Japan', 
      itinerary: newText,
      ...(newHotels ? { hotel_recommendations: newHotels } : {})
    },
    partialResult: { 
      ...state.partialResult, 
      itinerary: newText,
      ...(newHotels ? { hotel_recommendations: newHotels } : {})
    }
  })),

  // Plan results
  planResult: null,
  partialResult: {},
  planStatus: 'idle', // 'idle', 'planning', 'complete', 'error'
  autoRunPlan: false,
  cancelStreamFn: null,
  setAutoRunPlan: (flag) => set({ autoRunPlan: flag }),
  setCancelStreamFn: (fn) => set({ cancelStreamFn: fn }),
  setPlanResult: (result, status) => set({ planResult: result, planStatus: status }),
  updatePartialResult: (nodeData) => set((state) => ({
    partialResult: typeof nodeData === 'object' ? { ...state.partialResult, ...nodeData } : state.partialResult
  })),
  startPlanning: () => set((state) => ({ 
    planStatus: 'planning', 
    planResult: null, 
    partialResult: {}, 
    agentProgress: {}, 
    currentNode: 'starting', 
    overallProgress: 0, 
    selectedLocation: null, 
    autoRunPlan: false,
    conciergeMessages: [{ 
      role: 'ai', 
      content: `Hello! I am Travel Buddy — your global travel AI concierge. I see we are planning a 5-day trip to ${state.destination || 'your destination'}! How can I help tailor your itinerary today?` 
    }]
  })),
  stopPlanning: () => set((state) => {
    if (state.cancelStreamFn) {
      try { state.cancelStreamFn(); } catch (e) {}
    }
    const hasData = Object.keys(state.partialResult).length > 0;
    const finalResult = hasData ? {
      status: 'stopped',
      judge_verdict: 'Stopped early by traveler — Partial plan displayed',
      destination: state.destination || 'Destination',
      itinerary: state.partialResult.itinerary || '### Partial Itinerary\n- Sightseeing research completed.',
      food_and_retail: state.partialResult.food_and_retail || '### Dining\n- Local food recommendations.',
      hotel_recommendations: state.partialResult.hotel_recommendations || '### Accommodations\n- Recommended stays.',
      purchasing_guide: state.partialResult.purchasing_guide || '### Logistics\n- Transport options.',
      ...state.partialResult
    } : null;

    return {
      planStatus: 'complete',
      planResult: finalResult,
      cancelStreamFn: null
    };
  }),

  // Agent progress
  agentProgress: {},
  currentNode: null,
  overallProgress: 0,
  updateAgentProgress: (node, status, progress, data) => set((state) => {
    const nodeOrder = ['itinerary_agent', 'food_retail_agent', 'hospitality_agent', 'purchasing_agent', 'budget_guardrail', 'agent_as_judge'];
    const currentIdx = nodeOrder.indexOf(node);
    const newProgress = { ...state.agentProgress };
    
    if (currentIdx !== -1) {
      for (let i = 0; i < currentIdx; i++) {
        newProgress[nodeOrder[i]] = 'done';
      }
    }
    newProgress[node] = status;

    const completedCount = Object.values(newProgress).filter(v => v === 'done').length;
    const computedPct = status === 'done' ? Math.min(100, Math.round(((currentIdx + 1) / nodeOrder.length) * 100)) : Math.round((completedCount / nodeOrder.length) * 100);
    const pct = progress ? Math.round(progress * 100) : computedPct;

    const newPartial = data && typeof data === 'object' ? { ...state.partialResult, ...data } : state.partialResult;

    return {
      currentNode: status === 'running' ? node : state.currentNode,
      agentProgress: newProgress,
      overallProgress: pct,
      partialResult: newPartial
    };
  }),

  // Chat
  conciergeMessages: [{ role: 'ai', content: 'Hello! I am your Travel Buddy. How can I help you plan your trip today?' }],
  isTyping: false,
  addChatMessage: (msg) => set((state) => ({ conciergeMessages: [...state.conciergeMessages, msg] })),
  setIsTyping: (typing) => set({ isTyping: typing }),

  // Saved Trips
  savedTrips: [],
  setSavedTrips: (trips) => set({ savedTrips: trips }),
  loadSavedTrip: (trip) => set({ 
    planResult: trip, 
    planStatus: 'complete',
    destination: trip.destination || '',
    origin: trip.origin || ''
  }),

  // UI State
  leftDrawerOpen: true,
  rightPanelOpen: true,
  centerView: 'timeline', // 'timeline', 'map', 'split', 'hotels', 'flights'
  toggleLeftDrawer: () => set((state) => ({ leftDrawerOpen: !state.leftDrawerOpen })),
  toggleRightPanel: () => set((state) => ({ rightPanelOpen: !state.rightPanelOpen })),
  setCenterView: (view) => set({ centerView: view }),

  resetTrip: () => set({
    planResult: null,
    planStatus: 'idle',
    agentProgress: {},
    currentNode: null,
    conciergeMessages: [{ role: 'ai', content: 'Hello! I am your Travel Buddy. How can I help you plan your trip today?' }]
  })
}));
