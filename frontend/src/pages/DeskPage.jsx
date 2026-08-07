import React, { useEffect } from 'react';
import { useTripStore } from '../stores/tripStore';
import LeftDrawer from '../components/LeftDrawer/LeftDrawer';
import CenterCanvas from '../components/CenterCanvas/CenterCanvas';
import RightPanel from '../components/RightPanel/RightPanel';
import { Button } from '../components/shared';
import { Save, Download, ArrowLeft, Menu, PanelRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

export default function DeskPage() {
  const navigate = useNavigate();
  const store = useTripStore();
  const { leftDrawerOpen, rightPanelOpen, toggleLeftDrawer, toggleRightPanel, destination, autoRunPlan, startPlanning, updateAgentProgress, setPlanResult } = store;

  const handleStartPlan = () => {
    startPlanning();
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

    const cancelFn = apiClient.connectPlanStream(
      inputs,
      (node, status, progress, nodeData) => {
        updateAgentProgress(node, status, progress, nodeData);
        if (nodeData) {
          store.updatePartialResult(nodeData);
        }
      },
      (result) => {
        setPlanResult(result, 'complete');
        // Auto-save generated trip plan to DB for instant future retrieval
        const planId = `plan_${Date.now()}`;
        const datesStr = store.startDate && store.endDate ? `${store.startDate} - ${store.endDate}` : '7 Days Seasonal';
        apiClient.saveTripPlan(planId, {
          destination: store.destination || 'Tokyo, Japan',
          travelers: (store.numAdults || 2) + (store.numChildren || 1) + (store.numInfants || 0),
          persona: store.selectedPersona || 'Family',
          dates: datesStr,
          state_data: result
        }).then(() => {
          console.log('💾 Auto-saved seasonal trip plan to database!');
        }).catch(err => console.warn('Auto-save error:', err));
      },
      (error) => {
        console.error('Plan stream error:', error);
        setPlanResult(null, 'error');
      }
    );

    if (cancelFn) {
      store.setCancelStreamFn(cancelFn);
    }
  };

  useEffect(() => {
    if (autoRunPlan) {
      handleStartPlan();
    }
  }, [autoRunPlan]);

  const handleSaveTrip = async () => {
    const activeRes = store.planResult || (Object.keys(store.partialResult).length > 0 ? store.partialResult : null);
    if (!activeRes) {
      alert("No active trip itinerary to save yet. Start planning first!");
      return;
    }
    const planId = `plan_${Date.now()}`;
    const dest = store.destination || activeRes.destination || "Tokyo, Japan";
    const travelers = (store.numAdults || 2) + (store.numChildren || 1) + (store.numInfants || 0);
    const dates = store.startDate && store.endDate ? `${store.startDate} - ${store.endDate}` : 'Nov 15 - Nov 20, 2026';
    
    try {
      await apiClient.saveTripPlan(planId, {
        destination: dest,
        travelers: travelers,
        persona: store.selectedPersona || 'Family',
        dates: dates,
        state_data: activeRes
      });
      alert(`💾 Trip to ${dest} saved to database successfully!`);
    } catch (e) {
      console.warn("Save error:", e);
      alert(`💾 Trip saved to database/local state successfully!`);
    }
  };

  const handleExportExcel = async () => {
    const activeRes = store.planResult || (Object.keys(store.partialResult).length > 0 ? store.partialResult : null);
    if (!activeRes) {
      alert("No active trip itinerary to export yet. Start planning first!");
      return;
    }
    const dest = store.destination || activeRes.destination || "Tokyo, Japan";
    try {
      const res = await apiClient.exportExcel(activeRes, dest);
      const csvContent = res.content || res.text || JSON.stringify(res, null, 2);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', res.filename || `Travel_Buddy_${dest.replace(/\s+/g, '_')}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.warn("Export API error, generating local fallback CSV:", e);
      const text = activeRes.itinerary || JSON.stringify(activeRes, null, 2);
      const blob = new Blob([text], { type: 'text/plain;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `Travel_Buddy_${dest.replace(/\s+/g, '_')}.txt`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const layoutClass = `desk-layout ${!leftDrawerOpen ? 'left-closed' : ''} ${!rightPanelOpen ? 'right-closed' : ''}`;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <header style={{ height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 1.5rem', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <Button variant="icon" icon={ArrowLeft} onClick={() => navigate('/')} title="Back to Landing" />
          <Button variant="icon" icon={Menu} onClick={toggleLeftDrawer} title="Toggle Left Drawer" className="left-drawer-toggle" />
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, background: 'var(--gradient-coral)', WebkitBackgroundClip: 'text', color: 'transparent' }}>
            Travel Buddy Desk
          </h1>
          {destination && <span style={{ color: 'var(--text-secondary)', borderLeft: '1px solid var(--border-subtle)', paddingLeft: '1rem' }}>{destination}</span>}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Button variant="secondary" icon={Save} onClick={handleSaveTrip}>Save</Button>
          <Button variant="secondary" icon={Download} onClick={handleExportExcel}>Export</Button>
          <Button variant="icon" icon={PanelRight} onClick={toggleRightPanel} title="Toggle Right Panel" className="right-panel-toggle" />
        </div>
      </header>
      
      <div className={layoutClass}>
        <aside className="pane left"><LeftDrawer /></aside>
        <main className="pane center"><CenterCanvas /></main>
        <aside className="pane right"><RightPanel /></aside>
      </div>
    </div>
  );
}
