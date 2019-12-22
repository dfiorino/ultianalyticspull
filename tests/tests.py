from unittest import TestCase

import ultianalyticspull.src.core.utils as utils
import urllib

class TestScraper(TestCase):

    def test_test(self):
        self.assertTrue(True)

    def test_new_method(self):
        
        team_number=4597087672991744

        url = f'http://www.ultianalytics.com/rest/view/team/{team_number}/stats/export'
        urllib.request.urlretrieve(url, 'test1.csv')
        df1 = utils.csv2dataframe('test1.csv')

        df2 = utils.team_dataframe(team_number)

        self.assertTrue(df1.equals(df2))
