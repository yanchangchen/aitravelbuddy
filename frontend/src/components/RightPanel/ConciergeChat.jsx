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

  const handleSend = () => {
    if (!input.trim()) return;
    addChatMessage({ role: 'user', content: input });
    setInput('');
    setIsTyping(true);
    
    // Mock AI reply
    setTimeout(() => {
      setIsTyping(false);
      addChatMessage({ role: 'ai', content: 'I noted that. You can click "Plan Trip" when you are ready to generate the itinerary.' });
    }, 1000);
  };

  const handlePlan = () => {
    startPlanning();
    apiClient.connectPlanStream(
      {}, 
      (node, status) => updateAgentProgress(node, status),
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
