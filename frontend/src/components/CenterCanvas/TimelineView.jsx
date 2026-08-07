import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Edit2, Trash2, Map } from 'lucide-react';
import { motion } from 'framer-motion';

export default function TimelineView() {
  const { planResult, planStatus, destination, currentNode } = useTripStore();

  if (planStatus === 'planning') {
    return (
      <div style={{ padding: '3rem 2rem', maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ repeat: Infinity, repeatType: 'reverse', duration: 1.5 }}>
          <Map size={64} color="var(--accent-coral)" style={{ marginBottom: '1.5rem' }} />
        </motion.div>
        <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem', background: 'var(--gradient-coral)', WebkitBackgroundClip: 'text', color: 'transparent' }}>
          Crafting Your Trip to {destination || 'Destination'}
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.125rem' }}>
          Our 4 collaborative AI agents are researching sights, dining, hotels, and booking logistics in real-time...
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

  if (!planResult || !planResult.plan || !planResult.plan.days) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        <Map size={64} style={{ marginBottom: '1rem', opacity: 0.2 }} />
        <p style={{ fontSize: '1.25rem' }}>Start a conversation or click a Seasonal Pick to generate an itinerary</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      {planResult.plan.days.map((day, i) => (
        <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} style={{ marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ background: 'var(--bg-tertiary)', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-sm)', fontSize: '1rem' }}>Day {day.day}</span>
            {day.theme}
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {day.activities.map((act, j) => {
              const borderColors = {
                hotel: 'var(--accent-blue)',
                sightseeing: 'var(--accent-coral)',
                dining: 'var(--accent-orange)',
                transport: 'var(--accent-green)'
              };
              const borderColor = borderColors[act.category] || 'var(--border-subtle)';

              return (
                <div key={j} className="activity-card glass-card" style={{ borderColor, borderLeftWidth: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ color: 'var(--accent-coral)', fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>{act.time}</div>
                      <h4 style={{ fontSize: '1.125rem', margin: '0 0 0.5rem' }}>{act.title}</h4>
                      {act.cost > 0 && <span className="badge" style={{ background: 'var(--bg-primary)' }}>Est: ${act.cost}</span>}
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn-icon"><Edit2 size={16} /></button>
                      <button className="btn-icon"><Trash2 size={16} /></button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
