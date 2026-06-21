class SmartAssistant:
    def __init__(self):
        # Emission factors (approximate kg CO2 per unit)
        self.emission_factors = {
            "transportation": {
                "car": 0.192, # per km
                "bus": 0.089, # per km
                "train": 0.041, # per km
                "flight": 0.255, # per km
                "bike": 0.0,
                "walk": 0.0
            },
            "food": {
                "beef": 27.0, # per kg
                "chicken": 6.9, # per kg
                "vegetarian": 2.0, # per meal (avg)
                "vegan": 1.5, # per meal (avg)
            },
            "energy": {
                "electricity": 0.4, # per kWh (global average roughly)
                "natural_gas": 0.2 # per kWh
            }
        }

    def calculate_emission(self, category: str, subcategory: str, value: float) -> float:
        """Calculates carbon emission based on category and value."""
        if value is None:
            return 0.0
        try:
            val = float(value)
            if val < 0:
                return 0.0
            factor = self.emission_factors[category][subcategory]
            return round(factor * val, 2)
        except (KeyError, ValueError, TypeError):
            return 0.0

    def generate_insights(self, logs: list) -> list:
        """Analyzes logs and generates personalized tips."""
        insights = []
        if not logs:
            return ["Welcome! Start logging your activities to get personalized carbon reduction tips."]

        total_emission = sum(log.carbon_emission for log in logs)
        
        # Categorize emissions
        emissions_by_cat = {"transportation": 0, "food": 0, "energy": 0}
        for log in logs:
            if log.category in emissions_by_cat:
                emissions_by_cat[log.category] += log.carbon_emission
        
        # Find highest category
        highest_cat = max(emissions_by_cat, key=emissions_by_cat.get)
        highest_val = emissions_by_cat[highest_cat]

        if total_emission > 0:
            insights.append(f"Your highest footprint comes from **{highest_cat}** ({highest_val:.2f} kg CO2).")

        # Specific rule-based advice
        if highest_cat == "transportation":
            insights.append("💡 Consider carpooling, taking public transit, or biking for short distances to significantly cut down your transport emissions.")
        elif highest_cat == "food":
            insights.append("💡 Try incorporating more plant-based meals into your diet. Beef has one of the highest carbon footprints!")
        elif highest_cat == "energy":
            insights.append("💡 Remember to turn off lights when leaving a room and consider switching to energy-efficient LED bulbs.")

        # Praise for low footprint
        if total_emission < 10 and len(logs) > 3:
            insights.append("🌟 Great job keeping your footprint low! You are doing an amazing job for the planet.")

        return insights

assistant_engine = SmartAssistant()
