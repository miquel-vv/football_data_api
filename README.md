#Football Data Api (Python Interface)

##1. Introduction
This tool was built using the api provided by [football-data.org](https://www.football-data.org/) so all kudos go to Daniel, 
the creator of that tool.

The intend of the tool is to **simplify requests** to the api **for python** use. It does not rearrange any of the responses, it 
simply offers an interface and returns the response in a dictionary format.

##2. How to install it.

##3. How to use it.
#### 3.1 Starting
After installing the package, simply create a CompetitionData object. The CompetitionData object accepts two optional
arguments: competition name and plan. Plan refers to the tier system that football-data.org uses to manage the payment 
system. You can find out more about plans [here](https://www.football-data.org/coverage). The default plan is Tier One
which is the free tier. The default competition is an empty string. If you provide a competition name, make sure it has 
the same name as on football-data.org.

Instantiate CompetitionData object:
    
    >>> from football_data_api import data_fetchers
    >>> data = data_fetchers.CompetitionData()
    
#### 3.2 Setting the competition
If you are not sure which competitions you can choose from or how the competition is named exactly, you can call the 
get_available_competitions method that will return a dictionary with all available competitions as keys and their id as values. The 
available competitions to you will be based on the currently set plan.

    >>> data.get_available_competitions()
    {'série a': 2013, 
    'championship': 2016, 
    'premier league': 2021, 
    'european championship': 2018, 
    'uefa champions league': 2001, 
    'ligue 1': 2015, 
    'bundesliga': 2002, 
    'serie a': 2019, 
    'eredivisie': 2003, 
    'primeira liga': 2017, 
    'primera division': 2014, 
    'fifa world cup': 2000}

If there is ambiguity or you are not sure what competition the competition name relates to, you can find more details [here](https://www.football-data.org/coverage)
To set a competition you simply assign the competition name to the competition attribute of the CompetitionData object.

    >>> data.competition = 'premier league'
    >>> 
    
A KeyError will be raised if the competition name isn't available. The competition that is being set is the current
competition, changing this is not supported at the moment.

Once you have set a competition, you can start querying information about that competition. Currently on a competition 
level, the information you can ask for relates to the competition itself, the teams in the competition and the 
matches (games) in the competition.

To get information, the method get_info(type, filters as kwargs) should be called. The first (excluding self) argument
type refers to the type of information you are looking for. As said, three types are currently supported for competitions,
'teams', 'matches', 'competition'. Other arguments passed, should be passed as keyword arguments and will be used to 
filter the response. Common filters are: dateFrom=yyyy-mm-dd, dateTo=yyyy-mm-dd, id=int, matchday=int, status=string.

    >>> teams_in_premier = data.get_info('teams')
    >>> from datetime import datetime
    >>> date_today = datetime.today()
    >>> matches = data.get_info('matches', dateFrom='2018-08-01', dateTo=date_today)

The date filters can be passed in the format above or as python's datetime objects. id refers to the specific team id, 
matchday refers to the matchday in the current season (e.g. matchday 1 of season 2018-2019), status is an important 
filter for matches as it refers to the progress of games, you can use status to only get games that are in progress by 
passing status='IN_PLAY', a full description of match status can be found [here](https://www.football-data.org/assets/v2_status_diagram.png).
When a filter is passed that is not supported by football-data.org a ValueError will be raised. A complete list of filters
and how to use them can be found [here](https://www.football-data.org/documentation/quickstart). 
    
    >>> games_in_play = data.get_info('matches', status='IN_PLAY')
    
_Note on filters: Not all filters work on all type of request (e.g. passing a matchday filter when looking up teams doesn't
make sense). Currently these checks are not included in the interface, when an invalid filter is passed, the api will 
simply return an unfiltered result._

##4. Next Steps
Next items to be included:
  * Fetchers for info about teams and their players.
  * Keep track of api request for heavy api use (Limit of 10 per minute at the moment which is not being checked by this
  interface).
  * Include possibility to set competition by id.

#### N.B.
Please feel free to contribute to this project, I made this with my own needs in mind and therefore didn't include all 
useful functionality.
