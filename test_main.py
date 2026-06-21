import unittest
from assistant import SmartAssistant
from models import ActivityLog

class TestAssistantEngine(unittest.TestCase):
    def setUp(self):
        self.assistant = SmartAssistant()

    def test_calculate_emission_known_values(self):
        # Transportation: Car is 0.192 per km. 10km should be 1.92
        emission = self.assistant.calculate_emission("transportation", "car", 10.0)
        self.assertEqual(emission, 1.92)

    def test_calculate_emission_unknown_category(self):
        # Unknown subcategory should return 0.0
        emission = self.assistant.calculate_emission("transportation", "spaceship", 100.0)
        self.assertEqual(emission, 0.0)

    def test_generate_insights_empty_logs(self):
        insights = self.assistant.generate_insights([])
        self.assertEqual(len(insights), 1)
        self.assertIn("Welcome! Start logging", insights[0])

    def test_generate_insights_with_data(self):
        # Create a mock ActivityLog for testing
        log1 = ActivityLog(category="food", carbon_emission=27.0)
        log2 = ActivityLog(category="transportation", carbon_emission=1.92)
        
        insights = self.assistant.generate_insights([log1, log2])
        # It should tell us food is the highest
        self.assertTrue(any("food" in insight for insight in insights))

if __name__ == '__main__':
    unittest.main()
