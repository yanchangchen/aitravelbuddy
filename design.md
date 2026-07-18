# Travel Buddy — User-Centric UI/UX Design Specifications

## 🎯 1. Design Vision & Philosophy
Travel Buddy is designed to make complex, multi-agent travel planning effortless, visual, and delightfully interactive. The user interface prioritizes **Clarity, Visual Excellence, and Progressive Disclosure**—ensuring first-time users can generate a customized 5-day travel plan in under 10 seconds while giving power users granular control over personas, group sizes, self-drive preferences, and custom budgets.

---

## 🎨 2. Design System & Style Tokens

### 2.1 Color Palette (Clean Light Mode)
- **Primary Accent:** `#FF6B6B` (Coral Red — Call to Action & Headers)
- **Secondary Accent:** `#FF8E53` (Warm Amber — Sub-headers & Icons)
- **Tertiary Accent:** `#FFC857` (Golden Glow — Dividers & Badges)
- **Background Primary:** `#FFFFFF` (Pure White Canvas)
- **Background Secondary:** `#F8FAFC` (Slate Tint — Sidebar & Structural Containers)
- **Surface Cards:** `#FFFFFF` with `#E2E8F0` borders and subtle box-shadow (`0 4px 6px -1px rgba(0, 0, 0, 0.05)`)
- **Text Primary:** `#0F172A` (Slate 900 — High contrast readability)
- **Text Secondary:** `#475569` (Slate 600 — Captions & Helper Labels)
- **Status Badges:**
  - Approved / Success: Emerald Green (`#10B981` to `#34D399`)
  - Warning / Retrying: Amber Yellow (`#F59E0B`)
  - Error / Budget Busted: Rose Red (`#EF4444` to `#F87171`)

### 2.2 Typography
- **Primary Font Family:** Inter, sans-serif (Google Fonts)
- **Header 1 (App Title):** 2.8rem (700 bold), gradient text fill
- **Header 2 (Section Titles):** 1.4rem (600 semi-bold), `#0F172A`
- **Header 3 (Card Titles):** 1.1rem (600 semi-bold), `#FF6B6B`
- **Body Text:** 1.0rem (400 regular), 1.6 line-height

---

## 📐 3. Information Architecture & Layout Structure

```
+-----------------------------------------------------------------------------------+
| 🌍 Travel Buddy — AI Multi-Agent Travel Planner                                  |
+------------------------------------+----------------------------------------------+
| SIDEBAR (Trip Controls)            | MAIN WORKSPACE                               |
| 💾 Saved Trips (Supabase)          | 🔄 Agent Pipeline Live Progress Status       |
| 👥 Group Composition (Adults/Kids) | -------------------------------------------- |
| ✈️ Origin & Destination            | CONSOLIDATED TABBED RESULTS:                 |
| 🚗 Self-Drive Option Checkbox      |  [🗺️ Trip Plan & Map] [🏨 Hotels & Dining]   |
| 💰 Infinite Budget / SGD Input     |  [🛒 Flights & Budget] [💬 Travel Assistant] |
| 📅 Travel Dates (Default 5 Days)   |  [⚙️ Under the Hood]                         |
| 🎭 Persona Selector + Custom Maker | -------------------------------------------- |
| ---------------------------------- | 💾 Save Trip to Supabase                     |
| 🚀 [Plan My Trip] Primary Button   | 📥 Download CSV / Text Report                |
+------------------------------------+----------------------------------------------+
```

### 3.1 Progressive Disclosure Pattern
- **Step 1 (Setup):** Sidebar logically groups demographic and travel inputs. Technical API keys have been removed from the UI entirely to maintain a premium consumer feel.
- **Step 2 (Execution Feedback):** Live progress bar with animated status text showing node transitions in real time.
- **Step 3 (Multimodal Results):** Consolidating 10 legacy tabs into 5 logical categories prevents cognitive overload while providing deep context (e.g., Maps and Text Itineraries live together).
- **Step 4 (Persistence):** Users can save generated trips to Supabase and retrieve them later directly from the sidebar.

---

## 🗺️ 4. Interactive UX Components

1. **Consolidated Map & Itinerary (`🗺️ Trip Plan & Map`):**
   - **Pydeck 3D Scatterplot:** Interactive 3D pins for ALL day-by-day itinerary venues with day-coded tooltips.
   - **OpenStreetMap Embed:** Guaranteed fallback iframe working across all browsers.
   - **Text Itinerary:** Markdown display of the detailed day-by-day sightseeing plan seamlessly scrolling alongside the map.

2. **Purchasing & Budget Hub (`🛒 Flights & Budget`):**
   - Direct, clickable HTTPS links for round-trip flights, car rentals, and attraction tickets curated by the specialized Purchasing Agent.
   - Live budget breakdown tables showing allocation across categories.

3. **Micro-interactions:**
   - **Hover States:** Feature `.result-card` containers gently transform upward and cast a soft drop-shadow when hovered over, providing a responsive and modern tactile feel.

4. **Conversational Assistant (`💬 Travel Assistant`):**
   - Built-in chat interface for asking destination advice, packing tips, or local customs recommendations.

---

## 🔮 5. Future UX Enhancements Roadmap
- **Drag-and-Drop Itinerary Builder:** Allow users to reorder daily activities.
- **Interactive Budget Slider & Live Currency Converter:** Real-time conversion between SGD, USD, EUR, JPY, and GBP.
- **Mobile PWA Support:** Offline caching for mobile travelers on the go.
