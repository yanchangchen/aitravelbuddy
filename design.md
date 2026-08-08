# Travel Buddy — User-Centric UI/UX Design Specifications

## 🎯 1. Design Vision & Philosophy
Travel Buddy makes multi-agent travel planning visual, intuitive, and responsive. It features a modern design system across both its **React / Vite Single Page App (Vercel)** and its **Streamlit Studio**:
- **Clean Light Aesthetics:** `#FFFFFF` background, slate `#F8FAFC` sidebars, `#0F172A` high-contrast typography, and `#FF6B6B` coral accents.
- **Progressive Disclosure:** Simple one-click planning with deep controls for travelers, personas, budgets, and self-drive options.
- **Honest Connection Signals:** A real-time traffic light indicator (🟠 blinking wake-up, 🟢 ready, 🔴 offline) keeps users informed of backend status.

---

## 🎨 2. Design System & Style Tokens

### 2.1 Color Palette
- **Primary Accent:** `#FF6B6B` (Coral Red — Primary actions, active days, highlights)
- **Secondary Accent:** `#38BDF8` (Sky Blue — Flights, booking portals, hotels)
- **Tertiary Accent:** `#F59E0B` (Amber Orange — Dining, ratings, warnings)
- **Success Tone:** `#10B981` (Emerald Green — Car rentals, approved quality scores)
- **Canvas Background:** `#FFFFFF` (Light Mode Canvas) / `#0F172A` (Glass Container Dark Trim)
- **Sidebar & Surface:** `#F8FAFC` with subtle glassmorphic borders (`#E2E8F0`)

### 2.2 Typography
- **Primary Font:** Inter / Roboto, sans-serif
- **Headers:** High-contrast `#0F172A` with gradient accents
- **Body & Metrics:** 1.0rem regular, 1.6 line height

---

## 📐 3. React Frontend Workspaces (Vercel)

### 3.1 Landing Page (`LandingPage.jsx`)
- **Real-World Seasonal Fresh Picks:** 6 global continent packages auto-refreshed via Gemini AI with continent tags, durations, vibes, and single-click planning.
- **Dynamic Date Framing:** Auto-calculates start and end dates 2 weeks out for the exact package duration (5–6 days).
- **Backend Readiness Alert:** Traffic light badge ensures users never trigger planning before the backend server is active.

### 3.2 Planning Studio (`DeskPage.jsx`)
- **Center Canvas Tabs:**
  1. **Timeline:** Day-by-day sightseeing schedule with deduplication, activity icons, cost tags, and time blocks.
  2. **Map:** Interactive Google Maps Itinerary Explorer plotting all attractions, hotels, and restaurants with day filter pills (`All`, `Day 1..N`, `Hotels`, `Dining`) and direct Directions links.
  3. **Hotels:** Curated accommodation cards featuring star ratings (`⭐⭐⭐⭐`), neighborhood location, amenity tags, nightly rates, and estimated total stay in SGD (S$).
  4. **Bookings:** Round-trip flight search (Skyscanner, Google Flights), accommodation portals (Booking.com, Agoda), car rentals, and attraction ticket booking buttons.
  5. **Split View:** Side-by-side synchronized view of the Timeline and Google Maps.
- **Right Panel:** Interactive AI Concierge Chat with plan extraction and live agent node monitor.

---

## 🗺️ 4. Streamlit Studio Workspaces (`app.py`)
- **Full-Width Google Maps Explorer:** Seamlessly embedded Google Maps search and navigation for the chosen destination.
- **Day-by-Day Tabular Export:** Live table preview with one-click Excel (`.xlsx`) download.
- **Live Currency Converter:** Real-time SGD conversion across USD, EUR, JPY, GBP, and AUD.
