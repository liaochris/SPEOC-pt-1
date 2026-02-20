import unittest
from source.analysis.pre1790.analyze_ancestry_results import ExtractCounty, STATE_NAMES

class TestExtractCounty(unittest.TestCase):
    def test_extract_county(self):
        # Case 1: town, county, state
        self.assertEqual(ExtractCounty("Boston, Suffolk County, Massachusetts", "MA"), "SUFFOLK")

        # Case 2a: county, state
        self.assertEqual(ExtractCounty("Essex County, Massachusetts", "MA"), "ESSEX")

        # Case 2b: town, county
        self.assertEqual(ExtractCounty("Springfield, Hampden County", "MA"), "HAMPDEN")

        # Case 3: county only
        self.assertEqual(ExtractCounty("Worcester County", "MA"), "WORCESTER")

        # Handles no 'County' word
        self.assertEqual(ExtractCounty("Middlesex, Massachusetts", "MA"), "MIDDLESEX")

        # Handles lowercase and extra spaces
        self.assertEqual(ExtractCounty("  barnstable county  ", "MA"), "BARNSTABLE")

if __name__ == "__main__":
    unittest.main()
