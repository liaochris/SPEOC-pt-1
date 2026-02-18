import unittest
from analyze_results import extract_county, STATE_NAMES

class TestExtractCounty(unittest.TestCase):
    def test_extract_county(self):
        # Case 1: town, county, state
        self.assertEqual(extract_county("Boston, Suffolk County, Massachusetts", "MA"), "SUFFOLK")
        
        # Case 2a: county, state
        self.assertEqual(extract_county("Essex County, Massachusetts", "MA"), "ESSEX")
        
        # Case 2b: town, county
        self.assertEqual(extract_county("Springfield, Hampden County", "MA"), "HAMPDEN")
        
        # Case 3: county only
        self.assertEqual(extract_county("Worcester County", "MA"), "WORCESTER")
        
        # Handles no 'County' word
        self.assertEqual(extract_county("Middlesex, Massachusetts", "MA"), "MIDDLESEX")
        
        # Handles lowercase and extra spaces
        self.assertEqual(extract_county("  barnstable county  ", "MA"), "BARNSTABLE")

if __name__ == "__main__":
    unittest.main()