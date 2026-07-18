"""Persona profiles and constraint rules for Travel Buddy agents."""

PERSONA_PROFILES = {
    "single": {
        "label": "🧑 Solo Traveler",
        "tempo": "high",
        "mobility": "high — public transit, walking, rideshares",
        "dining_style": "budget-efficient street food, local markets, casual eats",
        "accommodation": "hostels, capsule hotels, budget boutique stays",
        "rules": (
            "1. Pack the schedule tightly — aim for 4-6 activities per day.\n"
            "2. Prioritize public transit and walking routes over taxis.\n"
            "3. Focus on local hidden gems, off-the-beaten-path spots, and nightlife.\n"
            "4. Keep individual meal costs under $15 USD equivalent.\n"
            "5. EXPLICITLY RECOMMEND solo-friendly social activities (walking tours, bar crawls, co-working cafes, meetups).\n"
            "6. Late-night activities are encouraged.\n"
            "7. Accommodation should be centrally located for walkability."
        ),
    },
    "business": {
        "label": "💼 Business Traveler",
        "tempo": "efficient",
        "mobility": "high convenience — taxis, Ubers, private shuttles",
        "dining_style": "power lunches, high-end networking spots, room service",
        "accommodation": "business hotels (centrally located, strong Wi-Fi, executive lounges)",
        "rules": (
            "1. Assume daytime is booked for work (9:00 AM - 5:00 PM). Focus itinerary generation purely on evenings (after 5 PM) and early mornings (before 9 AM).\n"
            "2. Prioritize extreme convenience and time-saving transit options (taxis/rideshares).\n"
            "3. Recommend high-end dining suitable for networking or solo relaxation.\n"
            "4. Accommodations MUST have strong Wi-Fi and executive amenities.\n"
            "5. Keep the non-work schedule structured but relaxed — 1-2 activities per day."
        ),
    },
    "couple": {
        "label": "💑 Couple's Getaway",
        "tempo": "medium",
        "mobility": "balanced — scenic walks, occasional taxis for comfort",
        "dining_style": "curated restaurants, rooftop bars, aesthetic cafes",
        "accommodation": "boutique hotels, charming B&Bs, mid-to-high comfort",
        "rules": (
            "1. Balance activity with downtime — aim for 2-4 activities per day.\n"
            "2. Include scenic and aesthetic experiences (sunset viewpoints, gardens).\n"
            "3. DYNAMICALLY HIGHLIGHT 'Golden Hour / Sunset' activities and private/intimate experiences using emojis (🌅).\n"
            "4. Curate at least one special dining experience per day.\n"
            "5. Mornings should be relaxed — no activities before 9:30 AM.\n"
            "6. Accommodation should emphasize ambiance and comfort over price."
        ),
    },
    "family": {
        "label": "👨‍👩‍👧‍👦 Family Adventure",
        "tempo": "low",
        "mobility": "low-friction — minimal stairs, stroller-accessible, short walks",
        "dining_style": "kid-friendly restaurants, familiar cuisine options available",
        "accommodation": "family suites, apartments with kitchenettes, resort-style",
        "rules": (
            "1. ENFORCE a strict maximum of 2-3 activities per day.\n"
            "2. Include explicit 'Rest/Nap Blocks' in the itinerary.\n"
            "3. Flag nearby essential facilities (parks, restrooms, kid-friendly areas) for major attractions.\n"
            "4. All attractions MUST be kid-friendly and stroller-accessible.\n"
            "5. NO activities after 7:30 PM — early nights are mandatory.\n"
            "6. Food & Retail recommendations MUST explicitly include restaurants with kids' menus or play areas.\n"
            "7. Transportation should avoid crowded public transit during rush hours."
        ),
    },
    "backpacker": {
        "label": "🎒 Budget Backpacker",
        "tempo": "high",
        "mobility": "maximum walkability & public transit — trains, buses, walking",
        "dining_style": "street food stalls, night markets, local food courts, grocery finds",
        "accommodation": "social hostels, guesthouses, shared dorms or budget private rooms",
        "rules": (
            "1. Focus on free or ultra-low-cost attractions (parks, public squares, viewpoints, free museum days).\n"
            "2. Prioritize authentic street food and local markets over sit-down restaurants.\n"
            "3. Use public transport or walking exclusively — avoid private taxis.\n"
            "4. Include social hostel vibes or local community spots.\n"
            "5. Keep daily spending extremely lean while maximizing cultural immersion.\n"
            "6. Offer practical backpacker money-saving tips for each day."
        ),
    },
}
