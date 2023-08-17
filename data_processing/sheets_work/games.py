import time
import json
import os
import string

from ..config import Connect
from database import TOURNAMENT_TYPES
from googlesheets import (SPREADSHEET_ID,
                          GAMES_STANDART_URL,
                          GAMES_FAST_URL,
                          GAMES_SLOW_URL)



class Games(Connect):
    """Class for the work with the data in the spreadsheet with the tournament games"""
    
    CELLS_COLS = {
        'game_number': 'A',
        'sport': 'B',
        'begin_time': 'C',
        'teams': 'D',
        'coefficients': 'E',
        'url': 'F'
    }


    def __init__(self,
                 ws_name: str,
                 tourn_type: str,
                 full_data: dict = None,
                 *args, **kwargs) -> None:
        assert tourn_type in TOURNAMENT_TYPES, 'Unknown tournament type'
        super().__init__(SPREADSHEET_ID)

        self.games_data = full_data
        self.worksheet = self.spreadsheet.worksheet(ws_name)
        self.cells = string.ascii_uppercase
        self.tournament_type = tourn_type


    def _combining_cells_in_line(self, length: int, count_gs: int) -> None:
        # combining the required cells in one line
        if length in [2, 3]:
            offset = length - 1
        else:
            offset == 0
        
        # columns in which to merge rows
        columns = [
            self.CELLS_COLS['game_number'],
            self.CELLS_COLS['sport'],
            self.CELLS_COLS['begin_time'],
            self.CELLS_COLS['url']
        ]
        for i in columns:
            self.worksheet.merge_cells(
                name=f'{i}{count_gs}:{i}{count_gs + offset}',
                merge_type='MERGE_COLUMNS'
            )


    def write_data(self):
        # write all data to googlesheet
        full_data = []
        formats = []
        count_gs = 2
        count = 1
        for data in list(self.games_data.values()):
            length = len(data['coeffs'])

            self._combining_cells_in_line(length, count_gs)
            time.sleep(1)

            # writing the number of game in table
            column = self.CELLS_COLS["game_number"]
            full_data.append(
                {
                    'range': f'{column}{count_gs}',
                    'values': [[count]]
                }
            )
            formats.append(
                {
                    "range": f"{column}{count_gs}",
                    "format": {
                        "textFormat": {"bold": True},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                }
            )

            # writing the type of sport, the date and time and the link of the game
            for i in ['sport', 'begin_time', 'url']:
                column = self.CELLS_COLS[i]
                full_data.append(
                    {
                        "range": f"{column}{count_gs}",
                        "values": [[data.get(i)]]
                    }
                )
                formats.append(
                    {
                        "range": f"{column}{count_gs}",
                        "format": {
                            "horizontalAlignment": "CENTER",
                            "verticalAlignment": "MIDDLE"
                        }
                    }
                )

            # writing the teams and the coefficients
            offset = 0
            for team, coeff in data['coeffs'].items():
                full_data.append(
                    {
                        "range": f'{self.CELLS_COLS["teams"]}{count_gs + offset}',
                        "values": [[team, coeff]]
                    }
                )
                offset += 1

            formats.append(
                {
                    "range": f'{self.CELLS_COLS["teams"]}{count_gs}:' \
                             f'{self.CELLS_COLS["coefficients"]}{count_gs + offset}',
                    "format": {"horizontalAlignment": "LEFT"}
                }
            )
            
            count_gs += length
            count += 1

        self.worksheet.batch_update(full_data)
        self.worksheet.batch_format(formats)
        

    def clear_table(self):
        # Clear the table and unmerge the all cells
               
        last_row = len(
            self.worksheet.col_values(
                self.cells.index(self.CELLS_COLS['teams']) + 1
            )
        )
        if last_row < 2:
            last_row = 2
        cells_range = f'{self.CELLS_COLS["game_number"]}2:' \
                        f'{self.CELLS_COLS["url"]}{last_row}'
        self.worksheet.batch_clear([cells_range])
        self.worksheet.unmerge_cells(cells_range)
        
        path = self._get_json_path(self.tournament_type)
        os.remove(path)


    def approve_tournament_games(self):
        # approve the games to the tournament in table of the games 
        path = self._get_json_path(self.tournament_type)

        with open(path, 'r', encoding='utf-8') as file:
            games = json.load(file)
        games_data = list(games.values())
        update = False

        getting_data = []
        count = 1
        for game in games_data:
            length = len(game['coeffs'])
            getting_data.append(
                f'{self.CELLS_COLS["sport"]}{count + 1}:{self.CELLS_COLS["url"]}{count + length}'
            )
            count += length
        
        gs_data = self.worksheet.batch_get(getting_data)
    
        count = 2
        for line, game in zip(gs_data, games_data):
            url = line[0][-1]
            if url != game['url']:
                game['url'] = url
                update = True

            for pair, row in zip(game['coeffs'].items(), line):
                length = len(row)
                pair_gs = tuple()

                if length == 3: pair_gs = (row[-1], "")
                elif length == 4: pair_gs = tuple(row[-2:])
                elif length == 5: pair_gs = tuple(row[-3:-1])

                if pair != pair_gs:
                    game['coeffs'][pair_gs[0]] = pair_gs[1]
                    update = True

        if update:
            for i, j in zip(games_data, games):
                games[j] = i

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(games, file, indent=4, ensure_ascii=False)
            
                
    def color_cell(self, game_key: str, color: str, winner = None) -> None:
        assert color not in ('green', 'red'), 'Unknown color'

        game_url = f'https://www.flashscorekz.com/match/{game_key}/#/match-summary'
        in_column = self.cells.index(self.CELLS_COLS['url']) + 1
        cell = self.worksheet.find(query=game_url, in_column=in_column)
        
        if color == 'green':
            row = cell.row + winner - 1
            ranges = f"{self.CELLS_COLS['teams']}{row}:{self.CELLS_COLS['coefficients']}{row}"
        else:
            ranges = f"{self.CELLS_COLS['url']}{cell.row}"

        self.worksheet.format(
            ranges=ranges,
            format={"backgroundColor": {color: 1.0}}
        )



class FAST(Games):
    """sheet games FAST"""

    SHEET_NAME = "Матчи FAST"
    TOURN_TYPE = 'FAST'
    URL = GAMES_FAST_URL


    def __init__(self,
                 games_data: dict = None,
                 *args, **kwargs) -> None:
        super().__init__(
            ws_name=self.SHEET_NAME,
            tourn_type=self.TOURN_TYPE,
            full_data=games_data, *args, **kwargs
        )



class STANDART(Games):
    """sheet games STANDART"""

    SHEET_NAME = "Матчи STANDART"
    TOURN_TYPE = 'STANDART'
    URL = GAMES_STANDART_URL


    def __init__(self,
                 games_data: dict = None,
                 *args, **kwargs) -> None:
        super().__init__(
            ws_name=self.SHEET_NAME,
            tourn_type=self.TOURN_TYPE,
            full_data=games_data, *args, **kwargs
        )



class SLOW(Games):
    """sheet games SLOW"""

    SHEET_NAME = "Матчи SLOW"
    TOURN_TYPE = 'SLOW'
    URL = GAMES_SLOW_URL

    def __init__(self,
                 games_data: dict = None,
                 *args, **kwargs) -> None:
        super().__init__(
            ws_name=self.SHEET_NAME,
            tourn_type=self.TOURN_TYPE,
            full_data=games_data, *args, **kwargs
        )
