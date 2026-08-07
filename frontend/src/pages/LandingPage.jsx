import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button, GlassCard } from '../components/shared';
import { Map, Zap, Calendar, Heart, RefreshCw } from 'lucide-react';
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
  const { setLogistics, setPersona, setAutoRunPlan } = useTripStore();
  const [seasonalPicks, setSeasonalPicks] = useState(INITIAL_SEASONAL_PICKS);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const calculateOptimal7DayDates = (tag, destName) => {
    const year = new Date().getFullYear();
    const s = ((tag || '') + ' ' + (destName || '')).toLowerCase();
    
    if (s.includes('autumn') || s.includes('fall') || s.includes('momiji')) {
      return { startStr: `Oct 15, ${year}`, endStr: `Oct 21, ${year}` };
    } else if (s.includes('winter') || s.includes('snow') || s.includes('ice')) {
      return { startStr: `Jan 10, ${year + 1}`, endStr: `Jan 16, ${year + 1}` };
    } else if (s.includes('spring') || s.includes('sakura') || s.includes('tulip') || s.includes('blossom')) {
      return { startStr: `Apr 05, ${year}`, endStr: `Apr 11, ${year}` };
    }
    return { startStr: `Jul 10, ${year}`, endStr: `Jul 16, ${year}` };
  };

  const handleCardClick = async (dest) => {
    const targetDest = dest.name || dest.destination;
    const { startStr, endStr } = calculateOptimal7DayDates(dest.tag, targetDest);

    setLogistics({ 
      origin: dest.origin || 'Singapore',
      destination: targetDest,
      startDate: startStr,
      endDate: endStr,
      numAdults: 2,
      numChildren: 1,
      numInfants: 0,
      selfDrive: dest.selfDrive || dest.self_drive || false,
      noBudget: true,
      budget: 0
    });
    
    setPersona('Family', {
      title: dest.title || targetDest,
      rules: `Family vacation with 2 Adults & 1 Child. Agent recommendations for top sights, local dining, and shopping.`,
      tempo: 'Medium',
      dining: 'Agent Recommended Sights & Food',
      lodging: 'Boutique & Family Stays'
    });

    // Check if pre-computed saved trip already exists in database
    try {
      const savedTrips = await apiClient.getSavedTrips();
      if (savedTrips && Array.isArray(savedTrips)) {
        const primaryCity = targetDest.split(',')[0].trim().toLowerCase();
        const existing = savedTrips.find(t => 
          t.destination && t.destination.toLowerCase().includes(primaryCity)
        );
        if (existing) {
          console.log('💾 Found pre-computed seasonal trip in database! Loading from cache:', existing);
          useTripStore.getState().loadSavedTrip(existing);
          navigate('/desk');
          return;
        }
      }
    } catch (e) {
      console.warn('Could not query saved trips cache:', e);
    }
    
    setAutoRunPlan(true);
    navigate('/desk');
  };

  const handleRefreshPicks = async () => {
    setIsRefreshing(true);
    try {
      const data = await apiClient.fetchLiveSeasonalPicks();
      if (data && Array.isArray(data) && data.length > 0) {
        const formatted = data.map((item, idx) => ({
          name: item.destination || item.name || 'Zurich, Switzerland',
          continent: item.continent ? `🌐 ${item.continent}` : INITIAL_SEASONAL_PICKS[idx % 6].continent,
          origin: item.origin || 'Singapore',
          tag: item.title || item.season || 'Seasonal Pick',
          reason: item.reason || 'Peak seasonal weather and local food highlights.',
          persona: item.persona || 'Family',
          selfDrive: item.self_drive || false,
          img: INITIAL_SEASONAL_PICKS[idx % 6].img
        }));
        setSeasonalPicks(formatted);
      } else {
        const fallback = await apiClient.getSeasonalPackages();
        if (fallback) setSeasonalPicks(INITIAL_SEASONAL_PICKS);
      }
    } catch (e) {
      console.warn('Using default seasonal picks:', e);
    } finally {
      setIsRefreshing(false);
    }
  };

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
