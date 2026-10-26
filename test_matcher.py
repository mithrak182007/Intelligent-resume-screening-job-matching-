import unittest
from matcher import analyze_resume

class MatcherTests(unittest.TestCase):
    def test_match_and_missing_evidence(self):
        result = analyze_resume("I used Python and SQL to build a project.", ["Python", "SQL", "Git"], {"Python": 3, "SQL": 2, "Git": 1})
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["score"], 83)
        self.assertEqual(result["criteria"][2]["Match status"], "No evidence found")
        self.assertIn("does not prove", result["criteria"][2]["Resume evidence"])

if __name__ == "__main__":
    unittest.main()
