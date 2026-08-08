import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { GlassCard, Badge } from '../shared';
import { Hotel, MapPin, CheckCircle, Sparkles, DollarSign } from 'lucide-react';
import { motion } from 'framer-motion';

function parseHotelsMarkdown(text) {
  if (!text || typeof text !== 'string') return [];
  
  // Find recommended option name if specified
  const recMatch = text.match(/\*\*🏨\s*RECOMMENDED OPTION:\s*([^\n—–-]+)/i);
  const recommendedName = recMatch ? recMatch[1].trim().toLowerCase() : null;

  // Split by Option headers
  const optionBlocks = text.split(/(?=###?\s*(?:Option\s*\d+|Hotel\s*\d+|Recommended))/i).filter(b => b.trim().length > 0);
  if (optionBlocks.length === 0) return [];

  const hotels = [];

  optionBlocks.forEach((block, idx) => {
    const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
    const headerLine = lines[0] || `Option ${idx + 1}`;
    if (!headerLine.toLowerCase().includes('option') && !headerLine.toLowerCase().includes('hotel') && !headerLine.startsWith('#')) {
      return;
    }

    const cleanTitle = headerLine.replace(/^#+\s*/, '').replace(/^Option\s*\d+[:\s-]*/i, '').trim();
    const starCount = (cleanTitle.match(/⭐/g) || []).length || (cleanTitle.toLowerCase().includes('luxury') ? 5 : 4);
    const hotelName = cleanTitle.replace(/⭐/g, '').replace(/\(.*?\)/g, '').trim();

    let location = 'Central Destination Area';
    let whyFits = 'Curated accommodation matching itinerary zones and traveler preferences.';
    let nightlyRate = 'S$180';
    let totalStay = 'S$720';
    let amenities = ['Free High-Speed WiFi', 'Family Friendly', 'Breakfast Included'];

    lines.forEach(line => {
      const lower = line.toLowerCase();
      if (lower.includes('location:')) {
        location = line.replace(/^[-*]\s*\*\*Location:\*\*\s*/i, '').replace(/^[A-Za-z\s*:]+/, '').trim();
      } else if (lower.includes('why it fits:')) {
        whyFits = line.replace(/^[-*]\s*\*\*Why it fits:\*\*\s*/i, '').replace(/^[A-Za-z\s*:]+/, '').trim();
      } else if (lower.includes('nightly rate:')) {
        nightlyRate = line.replace(/^[-*]\s*\*\*Nightly rate:\*\*\s*/i, '').replace(/^[A-Za-z\s*:]+/, '').trim();
      } else if (lower.includes('total for stay:') || lower.includes('total:')) {
        totalStay = line.replace(/^[-*]\s*\*\*Total[^:]*:\*\*\s*/i, '').replace(/^[A-Za-z\s*:]+/, '').trim();
      } else if (lower.includes('amenities:')) {
        const rawAmenities = line.replace(/^[-*]\s*\*\*[^:]*amenities:\*\*\s*/i, '').replace(/^[A-Za-z\s*:]+/, '').trim();
        amenities = rawAmenities.split(/[,•;]/).map(a => a.trim()).filter(Boolean);
      }
    });

    const isRec = recommendedName ? (hotelName.toLowerCase().includes(recommendedName) || recommendedName.includes(hotelName.toLowerCase())) : (idx === 0);

    hotels.push({
      name: hotelName || `Boutique Hotel Option ${idx + 1}`,
      stars: starCount > 0 ? starCount : 4,
      location,
      whyFits,
      nightlyRate,
      totalStay,
      amenities: amenities.length > 0 ? amenities : ['Free WiFi', 'Breakfast Option', 'Central Location'],
      recommended: isRec
    });
  });

  return hotels;
}

export default function HotelCards() {
  const { planResult, partialResult, planStatus } = useTripStore();
  const activeResult = planResult || (Object.keys(partialResult).length > 0 ? partialResult : null);
  const hotelText = activeResult?.hotel_recommendations;

  if (!hotelText) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', padding: '3rem 2rem', textAlign: 'center' }}>
        <Hotel size={56} style={{ marginBottom: '1rem', opacity: 0.25 }} />
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          {planStatus === 'planning' ? 'Sourcing Accommodations...' : 'No Hotel Recommendations Yet'}
        </h3>
        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', maxWidth: '450px' }}>
          {planStatus === 'planning' 
            ? 'The Hospitality Agent is matching boutique stays and family lodgings near your itinerary activity zones.'
            : 'Initiate a trip plan to receive curated hotel options with pricing and amenities.'}
        </p>
      </div>
    );
  }

  const parsedHotels = parseHotelsMarkdown(hotelText);

  return (
    <div style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Hotel size={24} color="var(--accent-coral)" /> Recommended Accommodations
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Curated by Hospitality Agent to match your daily activity zones and traveler persona.
          </p>
        </div>
      </div>

      {parsedHotels.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
          {parsedHotels.map((h, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <GlassCard style={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column', 
                justifyContent: 'space-between',
                borderColor: h.recommended ? 'var(--accent-coral)' : 'var(--border-subtle)', 
                boxShadow: h.recommended ? '0 8px 24px rgba(255, 107, 107, 0.15)' : 'none',
                position: 'relative'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    {h.recommended ? (
                      <Badge variant="approved" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem', fontWeight: 700 }}>
                        <Sparkles size={12} /> Top Recommended Pick
                      </Badge>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Option {i + 1}</span>
                    )}
                    <div style={{ color: '#F59E0B', fontSize: '0.875rem' }}>{'★'.repeat(h.stars)}</div>
                  </div>

                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                    {h.name}
                  </h3>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.85rem' }}>
                    <MapPin size={14} color="var(--accent-coral)" />
                    <span>{h.location}</span>
                  </div>

                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: '1.5', marginBottom: '1.25rem' }}>
                    {h.whyFits}
                  </p>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1.5rem' }}>
                    {h.amenities.map((a, j) => (
                      <span key={j} style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', background: 'var(--bg-tertiary)', color: 'var(--text-primary)', borderRadius: 'var(--radius-sm)' }}>
                        {a}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Nightly Rate</span>
                    <strong style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>{h.nightlyRate}</strong>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Estimated Total</span>
                    <strong style={{ fontSize: '1.25rem', color: 'var(--accent-coral)', fontWeight: 800 }}>{h.totalStay}</strong>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      ) : null}

      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
          Detailed Hospitality Agent Dossier
        </h3>
        <div className="glass-card" style={{ padding: '1.5rem', whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
          {hotelText}
        </div>
      </div>
    </div>
  );
}
