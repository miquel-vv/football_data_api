import unittest
from unittest.mock import Mock, patch, call
import requests
import os

from ..football_data_api.data_fetcher import CompetitionData

from football_data_api.tests import get_sample_data


class TestCompetitionData(unittest.TestCase):

    @patch('requests.get')
    def setUp(self, mocked_get):
        mocked_get.return_value = response = Mock()
        response.status_code = 200
        response.json = Mock()
        response.json.return_value = get_sample_data('competitions')
        self.cd = CompetitionData()
        self.headers = {'X-Auth-Token': os.environ["FOOTBALL_DATA_API"]}

    def test_default_settings(self):
        self.assertEqual(self.cd.available_competitions,
                         {'primera division': 2014, 'fifa world cup': 2000})
        self.assertEqual(self.cd.plan, 'TIER_ONE')
        self.assertEqual(self.cd.competition, '')
        self.assertEqual(self.cd.headers, self.headers)

    @patch('requests.get')
    def test_get_available_competitions(self, mocked_get):
        mocked_get.return_value = response = Mock()
        response.status_code = 200
        response.json = Mock()
        response.json.return_value = get_sample_data('competitions')

        data = self.cd.get_available_competitions()

        mocked_get.assert_called_with('https://api.football-data.org/v2/competitions/?plan=TIER_ONE&',
                                      headers=self.headers)

        self.assertEqual(data, {'primera division': 2014, 'fifa world cup': 2000})

        response.status_code = 404
        with self.assertRaises(ValueError):
            self.cd.get_available_competitions()

    @patch('requests.get')
    def test_plan(self, mocked_get):
        mocked_get.return_value = response = Mock()
        response.status_code = 200
        response.json = Mock()
        response.json.return_value = get_sample_data('competitions')

        cd = CompetitionData()
        self.assertEqual(cd.plan, 'TIER_ONE')

        mocked_get.reset_mock()
        cd.plan = 'TIER_TWO'
        calls = [call('https://api.football-data.org/v2/competitions/?plan=TIER_TWO&', headers=self.headers),
                 call('https://api.football-data.org/v2/competitions/?plan=TIER_ONE&', headers=self.headers)]
        mocked_get.assert_has_calls(calls, any_order=True)
        self.assertEqual(mocked_get.call_count, 2)  # 2 For updating plan and one when initialised.
        self.assertEqual(cd.plan, 'TIER_TWO')

        with self.assertRaises(ValueError):
            cd.plan = 'tier 4'



if __name__ == '__main__':
    unittest.main()
