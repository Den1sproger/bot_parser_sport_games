import requests

from fake_useragent import UserAgent
from ..config import Connect
from googlesheets import SPREADSHEET_ID



class Parser(Connect):
    """Base class for the scrapping data from the flashscorekz.com"""

    def __init__(self):
        super().__init__(SPREADSHEET_ID)
        self.ua = UserAgent(browsers=["chrome"])


    def _create_game_request(self, url: str) -> list[str]:
        # get data by the request for the one game
        headers = {
            'authority': 'local-ruua.flashscore.ninja',
            'accept': '*/*',
            'origin': 'https://www.flashscorekz.com',
            'referer': 'https://www.flashscorekz.com/',
            'user-agent': self.ua.random,
            'x-fsign': 'SW9D1eZo',
        }
        response = requests.get(url=url, headers=headers)
        return response.text.split('¬')


    def _get_data_time(self, game_id: str, data_key: str) -> int:
        # get data of time from the request of one game
        data: int

        game_data = self._create_game_request(
            url=f'https://local-ruua.flashscore.ninja/46/x/feed/dc_1_{game_id}'
        )
        for item in game_data:
            if data_key in item:
                data = int(item.split('÷')[-1])
                break

        return data