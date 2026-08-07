import { create } from 'zustand';

export const useTripStore = create((set) => ({
  // Logistics
  origin: '',
  destination: '',
  startDate: '',
  endDate: '',
  numAdults: 2,
  numChildren: 0,
  numInfants: 0,
  selfDrive: false,
  noBudget: false,
  budget: 5000,
  currency: 'USD',
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

  // Plan results
  planResult: null,
  planStatus: 'idle', // 'idle', 'planning', 'complete', 'error'
  autoRunPlan: false,
  setAutoRunPlan: (flag) => set({ autoRunPlan: flag }),
  setPlanResult: (result, status) => set({ planResult: result, planStatus: status }),
  startPlanning: () => set({ planStatus: 'planning', planResult: null, agentProgress: {}, currentNode: 'starting', autoRunPlan: false }),

  // Agent progress
  agentProgress: {},
  currentNode: null,
  updateAgentProgress: (node, status) => set((state) => ({
    currentNode: status === 'running' ? node : state.currentNode,
    agentProgress: { ...state.agentProgress, [node]: status }
  })),

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
