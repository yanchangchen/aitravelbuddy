import React from 'react';
import { useTripStore } from '../stores/tripStore';
import LeftDrawer from '../components/LeftDrawer/LeftDrawer';
import CenterCanvas from '../components/CenterCanvas/CenterCanvas';
import RightPanel from '../components/RightPanel/RightPanel';
import { Button } from '../components/shared';
import { Save, Download, ArrowLeft, Menu, PanelRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DeskPage() {
  const navigate = useNavigate();
  const { leftDrawerOpen, rightPanelOpen, toggleLeftDrawer, toggleRightPanel, destination } = useTripStore();
  
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
          <Button variant="secondary" icon={Save}>Save</Button>
          <Button variant="secondary" icon={Download}>Export</Button>
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
