import unittest
from unittest.mock import Mock, patch, call
import requests
import os
from datetime import datetime

from ..football_data_api.data_fetcher import CompetitionData, url_filters

from football_data_api.tests import get_sample_data


class TestFunction(unittest.TestCase):
    def test_url_filters(self):
        date1 = datetime(2018, 6, 15)
        date2 = datetime(2018, 7, 26)
        self.assertEqual(url_filters(dateFrom=date1, dateTo=date2), '?dateFrom=2018-06-15&dateTo=2018-07-26&')
        self.assertEqual(url_filters(dateFrom='2018-06-15', dateTo='2018-07-26'),
                         '?dateFrom=2018-06-15&dateTo=2018-07-26&')

        self.assertEqual(url_filters(id=1, stage='group_stage'), '?id=1&stage=group_stage&')
        with self.assertRaises(ValueError):
            url_filters(not_a_filter='error')


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
    def test_init(self, mocked_get):
        mocked_get.return_value = response = Mock()
        response.status_code = 200
        response.json = Mock()
        response.json.return_value = get_sample_data('competitions')

        cd = CompetitionData('fifa world cup', 'TIER_TWO')

        with self.assertRaises(KeyError):
            cd = CompetitionData('TIER_TWO')

        cd = CompetitionData('primera division', 'TIER_FOUR')

    @patch('requests.get')
    def test_get_available_competitions(self, mocked_get):
        mocked_get.return_value = response = Mock()
        response.status_code = 200
        response.json = Mock()
        response.json.return_value = get_sample_data('competitions')

        data = self.cd.get_available_competitions()

        mocked_get.assert_called_with('https://api.football-data.org/v2/competitions?plan=TIER_ONE&',
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
        calls = [call('https://api.football-data.org/v2/competitions?plan=TIER_TWO&', headers=self.headers),
                 call('https://api.football-data.org/v2/competitions?plan=TIER_ONE&', headers=self.headers)]
        mocked_get.assert_has_calls(calls, any_order=True)
        self.assertEqual(mocked_get.call_count, 2)  # 2 For updating plan and one when initialised.
        self.assertEqual(cd.plan, 'TIER_TWO')

        with self.assertRaises(ValueError):
            cd.plan = 'tier 4'

    @patch('requests.get')
    def test_get_info(self, mocked_get):
        mocked_get.return_value = response = Mock()
        response.status_code = 200
        response.json = Mock()
        response.json.return_value = get_sample_data('competitions')

        cd = CompetitionData(competition_name='fifa world cup')

        response.json.return_value = get_sample_data('teams')
        self.assertEqual(cd.get_info('teams'), get_sample_data('teams'))
        mocked_get.assert_called_with('https://api.football-data.org/v2/competitions/2000/teams',
                                      headers=self.headers)

        response.json.return_value = get_sample_data('matches')
        self.assertEqual(cd.get_info('matches'), get_sample_data('matches'))
        mocked_get.assert_called_with('https://api.football-data.org/v2/competitions/2000/matches',
                                      headers=self.headers)

        date = datetime(2018, 7, 8)
        cd.get_info('matches', dateFrom=date, stage='groupstage')
        mocked_get.assert_called_with('https://api.football-data.org/v2/competitions/2000/matches?dateFrom=2018-07-08&'
                                      'stage=groupstage&', headers=self.headers)

        response.json.return_value = get_sample_data('competitions')
        cd.plan = 'TIER_FOUR'
        cd.competition = 'primera division'
        response.json.return_value = get_sample_data('matches')
        cd.get_info('matches')
        mocked_get.assert_called_with('https://api.football-data.org/v2/competitions/2014/matches',
                                      headers=self.headers)

        with self.assertRaises(ValueError):
            cd.get_info('nothing')


if __name__ == '__main__':
    unittest.main()
