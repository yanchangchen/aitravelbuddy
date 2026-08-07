import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button, GlassCard } from '../components/shared';
import { Map, Zap, Calendar, Heart } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', padding: '4rem 2rem' }}>
      <header style={{ textAlign: 'center', marginBottom: '4rem' }}>
        <motion.h1 
          initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} 
          style={{ fontSize: '4rem', fontWeight: 800, background: 'var(--gradient-coral)', WebkitBackgroundClip: 'text', color: 'transparent', marginBottom: '1rem' }}>
          Travel Buddy
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          style={{ fontSize: '1.5rem', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          AI-Powered Multi-Agent Travel Planning
        </motion.p>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <Button size="lg" onClick={() => navigate('/desk')} icon={Zap} style={{ fontSize: '1.25rem', padding: '1rem 2rem' }}>
            Start Planning
          </Button>
        </motion.div>
      </header>

      <section style={{ maxWidth: '1200px', margin: '0 auto 4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Heart color="var(--accent-coral)"/> Seasonal Inspiration</h2>
          <Button variant="secondary">Refresh Picks</Button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          {[
            { name: 'Kyoto, Japan', tag: 'Autumn Leaves', img: 'linear-gradient(to bottom, transparent, var(--bg-primary)), url("https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500&q=80")' },
            { name: 'Swiss Alps', tag: 'Winter Wonderland', img: 'linear-gradient(to bottom, transparent, var(--bg-primary)), url("https://images.unsplash.com/photo-1531315630201-bb15abeb1653?w=500&q=80")' },
            { name: 'Santorini', tag: 'Summer Escape', img: 'linear-gradient(to bottom, transparent, var(--bg-primary)), url("https://images.unsplash.com/photo-1533105079780-92b9be482077?w=500&q=80")' }
          ].map((dest, i) => (
            <motion.div key={i} whileHover={{ y: -10 }} style={{ height: '300px', borderRadius: 'var(--radius-lg)', background: dest.img, backgroundSize: 'cover', backgroundPosition: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: '1.5rem', border: '1px solid var(--border-subtle)' }}>
              <span className="badge" style={{ alignSelf: 'flex-start', marginBottom: '0.5rem', background: 'var(--accent-coral)', color: 'white' }}>{dest.tag}</span>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{dest.name}</h3>
            </motion.div>
          ))}
        </div>
      </section>

      <section style={{ maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        <GlassCard>
          <Zap size={32} color="var(--accent-coral)" style={{ marginBottom: '1rem' }} />
          <h3>4 AI Agents</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Collaborative agents handle research, planning, budgeting, and critique to build the perfect itinerary.</p>
        </GlassCard>
        <GlassCard>
          <Map size={32} color="var(--accent-blue)" style={{ marginBottom: '1rem' }} />
          <h3>Smart Budget Guard</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Real-time cost tracking ensures your entire trip stays within your defined budget constraints.</p>
        </GlassCard>
        <GlassCard>
          <Calendar size={32} color="var(--accent-green)" style={{ marginBottom: '1rem' }} />
          <h3>Personalized Trips</h3>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>From backpacking solos to luxury family vacations, your personalized persona dictates the vibe.</p>
        </GlassCard>
      </section>
    </div>
  );
}
