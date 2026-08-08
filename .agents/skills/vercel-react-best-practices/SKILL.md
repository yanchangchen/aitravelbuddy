---
name: vercel-react-best-practices
description: Production-grade engineering, performance, architecture, resilience, and UI/UX best practices for React applications deployed on Vercel. Use when building, auditing, optimizing, or debugging React/Vite frontends, Vercel deployments, WebSocket/REST API communication, client state management, or Web Vitals.
version: 1.0.0
---

# Vercel & React Production Best Practices

This skill provides comprehensive architectural, performance, resilience, and design guidelines for developing and maintaining React applications deployed on the Vercel platform.

---

## 1. 🚀 Vercel Deployment & SPA Routing Architecture

### A. SPA Client Routing Configuration (`vercel.json`)
Single Page Applications (SPAs) built with React Router, Vite, or Create React App require fallback rewrite rules so deep URLs do not return `404 Not Found`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ]
}
```

### B. Environment Variable Management
- **Client-Accessible Variables:** Prefix with `VITE_` (for Vite) or `NEXT_PUBLIC_` (for Next.js).
- **Environment Isolation:** Do NOT bake sensitive secrets (LLM keys, private database connection strings) into frontend bundles.
- **Dynamic API Fallbacks:** Always configure dynamic host resolution:
  ```javascript
  export const API_BASE = import.meta.env.VITE_API_URL || (
    typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')
      ? 'https://your-backend.onrender.com'
      : 'http://localhost:8000'
  );
  ```

---

## 2. ⚡ Core Web Vitals & React Performance

### A. Largest Contentful Paint (LCP) & Asset Loading
- **Image Optimization:** Always specify explicit `width` and `height` (or aspect-ratio) to prevent layout shifts (CLS).
- **Preload Critical Assets:** Preconnect and preload critical Google Fonts or Hero imagery:
  ```html
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  ```
- **Code Splitting & Lazy Loading:** Lazy load heavy non-critical route chunks:
  ```javascript
  import React, { Suspense, lazy } from 'react';
  const HeavyMap = lazy(() => import('./components/CenterCanvas/MapView'));
  ```

### B. Interaction to Next Paint (INP) & State Management
- **Lightweight Stores (Zustand):** Prefer atomic state selectors over monolithic re-renders:
  ```javascript
  // Recommended: Select only required slice
  const planStatus = useTripStore((state) => state.planStatus);
  ```
- **Debounced Input & Transitions:** Wrap rapid filter or search updates in `useDeferredValue` or `startTransition` to keep the main thread responsive.

---

## 3. 🛡️ Network Resilience & Stream Fallbacks

### A. WebSocket & Long-Running Request Handlers
- **Cold-Start Resilience:** Long-running backend services on free tiers (like Render) require generous connection timeout allowances (e.g. 25–30s) to warm up before declaring connection failures.
- **Strict Cleanup in `useEffect`:** Always provide teardown logic to prevent ghost listeners:
  ```javascript
  useEffect(() => {
    const cancelFn = apiClient.connectPlanStream(...);
    return () => {
      if (cancelFn) cancelFn();
    };
  }, []);
  ```
- **Backend Readiness Checks:** Ping the health endpoint `/api/health` at app startup, rendering traffic light indicators (🟠 waking up, 🟢 active, 🔴 offline) and disabling action buttons until the server is ready.
- **No Deceptive Stubs:** Forward network and pipeline errors honestly to UI error handlers instead of returning fabricated placeholder itineraries.

---

## 4. 🎨 Visual Hierarchy & Design Guardrails

- **Curated Color Tokens:** Never use raw default colors (plain `#FF0000`, `#0000FF`). Use harmonious HSL/Hex tokens (`--bg-primary: #0F172A`, `--accent-coral: #FF6B6B`, `--accent-blue: #38BDF8`).
- **Smooth Feedback & Micro-Interactions:** Provide loading spinners, pulsing skeleton loaders, and Framer Motion transitions (`whileHover={{ y: -4 }}`) for responsive feedback.
- **Keyboard Navigation & Accessibility (a11y):** Ensure all interactive elements have semantic HTML tags (`<button>`, `<input>`), explicit `aria-label`s, and high-contrast text ratios ($\ge 4.5:1$).

---

## 5. ✅ Production Quality Checklist

1. [ ] `vercel.json` exists with single-page app rewrite directives.
2. [ ] No hardcoded local URLs (`localhost:8000`) without environment fallbacks.
3. [ ] All React hook dependencies are declared properly without infinite-loop triggers.
4. [ ] Build checks pass with zero fatal lint or type errors (`npm run build`).
5. [ ] Network pings and WebSockets handle disconnects, wake-up delays, and cleanup gracefully.
