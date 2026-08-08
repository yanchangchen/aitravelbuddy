import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Edit2, Trash2, Map as MapIcon, Utensils, Hotel, ShoppingCart, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

function parseItineraryMarkdown(text) {
  if (!text || typeof text !== 'string') return [];
  const dayBlocks = text.split(/(?=##?\s*Day\s*\d+)/i).filter(b => b.trim().length > 0);
  if (dayBlocks.length === 0) return [];
  
  const parsed = dayBlocks.map((block, idx) => {
    const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
    const headerLine = lines[0] || `Day ${idx + 1}`;
    const dayMatch = headerLine.match(/Day\s*(\d+)[:\s-]*(.*)/i);
    const dayNum = dayMatch ? parseInt(dayMatch[1], 10) : (idx + 1);
    const theme = dayMatch && dayMatch[2] ? dayMatch[2].replace(/^[:\s-]+/, '') : headerLine.replace(/^#+\s*/, '');

    const activities = [];
    lines.slice(1).forEach(line => {
      // Catch bullet points (-, *, +), numbers (1., 2.), or bold headers (**Morning**)
      const isBullet = /^[-*+]\s+/.test(line) || /^\d+\.\s+/.test(line) || /^\*\*[A-Za-z0-9\s():]+\*\*/.test(line);
      if (isBullet) {
        const cleanLine = line.replace(/^[-*+\d.]+\s*/, '');
        const costMatch = cleanLine.match(/(?:Est\.?\s*cost:\s*|cost:\s*)(S?\$[\d,]+|\$[\d,]+)/i);
        const costStr = costMatch ? costMatch[1] : null;
        
        let category = 'sightseeing';
        const lower = cleanLine.toLowerCase();
        if (lower.includes('lunch') || lower.includes('dinner') || lower.includes('breakfast') || lower.includes('food') || lower.includes('cuisine') || lower.includes('market') || lower.includes('dining')) {
          category = 'dining';
        } else if (lower.includes('hotel') || lower.includes('check-in') || lower.includes('resort') || lower.includes('stay') || lower.includes('lodge')) {
          category = 'hotel';
        } else if (lower.includes('flight') || lower.includes('transit') || lower.includes('train') || lower.includes('express') || lower.includes('car') || lower.includes('bus')) {
          category = 'transport';
        }

        activities.push({
          time: cleanLine.includes('(TIME)') ? cleanLine.split('(')[0].trim() : 'Scheduled Activity',
          title: cleanLine,
          cost: costStr,
          category
        });
      }
    });

    return {
      day: dayNum,
      theme: theme || `Day ${dayNum} Exploration`,
      activities: activities.length > 0 ? activities : [{ time: 'Full Day', title: block.replace(/^#+\s*/, ''), category: 'sightseeing' }]
    };
  });

  // Deduplicate by day number and filter out empty / invalid blocks
  const uniqueDaysMap = new Map();
  parsed.forEach(d => {
    // Prefer blocks that have parsed activities over empty fallback blocks
    if (!uniqueDaysMap.has(d.day) || (uniqueDaysMap.get(d.day).activities.length <= 1 && d.activities.length > 1)) {
      uniqueDaysMap.set(d.day, d);
    }
  });

  return Array.from(uniqueDaysMap.values()).sort((a, b) => a.day - b.day);
}

export default function TimelineView() {
  const { planResult, planStatus, destination, partialResult, selectedLocation, setSelectedLocation } = useTripStore();

  if (planStatus === 'planning') {
    const currentItinerary = partialResult?.itinerary;
    if (currentItinerary) {
      const parsedDays = parseItineraryMarkdown(currentItinerary);
      if (parsedDays.length > 0) {
        return (
          <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <div style={{ background: 'rgba(56, 189, 248, 0.1)', border: '1px solid var(--accent-blue)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="spinner" style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', border: '2px solid var(--accent-blue)', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
              Streaming live multi-agent itinerary generation...
            </div>
            {renderParsedDays(parsedDays, selectedLocation, setSelectedLocation)}
          </div>
        );
      }
    }

    return (
      <div style={{ padding: '3rem 2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ repeat: Infinity, repeatType: 'reverse', duration: 1.5 }}>
          <MapIcon size={64} color="var(--accent-coral)" style={{ marginBottom: '1.5rem' }} />
        </motion.div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem', background: 'var(--gradient-coral)', WebkitBackgroundClip: 'text', color: 'transparent' }}>
          Crafting Your Trip to {destination || 'Destination'}
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.125rem' }}>
          Our collaborative AI agents are researching sights, dining, hotels, and booking logistics in real-time...
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card animate-pulse" style={{ padding: '1.5rem', opacity: 0.6 }}>
              <div style={{ height: '20px', width: '30%', background: 'var(--bg-tertiary)', borderRadius: '4px', marginBottom: '0.75rem' }} />
              <div style={{ height: '16px', width: '70%', background: 'var(--bg-tertiary)', borderRadius: '4px' }} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const activeResult = planResult || (Object.keys(partialResult).length > 0 ? partialResult : null);

  if (!activeResult) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', padding: '2rem', textAlign: 'center' }}>
        <MapIcon size={64} style={{ marginBottom: '1rem', opacity: 0.2 }} />
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>No Itinerary Generated Yet</h3>
        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Click "Start Planning" or select a Seasonal Package to generate a custom itinerary.</p>
      </div>
    );
  }

  const daysData = activeResult.plan?.days || (activeResult.itinerary ? parseItineraryMarkdown(activeResult.itinerary) : []);
  daysData.sort((a, b) => (parseInt(a.day) || 0) - (parseInt(b.day) || 0));

  if (daysData.length === 0 && activeResult.itinerary) {
    return (
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
        <h2 style={{ fontSize: '1.5rem', color: 'var(--accent-coral)', marginBottom: '1rem' }}>Itinerary Details</h2>
        <div className="glass-card" style={{ padding: '1.5rem' }}>{activeResult.itinerary}</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      {renderParsedDays(daysData, selectedLocation, setSelectedLocation)}
      
      {activeResult.food_and_retail && (
        <div style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '1.25rem', color: 'var(--accent-orange)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Utensils size={20} /> Dining & Retail Highlights
          </h3>
          <div className="glass-card" style={{ padding: '1.5rem', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {activeResult.food_and_retail}
          </div>
        </div>
      )}
    </div>
  );
}

function renderParsedDays(days, selectedLocation, setSelectedLocation) {
  if (!days || !Array.isArray(days) || days.length === 0) return null;
  return days.map((day, i) => {
    if (!day) return null;
    const dayNumber = day.day || (i + 1);
    const dayTheme = day.theme || `Day ${dayNumber} Exploration`;
    const activities = Array.isArray(day.activities) ? day.activities : [];

    return (
      <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }} style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '1.35rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ background: 'var(--accent-coral)', color: '#fff', padding: '0.2rem 0.6rem', borderRadius: '6px', fontSize: '0.875rem', fontWeight: 700 }}>
            Day {dayNumber}
          </span>
          {dayTheme}
        </h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {activities.map((act, j) => {
            if (!act) return null;
            const actTitle = typeof act === 'string' ? act : (act.title || act.name || 'Scheduled Sightseeing');
            const actCategory = typeof act === 'object' && act.category ? act.category : 'sightseeing';
            const actCost = typeof act === 'object' ? act.cost : null;

            const borderColors = {
              hotel: 'var(--accent-blue)',
              sightseeing: 'var(--accent-coral)',
              dining: 'var(--accent-orange)',
              transport: 'var(--accent-green)'
            };
            const borderColor = borderColors[actCategory] || 'var(--accent-coral)';
            const isSelected = selectedLocation && (selectedLocation.name === actTitle || selectedLocation.title === actTitle);

            return (
              <div 
                key={j} 
                id={`timeline-card-${dayNumber}-${j}`}
                onClick={() => setSelectedLocation && setSelectedLocation({ name: actTitle, title: actTitle, day: dayNumber, category: actCategory })}
                className="activity-card glass-card" 
                style={{ 
                  borderColor: isSelected ? 'var(--accent-coral)' : borderColor, 
                  borderLeftWidth: '5px', 
                  padding: '1rem 1.25rem',
                  cursor: 'pointer',
                  boxShadow: isSelected ? '0 0 15px rgba(255,107,107,0.35)' : 'none',
                  background: isSelected ? 'rgba(255, 107, 107, 0.08)' : undefined,
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <p style={{ margin: 0, fontSize: '0.95rem', color: isSelected ? 'var(--accent-coral)' : 'var(--text-primary)', fontWeight: isSelected ? 600 : 400, lineHeight: '1.5' }}>
                      {actTitle}
                    </p>
                  </div>
                  {actCost && (
                    <span className="badge" style={{ background: 'var(--bg-tertiary)', color: 'var(--accent-green)', fontWeight: 600, fontSize: '0.8rem', marginLeft: '1rem', whiteSpace: 'nowrap' }}>
                      {actCost}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    );
  });
}
