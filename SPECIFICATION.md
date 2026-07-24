# 📄 Travel Buddy — System Specification & Technical Reference

This document provides the complete, authoritative functional and technical specification for **Travel Buddy**, an AI-powered multi-agent travel planning platform.

---

## 1. System Overview & Core Objectives

**Travel Buddy** is designed to generate customized, persona-aligned, budget-audited, multi-day travel itineraries. The system orchestrates four specialized domain agents using a **LangGraph state machine**, validates persona compliance with an **Agent-as-Judge LLM evaluator**, and provides a Streamlit web application.

### Key Capabilities
1. **4 Collaborative Agents**: Sightseeing, Food & Retail, Hospitality, and Purchasing/Logistics.
2. **Flexible & Unlimited Budget Modes**: Supports strict SGD budget auditing or flexible/unlimited luxury modes.
3. **Group Composition & Self-Drive Options**: Supports customizable Adult, Child, and Infant counts, plus optional car rental and fuel/toll calculations.
4. **Persona Studio & User Preferences Persistence**: Saves custom persona profiles, dietary restrictions, accommodation styles, travel pace, and top interests to `user_profile.json`.
5. **Guided Plan With Me Chatbot**: Interactive AI concierge assistant for undecided travelers to clarify trip criteria.
6. **"Surprise Me!" Seasonal Pick Engine**: 1-click recommendation generator for trending seasonal destinations.
7. **Unapproved Plan Display & Criteria Relaxation**: Preserves plan artifacts even if quality evaluation fails, displaying explicit failure reasons and quick controls to relax criteria and rerun.
8. **Universal State Persistence & Export/Import**: Saves trip details and full agent execution states to cloud/local storage, with 1-click `.json` export and import capabilities.
9. **Interactive Location Mapping**: Geocodes all itinerary venues and plots scatter pins on Pydeck & OpenStreetMap.
10. **Real-Time Logging & Diagnostics**: Logs agent outputs and provides live diagnostic consoles and error stack trace displays.

---

## 2. Technical Architecture & Component Specifications

```mermaid
graph TD
    Client[🖥️ Streamlit Web App (ui/)] -->|User Specs & State| App[app.py Router]
    App -->|Initial State| StateGraph[🔄 LangGraph State Machine (core/graph.py)]

    subgraph "Agents Execution Phase"
        StateGraph --> Itin[🗺️ Itinerary Agent (core/agents.py)]
        Itin --> Food[🍽️ Food & Retail Agent (core/agents.py)]
        Food --> Hosp[🏨 Hospitality Agent (core/agents.py)]
        Hosp --> Purch[🛒 Purchasing Agent (core/agents.py)]
    end

    subgraph "Guardrail & Judge Phase"
        Purch --> Guard[💰 Budget Guardrail (core/evaluation.py)]
        Guard -->|Over Budget & Retries < 3| Itin
        Guard -->|Within Budget / Unlimited| Judge[⚖️ Agent-as-Judge (core/evaluation.py)]
        Judge -->|Pass Score >= 6| Appr[✅ Final Output]
        Judge -->|Fail Score < 6 & Retries >= 3| Fallback[🚨 Terminal Fallback]
    end

    Appr --> App
    Fallback --> App
    App --> DB[(💾 Storage Layer - core/db.py)]
```

---

## 3. Data Schema & State Management

### 3.1 Central State Schema (`TravelBuddyState` in `core/state.py`)

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `origin` | `str` | Source city (e.g. `"Singapore"`) |
| `destination` | `str` | Destination city/country (e.g. `"Tokyo, Japan"`) |
| `budget` | `float` | Target budget in SGD |
| `num_adults` | `int` | Number of adult travelers |
| `num_children` | `int` | Number of child travelers (>2 yrs) |
| `num_infants` | `int` | Number of infant travelers (<2 yrs) |
| `travelers_summary` | `str` | Summary string (e.g. `"2 Adults, 1 Child"`) |
| `self_drive` | `bool` | Self-drive rental toggle |
| `no_budget` | `bool` | Unlimited budget toggle |
| `currency` | `str` | Target currency (default `"SGD"`) |
| `dates` | `str` | Travel dates string (e.g. `"Nov 15 - Nov 20, 2026"`) |
| `num_days` | `int` | Total trip length in days |
| `persona` | `str` | Active persona key (`"single"`, `"couple"`, `"family"`, `"custom"`) |
| `custom_persona_profile` | `dict` | Custom persona rules & pacing |
| `user_preferences` | `dict` | User dietary, accommodation, pace, and interest preferences |
| `itinerary` | `str` | Sightseeing itinerary markdown |
| `food_and_retail` | `str` | Dining & shopping markdown |
| `hotel_recommendations` | `str` | Accommodation markdown |
| `purchasing_guide` | `str` | Flight & transport booking guide |
| `budget_breakdown` | `str` | Cost audit summary |
| `judge_verdict` | `str` | Agent-as-Judge compliance report |
| `status` | `str` | Plan status (`"approved"`, `"unapproved"`, `"planning"`) |
| `quality_failure_reason` | `str` | Quality evaluation failure explanation |
| `session_logs` | `str` | Execution logs buffer |

---

## 4. UI Package Specification (`ui/`)

- **`ui/styles.py`**: Injects light-mode CSS variables, Inter fonts, gradient headers, card containers, and status badges.
- **`ui/sidebar.py`**: Renders setup controls, traveler count selectors, date range pickers, persona radio buttons, and the **"Saved Persona & Preferences Settings"** panel.
- **`ui/landing.py`**: Manages the landing page view containing:
  - **"💬 Guided Plan With Me"**: Conversational AI assistant for undecided travelers.
  - **"🎲 Surprise Me!"**: Trending seasonal destination cards.
  - **"✨ Key Features"**: Architecture cards.
- **`ui/plan_view.py`**: Renders complete trip results:
  - **Primary Action Bar**: `💾 Save Trip & Agent State`, `📥 Export Agent State (.json)`, `📊 Export Excel (.xlsx)`.
  - **5 Plan Tabs**:
    1. 🗺️ *Trip Plan & Map*: Markdown itinerary, Pydeck scatter chart, OpenStreetMap iframe, day-by-day table.
    2. 🏨 *Hotels & Dining*: Accommodation and dining recommendations.
    3. 🛒 *Flights & Budget*: Flight deals, transport guide, SGD cost breakdown, currency converter.
    4. 💬 *Travel Assistant*: Q&A chat assistant and plan iteration form.
    5. ⚙️ *Under the Hood*: Agent-as-Judge report, live debug logs console, report download.

---

## 5. Storage & Persistence Specifications

1. **User Profile Persistence (`core/profile.py`)**:
   - Saves/loads `user_profile.json` in the workspace root.
   - Preserves custom persona definitions and preference tags across sessions.

2. **Trip & Agent Run State Persistence (`core/db.py`)**:
   - Saves trip plans to Supabase PostgreSQL database if `SUPABASE_URL` and `SUPABASE_KEY` are provided.
   - Falls back to `.saved_trips.json` if Supabase credentials are not configured.
   - Stores full state dictionary for both approved and unapproved plans.

3. **JSON State Export & Import**:
   - Allows users to export `agent_run_state_*.json` from the action bar.
   - Allows users to import any `agent_run_state.json` via the sidebar file uploader.

---

## 6. Testing & Quality Assurance Specifications

- Test Suite Directory: `tests/`
- Test Framework: Python `unittest`
- Test Coverage:
  - `test_db.py`: Database storage and local `.saved_trips.json` fallback.
  - `test_evaluation.py`: Terminal fallback preservation and quality failure reasons.
  - `test_graph.py`: StateGraph compilation and node routing.
  - `test_guardrail.py`: Budget guardrail logic and retry counter limits.
  - `test_profile.py`: `user_profile.json` loading, saving, and context injection.
  - `test_surprise.py`: Seasonal pick generator across all 4 seasons.
  - `test_utils.py`: Location extraction, geocoding, and report generation.

To run the complete automated test suite:
```powershell
python -m unittest discover -s tests
```
