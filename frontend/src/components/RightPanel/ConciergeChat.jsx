import React, { useState, useRef, useEffect } from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Button } from '../shared';
import { Send, Zap, Palette } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function ConciergeChat() {
  const { conciergeMessages, addChatMessage, isTyping, setIsTyping, startPlanning, updateAgentProgress, setPlanResult } = useTripStore();
  const [input, setInput] = useState('');
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conciergeMessages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;
    const userMsg = { role: 'user', content: input };
    const updatedMessages = [...conciergeMessages, userMsg];
    addChatMessage(userMsg);
    setInput('');
    setIsTyping(true);
    
    const store = useTripStore.getState();
    const currentItinerary = store.planResult?.itinerary || store.partialResult?.itinerary || '';
    const currentDest = store.destination || store.planResult?.destination || 'Tokyo, Japan';

    try {
      const response = await apiClient.sendConciergeMessage(updatedMessages, 'Traveler planning a trip', currentItinerary, currentDest);
      const replyContent = response.message || response.content || response.text || (typeof response === 'string' ? response : 'I have noted your preferences. Click "Plan Trip" whenever you are ready!');
      addChatMessage({ role: 'ai', content: replyContent });
    } catch (e) {
      console.warn('Concierge API error, using fallback response:', e);
      addChatMessage({ role: 'ai', content: 'Got it! I have recorded your travel preferences. Click "Plan Trip" whenever you are ready to initiate the multi-agent planning pipeline.' });
    } finally {
      setIsTyping(false);
    }
  };

  const handlePlan = async () => {
    setIsTyping(true);
    let extractedDest = null;
    let extractedPersona = null;
    let customProfile = null;

    try {
      const currentDest = useTripStore.getState().destination || 'Banff & Lake Louise, Canada';
      const res = await apiClient.extractPlanFromChat(conciergeMessages, currentDest);
      const extracted = res?.plan || res;
      if (extracted) {
        if (extracted.destination) {
          extractedDest = extracted.destination;
          useTripStore.getState().setLogistics({ destination: extracted.destination });
        }
        if (extracted.persona) {
          extractedPersona = extracted.persona;
          customProfile = extracted.custom_persona_profile || {};
          useTripStore.getState().setPersona(extracted.persona, customProfile);
        }
      }
    } catch (e) {
      console.warn('Extraction skipped, proceeding with active inputs:', e);
    } finally {
      setIsTyping(false);
    }

    const store = useTripStore.getState();
    const targetDest = extractedDest || store.destination || 'Tokyo, Japan';
    
    // Compile full chat history context
    const conversationContext = conciergeMessages
      .map(m => `${m.role === 'user' ? 'Traveler' : 'Travel Buddy'}: ${m.content}`)
      .join('\n');

    startPlanning();

    const inputs = {
      origin: store.origin || 'Singapore',
      destination: targetDest,
      budget: store.noBudget ? 0 : store.budget,
      num_adults: store.numAdults || 2,
      num_children: store.numChildren || 1,
      num_infants: store.numInfants || 0,
      self_drive: store.selfDrive,
      no_budget: store.noBudget,
      currency: store.currency || 'SGD',
      dates: store.startDate && store.endDate ? `${store.startDate} - ${store.endDate}` : 'Nov 15 - Nov 20, 2026',
      num_days: 5,
      persona: extractedPersona || store.selectedPersona || 'Family',
      custom_persona_profile: store.selectedPersona === 'Custom' ? store.customPersona : customProfile,
      user_preferences: {
        dining: store.customPersona?.dining,
        lodging: store.customPersona?.lodging,
        rules: `TRAVEL BUDDY CONVERSATION HISTORY & TRAVELER PREFERENCES:\n${conversationContext}`
      }
    };

    apiClient.connectPlanStream(
      inputs, 
      (node, status, progress, nodeData) => updateAgentProgress(node, status, progress, nodeData),
      (result) => setPlanResult(result, 'complete'),
      (err) => setPlanResult(null, 'error')
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', gap: '0.5rem' }}>
        <Button size="sm" onClick={handlePlan} icon={Zap} style={{ flex: 1 }}>Plan Trip</Button>
        <Button size="sm" variant="secondary" icon={Palette} title="Apply Vibe Only" />
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {conciergeMessages.map((msg, i) => {
          const isAi = msg.role === 'ai';
          const hasItineraryProposal = isAi && (msg.content.includes('## Day') || msg.content.includes('Day 1:'));

          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: isAi ? 'flex-start' : 'flex-end', gap: '0.35rem' }}>
              <div className={`chat-bubble-${msg.role}`} style={{ padding: '0.75rem 1rem', maxWidth: '88%', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                {msg.content}
              </div>
              {hasItineraryProposal && (
                <Button 
                  size="sm" 
                  onClick={() => {
                    const dayStart = msg.content.indexOf('## Day') !== -1 ? msg.content.indexOf('## Day') : msg.content.indexOf('Day 1:');
                    const hotelStart = msg.content.indexOf('### Recommended Hotel') !== -1 ? msg.content.indexOf('### Recommended Hotel') : msg.content.indexOf('### Hotel');
                    
                    let modText = msg.content;
                    let hotelText = null;
                    
                    if (hotelStart !== -1 && hotelStart > dayStart) {
                      modText = msg.content.substring(dayStart, hotelStart).trim();
                      hotelText = msg.content.substring(hotelStart).trim();
                    } else if (dayStart !== -1) {
                      modText = msg.content.substring(dayStart).trim();
                    }
                    
                    useTripStore.getState().updateItineraryText(modText, hotelText);
                  }}
                  style={{ fontSize: '0.75rem', background: 'var(--accent-coral)', color: '#fff', padding: '0.25rem 0.6rem', marginTop: '0.25rem' }}
                >
                  Apply Modification to Timeline, Hotels & Map
                </Button>
              )}
            </div>
          );
        })}
        {isTyping && (
          <div className="chat-bubble-ai" style={{ padding: '0.75rem 1rem', maxWidth: '85%' }}>
            <span className="spinner" style={{ letterSpacing: '2px' }}>...</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ position: 'relative' }}>
          <input 
            className="input-field" 
            style={{ paddingRight: '3rem' }}
            placeholder="Tell me what you'd like..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button className="btn-icon" onClick={handleSend} style={{ position: 'absolute', right: '0.5rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--accent-coral)' }}>
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
