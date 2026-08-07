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
    
    try {
      const response = await apiClient.sendConciergeMessage(updatedMessages, 'Traveler planning a trip');
      const replyContent = response.content || response.text || (typeof response === 'string' ? response : 'I have noted your preferences. Click "Plan Trip" whenever you are ready!');
      addChatMessage({ role: 'ai', content: replyContent });
    } catch (e) {
      console.warn('Concierge API error, using fallback response:', e);
      addChatMessage({ role: 'ai', content: 'Got it! I have recorded your travel preferences. Click "Plan Trip" whenever you are ready to initiate the multi-agent planning pipeline.' });
    } finally {
      setIsTyping(false);
    }
  };

  const handlePlan = async () => {
    startPlanning();
    try {
      const res = await apiClient.extractPlanFromChat(conciergeMessages);
      const extracted = res?.plan || res;
      if (extracted) {
        if (extracted.destination) useTripStore.getState().setLogistics({ destination: extracted.destination });
        if (extracted.persona) useTripStore.getState().setPersona(extracted.persona, extracted.custom_persona_profile || {});
      }
    } catch (e) {
      console.warn('Extraction skipped, proceeding with active inputs:', e);
    }

    const store = useTripStore.getState();
    const inputs = {
      origin: store.origin || 'Singapore',
      destination: store.destination || 'Tokyo, Japan',
      budget: store.noBudget ? 0 : store.budget,
      num_adults: store.numAdults,
      num_children: store.numChildren,
      num_infants: store.numInfants,
      self_drive: store.selfDrive,
      no_budget: store.noBudget,
      currency: store.currency || 'SGD',
      dates: store.startDate && store.endDate ? `${store.startDate} - ${store.endDate}` : 'Nov 15 - Nov 20, 2026',
      num_days: 5,
      persona: store.selectedPersona,
      custom_persona_profile: store.selectedPersona === 'Custom' ? store.customPersona : null,
      user_preferences: {
        dining: store.customPersona?.dining,
        lodging: store.customPersona?.lodging,
        rules: store.customPersona?.rules
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
        {conciergeMessages.map((msg, i) => (
          <div key={i} className={`chat-bubble-${msg.role}`} style={{ padding: '0.75rem 1rem', maxWidth: '85%' }}>
            {msg.content}
          </div>
        ))}
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
