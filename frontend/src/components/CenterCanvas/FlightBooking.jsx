import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { GlassCard, Badge, Button } from '../shared';
import { Plane, Car, Ticket, ExternalLink, ShoppingBag, CheckCircle, Info } from 'lucide-react';
import { motion } from 'framer-motion';

function extractBookingLinks(text) {
  if (!text || typeof text !== 'string') return [];
  const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
  const links = [];
  let match;
  while ((match = linkRegex.exec(text)) !== null) {
    links.push({ label: match[1], url: match[2] });
  }
  return links;
}

export default function FlightBooking() {
  const { planResult, partialResult, planStatus, selfDrive, origin, destination } = useTripStore();
  const activeResult = planResult || (Object.keys(partialResult).length > 0 ? partialResult : null);
  const purchasingText = activeResult?.purchasing_guide;

  if (!purchasingText) {
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', padding: '3rem 2rem', textAlign: 'center' }}>
        <Plane size={56} style={{ marginBottom: '1rem', opacity: 0.25 }} />
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          {planStatus === 'planning' ? 'Sourcing Booking Logistics & Airfare...' : 'No Booking Guide Available Yet'}
        </h3>
        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', maxWidth: '450px' }}>
          {planStatus === 'planning' 
            ? 'The Purchasing Agent is querying live round-trip flight rates, self-drive rentals, and verified attraction booking links.'
            : 'Initiate a trip plan to generate direct booking links and logistics.'}
        </p>
      </div>
    );
  }

  const allLinks = extractBookingLinks(purchasingText);

  // Group sections by headers
  const flightSection = purchasingText.match(/###\s*✈️[^\n]*\n([\s\S]*?)(?=###|$)/i)?.[1] || '';
  const hotelSection = purchasingText.match(/###\s*🏨[^\n]*\n([\s\S]*?)(?=###|$)/i)?.[1] || '';
  const carSection = purchasingText.match(/###\s*🚗[^\n]*\n([\s\S]*?)(?=###|$)/i)?.[1] || '';
  const ticketSection = purchasingText.match(/###\s*🎫[^\n]*\n([\s\S]*?)(?=###|$)/i)?.[1] || '';

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <ShoppingBag size={24} color="var(--accent-blue)" /> Logistics & Purchasing Guide
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          Direct verified booking links and transport options curated by the Purchasing Agent.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2.5rem' }}>
        {/* Flights Card */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <GlassCard style={{ borderLeft: '4px solid var(--accent-blue)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--accent-blue)' }}>
              <Plane size={20} /> Flights & Airfare (Round-Trip)
            </h3>
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: '1rem' }}>
              {flightSection ? flightSection.trim() : `Round-trip flights from ${origin || 'Singapore'} to ${destination || 'Destination'}.`}
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
              <a 
                href={`https://www.skyscanner.com/transport/flights/${(origin || 'SIN').toLowerCase().slice(0,3)}/${(destination || 'NRT').toLowerCase().slice(0,3)}/`} 
                target="_blank" 
                rel="noreferrer"
                style={{ textDecoration: 'none' }}
              >
                <Button size="sm" variant="primary" icon={ExternalLink}>
                  Search Flights on Skyscanner
                </Button>
              </a>
              <a 
                href="https://www.google.com/travel/flights" 
                target="_blank" 
                rel="noreferrer"
                style={{ textDecoration: 'none' }}
              >
                <Button size="sm" variant="secondary" icon={ExternalLink}>
                  Google Flights
                </Button>
              </a>
            </div>
          </GlassCard>
        </motion.div>

        {/* Accommodation Booking Card */}
        {hotelSection && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <GlassCard style={{ borderLeft: '4px solid var(--accent-coral)' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--accent-coral)' }}>
                🏨 Accommodation Booking Portals
              </h3>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: '1rem' }}>
                {hotelSection.trim()}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                <a 
                  href={`https://www.booking.com/searchresults.html?ss=${encodeURIComponent(destination || 'Tokyo')}`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ textDecoration: 'none' }}
                >
                  <Button size="sm" variant="secondary" icon={ExternalLink}>
                    Open on Booking.com
                  </Button>
                </a>
                <a 
                  href={`https://www.agoda.com/search?city=${encodeURIComponent(destination || 'Tokyo')}`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ textDecoration: 'none' }}
                >
                  <Button size="sm" variant="secondary" icon={ExternalLink}>
                    Open on Agoda
                  </Button>
                </a>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Car Rental Card (if applicable) */}
        {(selfDrive || carSection) && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <GlassCard style={{ borderLeft: '4px solid var(--accent-green)' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--accent-green)' }}>
                <Car size={20} /> Self-Drive Car Rental & Toll Logistics
              </h3>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: '1rem' }}>
                {carSection ? carSection.trim() : `Self-drive vehicle booking recommended with ETC toll card.`}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                <a 
                  href="https://www.rentalcars.com/" 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ textDecoration: 'none' }}
                >
                  <Button size="sm" variant="secondary" icon={ExternalLink}>
                    Compare on Rentalcars.com
                  </Button>
                </a>
                <a 
                  href="https://www.tabirai.net/car/japan/" 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ textDecoration: 'none' }}
                >
                  <Button size="sm" variant="secondary" icon={ExternalLink}>
                    Tabirai Car Rental
                  </Button>
                </a>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Attraction Tickets & Passes */}
        {ticketSection && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <GlassCard style={{ borderLeft: '4px solid var(--accent-orange)' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--accent-orange)' }}>
                <Ticket size={20} /> Attraction Tickets & Sights Bookings
              </h3>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem', color: 'var(--text-primary)', marginBottom: '1rem' }}>
                {ticketSection.trim()}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                <a 
                  href={`https://www.klook.com/en-SG/search/?query=${encodeURIComponent(destination || 'Tokyo')}`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ textDecoration: 'none' }}
                >
                  <Button size="sm" variant="secondary" icon={ExternalLink}>
                    Klook Pass Bookings
                  </Button>
                </a>
                <a 
                  href={`https://www.getyourguide.com/s/?q=${encodeURIComponent(destination || 'Tokyo')}`} 
                  target="_blank" 
                  rel="noreferrer"
                  style={{ textDecoration: 'none' }}
                >
                  <Button size="sm" variant="secondary" icon={ExternalLink}>
                    GetYourGuide Tickets
                  </Button>
                </a>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </div>

      {/* Full Dossier */}
      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
          Complete Purchasing Agent Dossier
        </h3>
        <div className="glass-card" style={{ padding: '1.5rem', whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
          {purchasingText}
        </div>
      </div>
    </div>
  );
}
