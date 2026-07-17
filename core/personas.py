"""Persona profiles and constraint rules for Travel Buddy agents."""

PERSONA_PROFILES = {
    "single": {
        "label": "\U0001f9d1 Solo Traveler",
        "tempo": "high",
        "mobility": "high \u2014 public transit, walking, rideshares",
        "dining_style": "budget-efficient street food, local markets, casual eats",
        "accommodation": "hostels, capsule hotels, budget boutique stays",
        "rules": (
            "1. Pack the schedule tightly \u2014 aim for 4-6 activities per day.\n"
            "2. Prioritize public transit and walking routes over taxis.\n"
            "3. Focus on local hidden gems, off-the-beaten-path spots, and nightlife.\n"
            "4. Keep individual meal costs under $15 USD equivalent.\n"
            "5. Include at least one solo-friendly social activity per day "
            "(walking tours, bar crawls, co-working cafes).\n"
            "6. Late-night activities are encouraged.\n"
            "7. Accommodation should be centrally located for walkability."
        ),
    },
    "couple": {
        "label": "\U0001f491 Couple's Getaway",
        "tempo": "medium",
        "mobility": "balanced \u2014 scenic walks, occasional taxis for comfort",
        "dining_style": "curated restaurants, rooftop bars, aesthetic cafes",
        "accommodation": "boutique hotels, charming B&Bs, mid-to-high comfort",
        "rules": (
            "1. Balance activity with downtime \u2014 aim for 2-4 activities per day.\n"
            "2. Include scenic and aesthetic experiences (sunset viewpoints, gardens).\n"
            "3. Mornings should be relaxed \u2014 no activities before 9:30 AM.\n"
            "4. Curate at least one special dining experience per day.\n"
            "5. Include romantic or intimate activities (private tours, spa).\n"
            "6. Evening activities should wrap up by 10:30 PM unless nightlife is requested.\n"
            "7. Accommodation should emphasize ambiance and comfort over price."
        ),
    },
    "family": {
        "label": "\U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466 Family Adventure",
        "tempo": "low",
        "mobility": "low-friction \u2014 minimal stairs, stroller-accessible, short walks",
        "dining_style": "kid-friendly restaurants, familiar cuisine options available",
        "accommodation": "family suites, apartments with kitchenettes, resort-style",
        "rules": (
            "1. Keep the pace gentle \u2014 aim for 2-3 activities per day max.\n"
            "2. Include frequent rest stops and snack breaks every 2 hours.\n"
            "3. All attractions MUST be kid-friendly and stroller-accessible.\n"
            "4. NO activities after 7:30 PM \u2014 early nights are mandatory.\n"
            "5. NO nightlife, bars, or adult-only venues in the itinerary.\n"
            "6. Include at least one playground, park, or interactive kids' museum per day.\n"
            "7. Restaurants must have children's menus or kid-friendly options.\n"
            "8. Transportation should avoid crowded public transit during rush hours."
        ),
    },
}
