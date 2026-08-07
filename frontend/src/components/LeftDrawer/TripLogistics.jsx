import React from 'react';
import { useTripStore } from '../../stores/tripStore';
import { Input, Select } from '../shared';
import { MapPin, Calendar as CalIcon } from 'lucide-react';

export default function TripLogistics() {
  const { origin, destination, startDate, endDate, numAdults, numChildren, numInfants, selfDrive, noBudget, budget, currency, setLogistics } = useTripStore();

  return (
    <div style={{ padding: '1rem' }}>
      <Input label="Origin City" icon={MapPin} placeholder="e.g. New York" value={origin} onChange={(e) => setLogistics({ origin: e.target.value })} />
      <Input label="Destination City" icon={MapPin} placeholder="e.g. Tokyo" value={destination} onChange={(e) => setLogistics({ destination: e.target.value })} />
      
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <Input type="date" label="Start Date" value={startDate} onChange={(e) => setLogistics({ startDate: e.target.value })} />
        <Input type="date" label="End Date" value={endDate} onChange={(e) => setLogistics({ endDate: e.target.value })} />
      </div>

      <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Travelers</label>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <Input type="number" label="Adults" min="1" value={numAdults} onChange={(e) => setLogistics({ numAdults: parseInt(e.target.value) || 1 })} />
        <Input type="number" label="Children" min="0" value={numChildren} onChange={(e) => setLogistics({ numChildren: parseInt(e.target.value) || 0 })} />
        <Input type="number" label="Infants" min="0" value={numInfants} onChange={(e) => setLogistics({ numInfants: parseInt(e.target.value) || 0 })} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
        <input type="checkbox" id="selfDrive" checked={selfDrive} onChange={(e) => setLogistics({ selfDrive: e.target.checked })} />
        <label htmlFor="selfDrive" style={{ fontSize: '0.875rem' }}>Self-drive (Rent a car)</label>
      </div>

      <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Budget</label>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <input type="checkbox" id="noBudget" checked={noBudget} onChange={(e) => setLogistics({ noBudget: e.target.checked })} />
        <label htmlFor="noBudget" style={{ fontSize: '0.875rem' }}>No Budget Limit</label>
      </div>
      
      {!noBudget && (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <div style={{ flex: 1 }}><Input type="number" value={budget} onChange={(e) => setLogistics({ budget: parseInt(e.target.value) || 0 })} /></div>
          <div style={{ width: '90px' }}><Select options={['SGD', 'USD', 'EUR', 'JPY', 'GBP']} value={currency} onChange={(e) => setLogistics({ currency: e.target.value })} /></div>
        </div>
      )}
    </div>
  );
}
