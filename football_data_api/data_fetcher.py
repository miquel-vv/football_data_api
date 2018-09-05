import os
import requests
from datetime import datetime

PLANS = ['TIER_ONE', 'TIER_TWO', 'TIER_THREE', 'TIER_FOUR']
FILTERS = {'dateFrom', 'dateTo', 'id',
           'matchday', 'season', 'status',
           'venue', 'stage', 'plan',
           'competitions', 'group', 'limit'}


def url_filters(**kwargs):
    global FILTERS
    if not kwargs:
        return ''
    template_filter = '{filter}={value}&'
    filters = '?'
    for filt, value in kwargs.items():
        if filt not in FILTERS:
            raise ValueError('{} is not a valid filter, valid filters are: {}'.format(filt, FILTERS))
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d')
        else:
            value = str(value)
        filters += template_filter.format(filter=filt, value=value)
    return filters


def check_and_return_json(fn):
    """Helper function. Checks status codes and returns the body in dict format if status code was 200."""
    def wrapped(*args, **kwargs):
        r = fn(*args, **kwargs)
        if r.status_code == 400:
            raise ValueError(r.json()['message'])
        if r.status_code != 200:
            raise ValueError('Calling {} returned a {} status code'.format(r.request.url, r.status_code))
        return r.json()
    return wrapped


def one_competition(fn):
    def wrapped(*args, **kwargs):
        o = args[0]
        if not o.competition:
            raise Exception('No competition set.')
        kwargs['url'] = '{}/{}/'.format(o.BASE_URL, o._competition)
        return fn(*args, **kwargs)
    return wrapped


class CompetitionData:
    """A CompetitionData object is an object that helps making calls to the football-data.org api. Each object created is linked
    to a competition. If the competition is not chosen only the available competitions will be shown. By default the
    available competitions.json are limited to the 'TIER ONE' pay plan (for more information visit:
    https://www.football-data.org/coverage)."""

    def __init__(self, competition_name=None, plan='TIER_ONE'):
        self.BASE_URL = 'https://api.football-data.org/v2/competitions'
        self._plan = plan
        self._competition = 0  # competition is the football-data id for the chosen competition.
        self.competition_name = ''
        try:
            self.headers = {'X-Auth-Token': os.environ["FOOTBALL_DATA_API"]}
        except KeyError:
            raise KeyError('The environment variable "FOOTBALL_DATA_API" is not set. This should be your api key.')
        self.available_competitions = self.get_available_competitions()

        if competition_name is not None:
            self.competition = competition_name

    def get_available_competitions(self):
        """returns the available """
        global PLANS
        include = False
        competitions = []

        for pl in PLANS[::-1]:
            include = True if pl == self.plan else include  # remains True once plan is reached.
            if not include:
                continue
            competitions += self.competitions(pl)['competitions']

        return {comp['name'].lower(): comp['id'] for comp in competitions}

    @check_and_return_json
    def competitions(self, plan):
        url = self.BASE_URL + url_filters(plan=plan)
        return requests.get(url, headers=self.headers)

    @check_and_return_json
    @one_competition
    def get_info(self, type, **kwargs):
        """Method to request data from the football-data api and return the body of the response in dict format.
        The information requested with this method only relates to one competition, so a competition needs to be set
        before this is used.
        It accepts a type argument that should be either competition, teams or matches. This is the info that will be
        returned. The **kwargs are any relevant filters that need to be applied."""

        if type not in {'teams', 'matches', 'competition'}:
            raise ValueError('type should be either teams, matches or competition not {}'.format(type))

        url = kwargs.pop('url') if type == 'competition' else kwargs.pop('url') + type
        url += url_filters(**kwargs)
        return requests.get(url, headers=self.headers)

    @property
    def plan(self):
        return self._plan

    @plan.setter
    def plan(self, value):
        """Update the available competitions once plan has changed."""
        global PLANS
        if value not in PLANS:
            raise ValueError('{} is not an excepted plan, choose from: {}'.format(value, PLANS))
        self._plan = value
        self.available_competitions = self.get_available_competitions()

    @property
    def competition(self):
        """Abstraction made to interact with the competition. Whilst internally both the competition id and competition
        name are stored, user only has to deal with competition name."""
        return self.competition_name

    @competition.setter
    def competition(self, competition_name):
        try:
            competition_name = competition_name.lower()
            self._competition = self.available_competitions[competition_name]
            self.competition_name = competition_name
        except KeyError:
            raise KeyError('{} is not an available competition, available competitions.json are: {}'
                           .format(competition_name, ', '.join(name for name in self.available_competitions)))

