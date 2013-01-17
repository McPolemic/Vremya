from django.utils import unittest
from datetime import date
import utils

class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_leap_year_should_give_correct_year_and_week(self):
        (year, week) = utils.find_week_from_date(date(2012,1,1))

        self.assertEqual(year, 2011)
        self.assertEqual(week, 52)

if __name__=="__main__":
    unittest.main()
