import React from 'react';
import { motion } from 'framer-motion';

export const Button = ({ variant = 'primary', size = 'md', icon: Icon, children, loading, disabled, onClick, className = '' }) => {
  const baseClass = `btn btn-${variant} ${className}`;
  return (
    <motion.button
      whileHover={disabled ? {} : { scale: 1.02 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      className={baseClass}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? <span className="spinner">⏳</span> : Icon && <Icon size={18} />}
      {children}
    </motion.button>
  );
};

export const Input = ({ label, icon: Icon, error, ...props }) => (
  <div style={{ marginBottom: '1rem', width: '100%' }}>
    {label && <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{label}</label>}
    <div style={{ position: 'relative' }}>
      {Icon && <Icon size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />}
      <input className="input-field" style={{ paddingLeft: Icon ? '2.5rem' : '1rem' }} {...props} />
    </div>
    {error && <span style={{ color: 'var(--accent-coral)', fontSize: '0.75rem', marginTop: '0.25rem' }}>{error}</span>}
  </div>
);

export const Select = ({ label, options = [], ...props }) => (
  <div style={{ marginBottom: '1rem', width: '100%' }}>
    {label && <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{label}</label>}
    <select className="input-field" {...props}>
      {options.map((opt, i) => (
        <option key={i} value={opt.value || opt}>{opt.label || opt}</option>
      ))}
    </select>
  </div>
);

export const Card = ({ children, className = '' }) => (
  <div className={`glass-card ${className}`}>
    {children}
  </div>
);

export const GlassCard = Card;

export const Badge = ({ variant = 'pending', children }) => (
  <span className={`badge ${variant}`}>{children}</span>
);

export const Skeleton = ({ width = '100%', height = '1rem', variant = 'text', style = {} }) => (
  <div className="skeleton" style={{ width, height, borderRadius: variant === 'circle' ? '50%' : 'var(--radius-sm)', ...style }}></div>
);

import { animate } from 'framer-motion';

export const AnimatedNumber = ({ value }) => {
  const nodeRef = React.useRef(null);
  React.useEffect(() => {
    const node = nodeRef.current;
    if (node) {
      const controls = animate(0, value, {
        duration: 1,
        onUpdate(v) {
          node.textContent = v.toFixed(0);
        }
      });
      return () => controls.stop();
    }
  }, [value]);
  return <span ref={nodeRef}>{value}</span>;
};

export const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;
  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }} className="glass-card" style={{ width: '100%', maxWidth: '500px', position: 'relative' }}>
        <button className="btn-icon" onClick={onClose} style={{ position: 'absolute', top: '1rem', right: '1rem' }}>✕</button>
        {children}
      </motion.div>
    </div>
  );
};
