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
| 🔐 API Credentials                 | 🔄 Agent Pipeline Live Progress Status       |
| 👥 Group Composition (Adults/Kids) | -------------------------------------------- |
| ✈️ Origin & Destination            | TABBED RESULTS DISPLAY:                      |
| 🚗 Self-Drive Option Checkbox      |  [🗺️ Itinerary] [🛒 Booking Links]            |
| 💰 Infinite Budget / SGD Input     |  [📍 Location Map] [📊 Tabular Itinerary]     |
| 📅 Travel Dates (Default 5 Days)   |  [🍽️ Food & Retail] [🏨 Accommodation]       |
| 🎭 Persona Selector + Custom Maker |  [💰 Budget] [⚖️ Quality] [💬 Q&A Chat]      |
| ---------------------------------- | -------------------------------------------- |
| 🚀 [Plan My Trip] Primary Button   | 📥 Download CSV / Text Report / Debug Logs   |
+------------------------------------+----------------------------------------------+
```

### 3.1 Progressive Disclosure Pattern
- **Step 1 (Setup):** Sidebar groups inputs logically (API Keys -> Group Composition -> Destination & Dates -> Persona).
- **Step 2 (Execution Feedback):** Live progress bar with animated status text showing node transitions in real time.
- **Step 3 (Multimodal Results):** Organized tabs prevent cognitive overload by separating Itineraries, Maps, Booking Links, Data Tables, and Chat.

---

## 🗺️ 4. Interactive UX Components

1. **Multi-Layer Location Maps (`📍 Location Map`):**
   - **Pydeck 3D Scatterplot:** Interactive 3D pins for ALL day-by-day itinerary venues with day-coded tooltips.
   - **OpenStreetMap Embed:** Guaranteed fallback iframe working across all browsers without API keys.
   - **Google Maps Integration:** Direct navigation buttons for Google Maps & OpenStreetMap.

2. **Purchasing & Booking Hub (`🛒 Booking Links`):**
   - Direct, clickable HTTPS links for round-trip flights (from origin city), hotels, car rentals, and attraction tickets curated by the specialized Purchasing Agent.

3. **Tabular Data Export (`📊 Tabular Itinerary`):**
   - Clean Pandas DataFrame displaying Day, Theme, Time Slot, Activity Details, and Estimated Costs (SGD).
   - One-click **Download CSV** button for spreadsheet integration.

4. **Conversational Assistant (`💬 Travel Q&A Chat`):**
   - Built-in chat interface for asking destination advice, packing tips, or local customs recommendations.

---

## 🔮 5. Future UX Enhancements Roadmap
- **Drag-and-Drop Itinerary Builder:** Allow users to reorder daily activities.
- **Interactive Budget Slider & Live Currency Converter:** Real-time conversion between SGD, USD, EUR, JPY, and GBP.
- **Mobile PWA Support:** Offline caching for mobile travelers on the go.
