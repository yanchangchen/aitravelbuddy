# Travel Buddy — Project Directives & Guidelines

## 🎨 UI/UX Design Directives
- **Theme:** Clean Light Mode (`#FFFFFF` background, `#F8FAFC` slate sidebar, `#0F172A` high-contrast typography, `#FF6B6B` primary accent). Do NOT use dark mode backgrounds unless explicitly requested.
- **Location Maps:** All location maps MUST plot day-by-day venue/attraction pins extracted from itineraries using `extract_all_itinerary_locations()`. Maps must provide Pydeck 3D views, OpenStreetMap iframe fallbacks, and direct navigation links.
- **Group Composition:** Default travelers setup is **2 Adults, 1 Child (>2 yrs)**. Allow sidebar edits for Adults, Children, and Infants.
- **Transport & Purchasing:** Always include source city (origin), airfare estimates, optional self-drive car rental costs, and direct clickable HTTPS markdown booking links curated by `purchasing_agent`.
- **Budgets & Currencies:** Default currency is **Singapore Dollars (SGD / S$)**. Default budget mode is **Infinite / Flexible Budget** (`no_budget = True`).

## 🛠️ Engineering & Code Quality Directives
- **State Schema:** Keep `TravelBuddyState` typed, explicit, and backwards compatible.
- **Dependency Injection:** Planning and evaluation modules (`agents.py`, `evaluation.py`) must use dependency injection (`init(llm, search_tool)`) rather than global model instances.
- **Logging & Debugging:** Log all search queries, LLM calls, cost extraction details, and router decisions using `core/logger.py`.
- **Validation:** Always verify AST syntax parsing of Python code before committing.
- **Documentation:** Maintain `README.md`, `specifications.md`, `design.md`, and `architecture.md` up to date with system changes.
