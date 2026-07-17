# 🌍 Travel Buddy — AI Multi-Agent Travel Planner

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Travel Buddy** is a production-grade, multi-agent travel planning web application built with **Streamlit**, **LangGraph**, and **Google Gemini** (`gemini-3.1-flash-lite`). It coordinates three specialized AI agents to generate personalized, real-world grounded travel itineraries, dining recommendations, and hotel options while maintaining budget safety buffers in **Singapore Dollars (SGD / S$)** and quality standards.

---

## 🌟 Key Features

- 🔑 **Streamlit Secrets Integration:** Automatically reads `GOOGLE_API_KEY`, `TAVILY_API_KEY`, and optional `GOOGLE_MAPS_API_KEY` directly from `st.secrets`.
- 🇸🇬 **Default SGD Currency (S$):** Calculates all itinerary, dining, and hotel costs in Singapore Dollars, with internal USD reference conversion.
- ♾️ **Flexible / No-Budget Option:** Toggle infinite / flexible budget mode to plan without upper cost limits.
- 📍 **Google Maps Location Visualizer:** Embedded interactive Google Maps for destination attractions and quick direction links.
- 📊 **Tabular Itinerary & CSV Export:** Displays itineraries as structured data tables and enables one-click **CSV** and **Full Text (.txt)** downloads.
- 🤖 **Multi-Agent Collaboration:** Sequential generation pipeline with specialized agents for Sightseeing, Food & Retail, and Hospitality.
- 🌐 **Real-Time Web Grounding:** Uses the Tavily Search API to retrieve live attraction details, restaurant recommendations, and current hotel pricing.
- 💰 **Deterministic Budget Guardrail:** Hard-coded Python cost parsing ensuring total estimated trip cost lands strictly within **80%–90%** of the target budget with a 3-strike retry loop.
- ⚖️ **Cognitive Agent-as-Judge:** Automated quality evaluation inspecting outputs against persona-specific mandatory constraints.
- 🎭 **Demographic Personas:** Custom rules and pacing for **Solo Travelers**, **Couple's Getaways**, and **Family Adventures**.

---

## 🏗️ Architecture & Graph Flow

```mermaid
graph TD
    START([START]) --> itinerary[🗺️ Itinerary Agent (SGD)]
    itinerary --> food[🍽️ Food & Retail Agent (SGD)]
    food --> hotel[🏨 Hospitality Agent (SGD)]
    hotel --> guardrail{💰 Budget Guardrail}
    
    guardrail -->|80-90% SGD Passed / Flexible| judge[⚖️ Agent-as-Judge]
    guardrail -->|Budget Violated & Attempts < 3| itinerary
    guardrail -->|Attempts >= 3| busted[🚨 Budget Busted]
    
    judge --> final_out[✨ Final Output & Maps/CSV Export]
    final_out --> END([END])
    busted --> END
```

*For detailed state schemas and constraint documentation, see [specifications.md](specifications.md).*

---

## 📁 Project Structure

```
aitravelbuddy/
├── .streamlit/
│   └── config.toml          # Dark theme UI settings
├── core/
│   ├── __init__.py          # Core package init
│   ├── state.py             # LangGraph TravelBuddyState schema (with SGD & no_budget)
│   ├── personas.py          # Demographic profile definitions & rules
│   ├── utils.py             # Cost extraction, prompt formatting, DataFrame parser, text export
│   ├── agents.py            # Itinerary, Food/Retail, and Hospitality agent nodes (SGD)
│   ├── evaluation.py        # Budget guardrail & Agent-as-Judge nodes
│   └── graph.py             # StateGraph setup & conditional routing logic
├── app.py                   # Streamlit web frontend (Secrets, Maps, CSV export)
├── requirements.txt         # Project dependencies
├── specifications.md        # Comprehensive technical specification
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- [Google Gemini API Key](https://aistudio.google.com/apikey)
- [Tavily Search API Key](https://tavily.com)
- Optional: [Google Maps Platform API Key](https://console.cloud.google.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yanchangchen/aitravelbuddy.git
   cd aitravelbuddy
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Secrets (Optional):**
   Create `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your-gemini-key"
   TAVILY_API_KEY = "your-tavily-key"
   GOOGLE_MAPS_API_KEY = "your-gmaps-key"
   ```

4. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
