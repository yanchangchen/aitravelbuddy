import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button, GlassCard } from '../components/shared';
import { Map as MapIcon, Zap, Calendar, Heart, RefreshCw } from 'lucide-react';
import { useTripStore } from '../stores/tripStore';
import { apiClient } from '../api/client';

const INITIAL_SEASONAL_PICKS = [
  { 
    name: 'Kyoto & Hokkaido, Japan', 
    continent: '🌏 Asia', 
    tag: 'Autumn Foliage & Lavender', 
    persona: 'Couple', 
    reason: 'Temples surrounded by crimson momiji leaves and self-drive lavender routes.',
    img: 'linear-gradient(to bottom, rgba(15,23,42,0.3), var(--bg-primary)), url("https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500&q=80")' 
  },
  { 
    name: 'Swiss Alps, Switzerland', 
    continent: '🌍 Europe', 
    tag: 'Alpine Train Explorer', 
    persona: 'Couple', 
    reason: 'Glacier Express trains, crystal mountain lakes, and Jungfrau peaks.',
    img: 'linear-gradient(to bottom, rgba(15,23,42,0.3), var(--bg-primary)), url("https://images.unsplash.com/photo-1531315630201-bb15abeb1653?w=500&q=80")' 
  },
  { 
    name: 'Banff & Lake Louise, Canada', 
    continent: '🌎 North America', 
    tag: 'Turquoise Lakes & Glaciers', 
    persona: 'Solo', 
    reason: 'Icefields Parkway drive, turquoise glacial waters, and alpine wildlife.',
    img: 'linear-gradient(to bottom, rgba(15,23,42,0.3), var(--bg-primary)), url("https://images.unsplash.com/photo-1517411032315-54ef2cb783bb?w=500&q=80")' 
  },
  { 
    name: 'Cusco & Machu Picchu, Peru', 
    continent: '🌎 South America', 
    tag: 'Inca Trail & Sacred Valley', 
    persona: 'Custom', 
    reason: 'Ancient citadel above the clouds, Sacred Valley ruins, and Andean markets.',
    img: 'linear-gradient(to bottom, rgba(15,23,42,0.3), var(--bg-primary)), url("https://images.unsplash.com/photo-1526392060635-9d6019884377?w=500&q=80")' 
  },
  { 
    name: 'Cape Town & Garden Route, South Africa', 
    continent: '🌍 Africa', 
    tag: 'Table Mountain & Safari', 
    persona: 'Family', 
    reason: 'Whale watching along Hermanus, penguin beach, and Stellenbosch vineyards.',
    img: 'linear-gradient(to bottom, rgba(15,23,42,0.3), var(--bg-primary)), url("https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=500&q=80")' 
  },
  { 
    name: 'Queenstown & Milford Sound, New Zealand', 
    continent: '🌏 Oceania', 
    tag: 'Alpine Fjords & Snow Peaks', 
    persona: 'Solo', 
    reason: 'Fjordland cruises, snow-capped alpine peaks, and adventure thrill sports.',
    img: 'linear-gradient(to bottom, rgba(15,23,42,0.3), var(--bg-primary)), url("https://images.unsplash.com/photo-1589802829985-817e51171b92?w=500&q=80")' 
  }
];

export default function LandingPage() {
  const navigate = useNavigate();
  const { setLogistics, setPersona, setAutoRunPlan, backendStatus, checkBackendHealth } = useTripStore();
  const [seasonalPicks, setSeasonalPicks] = useState(INITIAL_SEASONAL_PICKS);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    checkBackendHealth();
  }, []);

  // When backend becomes active, automatically fetch the real-world seasonal picks
  useEffect(() => {
    if (backendStatus === 'up') {
      handleRefreshPicks();
    }
  }, [backendStatus]);

  const handleCardClick = async (dest) => {
    if (backendStatus !== 'up') {
      alert("Please wait for the backend service to wake up before starting the planner!");
      return;
    }
    const targetDest = dest.name || dest.destination || dest.title || 'Tokyo, Japan';
    const tag = dest.tag || dest.title || 'Seasonal Pick';
    const reason = dest.reason || 'Peak seasonal weather and local food highlights.';
    const duration = dest.duration_days || dest.duration || 5;

    // Calculate dates starting 2 weeks from now for optimal seasonal experience
    const today = new Date();
    const startDateObj = new Date(today.getTime() + 14 * 24 * 60 * 60 * 1000);
    const endDateObj = new Date(startDateObj.getTime() + (duration - 1) * 24 * 60 * 60 * 1000);
    
    const startStr = startDateObj.toISOString().split('T')[0];
    const endStr = endDateObj.toISOString().split('T')[0];
    
    setLogistics({
      origin: dest.origin || 'Singapore',
      destination: targetDest,
      startDate: startStr,
      endDate: endStr,
      currency: 'SGD',
      numAdults: 2,
      numChildren: 1,
      numInfants: 0,
      selfDrive: dest.selfDrive || dest.self_drive || false,
      noBudget: true,
      budget: 0
    });
    
    setPersona(dest.persona === 'couple' ? 'Couple' : dest.persona === 'single' ? 'Solo' : 'Family', {
      title: dest.title || targetDest,
      rules: `Trip for ${targetDest}. Seasonal context: ${tag} — ${reason}. Curate local sights, dining, and scenic routes.`,
      tempo: 'Medium',
      dining: 'Agent Recommended Sights & Food',
      lodging: 'Boutique & Family Stays'
    });

    const seasonalGreeting = `✨ Welcome to your ${targetDest} (${tag}) Seasonal Escape! 🌍 I'm Travel Buddy, your global AI travel concierge.\n\n` +
      `For this ${duration}-day trip, I've configured our collaborative AI agents with these seasonal highlights:\n` +
      `📍 Destination: ${targetDest}\n` +
      `🌟 Seasonal Vibe: ${tag} — ${reason}\n` +
      `👥 Travelers: 2 Adults, 1 Child (Origin: ${dest.origin || 'Singapore'} | SGD Budget: Flexible)\n\n` +
      `Our multi-agent pipeline is building your live itinerary right now! While they research, what are your top priorities for ${targetDest} (e.g. food, relaxation, photography, or culture)?`;

    useTripStore.getState().setConciergeGreeting(seasonalGreeting);
    setAutoRunPlan(true);
    navigate('/desk');
  };

  const handleRefreshPicks = async () => {
    setIsRefreshing(true);
    try {
      const data = await apiClient.fetchLiveSeasonalPicks();
      const rawList = Array.isArray(data) ? data : (data?.results || []);
      if (rawList && Array.isArray(rawList) && rawList.length > 0) {
        const formatted = rawList.map((item, idx) => ({
          name: item.destination || item.name || item.title || 'Zurich, Switzerland',
          continent: item.continent ? (item.continent.includes('🌐') || item.continent.includes('🌏') || item.continent.includes('🌍') || item.continent.includes('🌎') ? item.continent : `🌐 ${item.continent}`) : INITIAL_SEASONAL_PICKS[idx % INITIAL_SEASONAL_PICKS.length].continent,
          origin: item.origin || 'Singapore',
          tag: item.title || item.persona_label || item.season || 'Trending AI Pick',
          reason: item.reason || 'Peak seasonal weather and local food highlights.',
          persona: item.persona || 'Family',
          selfDrive: item.self_drive || item.selfDrive || false,
          duration_days: item.duration_days || 5,
          img: INITIAL_SEASONAL_PICKS[idx % INITIAL_SEASONAL_PICKS.length].img
        }));
        setSeasonalPicks(formatted);
      } else {
        const packages = await apiClient.getSeasonalPackages();
        if (packages && typeof packages === 'object') {
          const currentSeason = Object.keys(packages)[0] || 'summer';
          const seasonItems = Array.isArray(packages) ? packages : (packages[currentSeason] || Object.values(packages)[0] || []);
          if (seasonItems.length > 0) {
            const formatted = seasonItems.map((item, idx) => ({
              name: item.destination || item.title || 'Zurich, Switzerland',
              continent: item.continent ? `🌐 ${item.continent}` : INITIAL_SEASONAL_PICKS[idx % INITIAL_SEASONAL_PICKS.length].continent,
              origin: item.origin || 'Singapore',
              tag: item.title || item.persona_label || 'Seasonal Pick',
              reason: item.reason || 'Peak seasonal weather and local food highlights.',
              persona: item.persona || 'Family',
              selfDrive: item.self_drive || false,
              duration_days: item.duration_days || 5,
              img: INITIAL_SEASONAL_PICKS[idx % INITIAL_SEASONAL_PICKS.length].img
            }));
            setSeasonalPicks(formatted);
          }
        }
      }
    } catch (e) {
      console.warn('Using default seasonal picks:', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '4rem 2rem' }}>
      <style>{`
        @keyframes orangeBlink {
          0% { opacity: 0.3; }
          50% { opacity: 1; }
          100% { opacity: 0.3; }
        }
        .status-dot-waiting {
          animation: orangeBlink 1.5s infinite ease-in-out;
        }
      `}</style>

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

        {/* Backend Status Traffic Light Banner */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.75rem',
          padding: '0.75rem 1.5rem',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          maxWidth: '500px',
          margin: '0 auto 2.5rem',
          fontSize: '0.9rem',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: backendStatus === 'up' ? '#10B981' : backendStatus === 'down' ? '#EF4444' : '#F59E0B',
            boxShadow: backendStatus === 'up' 
              ? '0 0 8px #10B981' 
              : backendStatus === 'down' 
                ? '0 0 8px #EF4444' 
                : '0 0 8px #F59E0B',
          }} className={backendStatus === 'waiting' ? 'status-dot-waiting' : ''} />
          <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
            {backendStatus === 'up' && '🟢 Backend Server Active & Ready'}
            {backendStatus === 'down' && '🔴 Backend Offline. Fallback mode enabled.'}
            {backendStatus === 'waiting' && '🟠 Server Waking Up (Render cold start)... Please wait.'}
          </span>
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <Button 
            size="lg" 
            onClick={() => backendStatus === 'up' && navigate('/desk')} 
            icon={Zap} 
            disabled={backendStatus !== 'up'}
            style={{ 
              fontSize: '1.25rem', 
              padding: '1rem 2rem',
              opacity: backendStatus === 'up' ? 1 : 0.6,
              cursor: backendStatus === 'up' ? 'pointer' : 'not-allowed'
            }}
          >
            {backendStatus === 'up' ? 'Start Planning' : 'Backend Waking Up...'}
          </Button>
        </motion.div>
      </header>

      <section style={{ maxWidth: '1200px', margin: '0 auto 4rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Heart color="var(--accent-coral)"/> Seasonal Inspiration</h2>
          <Button variant="secondary" icon={RefreshCw} onClick={handleRefreshPicks} disabled={isRefreshing}>
            {isRefreshing ? 'Fetching AI Picks...' : 'Refresh Picks'}
          </Button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
          {seasonalPicks.map((dest, i) => (
            <motion.div 
              key={i} 
              whileHover={{ y: -10, scale: 1.02 }} 
              onClick={() => handleCardClick(dest)}
              style={{ 
                height: '300px', 
                borderRadius: 'var(--radius-lg)', 
                background: dest.img, 
                backgroundSize: 'cover', 
                backgroundPosition: 'center', 
                display: 'flex', 
                flexDirection: 'column', 
                justify: 'flex-end', 
                padding: '1.5rem', 
                border: '1px solid var(--border-subtle)',
                cursor: 'pointer'
              }}>
              <div style={{ display: 'flex', gap: '0.5rem', alignSelf: 'flex-start', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                <span className="badge" style={{ background: 'rgba(30, 41, 59, 0.9)', color: 'var(--text-primary)', border: '1px solid var(--border-subtle)' }}>{dest.continent || '🌐 Global'}</span>
                <span className="badge" style={{ background: 'var(--accent-coral)', color: 'white' }}>{dest.tag}</span>
              </div>
              <h3 style={{ fontSize: '1.35rem', fontWeight: 700, marginBottom: '0.25rem' }}>{dest.name}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{dest.reason || 'Click to auto-generate trip plan'}</p>
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
          <MapIcon size={32} color="var(--accent-blue)" style={{ marginBottom: '1rem' }} />
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
