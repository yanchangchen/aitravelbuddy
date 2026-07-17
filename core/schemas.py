"""Pydantic schemas for structured LLM outputs in Travel Buddy agents."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ActivityItem(BaseModel):
    time_slot: str = Field(description="Time of day, e.g. Morning (10:00 AM)")
    activity: str = Field(description="Description of attraction or activity")
    est_cost_sgd: float = Field(description="Estimated cost in Singapore Dollars (SGD)")


class DailyItineraryDay(BaseModel):
    day_number: int = Field(description="Day number, e.g. 1")
    theme: str = Field(description="Theme or title of the day")
    activities: List[ActivityItem] = Field(default_factory=list)
    daily_transport_sgd: float = Field(default=0.0, description="Daily transport cost in SGD")


class ItineraryOutput(BaseModel):
    days: List[DailyItineraryDay] = Field(default_factory=list)
    sightseeing_total_sgd: float = Field(description="Total sightseeing & transport cost in SGD")
    formatted_markdown: str = Field(description="Complete day-by-day markdown text")


class MealItem(BaseModel):
    meal_type: str = Field(description="Breakfast, Lunch, Dinner, or Shopping")
    name: str = Field(description="Restaurant, cafe, or shop name")
    cuisine_or_type: str = Field(description="Cuisine type or what to buy")
    est_cost_sgd: float = Field(description="Estimated cost in SGD")


class DailyDiningDay(BaseModel):
    day_number: int
    meals: List[MealItem] = Field(default_factory=list)
    daily_dining_total_sgd: float = Field(default=0.0)


class FoodRetailOutput(BaseModel):
    days: List[DailyDiningDay] = Field(default_factory=list)
    food_retail_total_sgd: float = Field(description="Total dining & shopping cost in SGD")
    formatted_markdown: str = Field(description="Complete dining & retail markdown text")


class HotelOption(BaseModel):
    hotel_name: str
    star_rating: int = Field(default=3)
    location: str
    why_it_fits: str
    nightly_rate_sgd: float
    total_stay_sgd: float
    key_amenities: List[str] = Field(default_factory=list)


class HospitalityOutput(BaseModel):
    options: List[HotelOption] = Field(default_factory=list)
    recommended_hotel_name: str
    hotel_total_sgd: float = Field(description="Total lodging cost in SGD for recommended hotel")
    formatted_markdown: str = Field(description="Complete hotel recommendations markdown text")


class BookingLinkItem(BaseModel):
    category: str = Field(description="Flight, Hotel, Car Rental, or Attraction")
    title: str = Field(description="Link title")
    url: str = Field(description="Full HTTPS URL")


class PurchasingOutput(BaseModel):
    estimated_airfare_per_person_sgd: float
    airfare_total_sgd: float
    car_rental_daily_rate_sgd: float = Field(default=0.0)
    car_rental_total_sgd: float = Field(default=0.0)
    booking_links: List[BookingLinkItem] = Field(default_factory=list)
    formatted_markdown: str = Field(description="Complete purchasing guide markdown text")
