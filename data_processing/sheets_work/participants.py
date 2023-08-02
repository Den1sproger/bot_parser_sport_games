import string

from ..config import Connect
from database import (TOURNAMENT_TYPES,
                      Database,
                      PROMPT_VIEW_LAST_SCORES)
from googlesheets import SPREADSHEET_ID


    
class Rating(Connect):
    """
    Class for the work with the participants of the current tournament
    in the worksheet with the raiting of participants
    """
    CELLS_COLS = {
        "nickname": "A",
        "score": "B",
        "tourn_type": "C"
    }
    LENGTH = len(CELLS_COLS)
    BETWEEN = 1
    OFFSET = LENGTH + BETWEEN
    SHEET_NAME = "Текущий рейтинг"


    def __init__(self, tourn_type: str, *args, **kwargs) -> None:
        assert tourn_type in TOURNAMENT_TYPES, 'Unknown tournament type'

        super().__init__(SPREADSHEET_ID)
        self.cells = string.ascii_uppercase
        self.tournament_type = tourn_type
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)
        

    def _get_column(self, column: str) -> str:
        if self.tournament_type == 'FAST':
            return self.CELLS_COLS[column]
        elif self.tournament_type == 'STANDART':
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET]
        else:
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET * 2]
        
    
    def clear_table(self):
        # Clear the all cells in the table
        column = self._get_column('nickname')
        
        last_row = len(
            self.worksheet.col_values(self.cells.index(column) + 1)
        )
        left_top_cell = f'{self._get_column("nickname")}3'
        right_low_cell = f'{self._get_column("score")}{last_row + 1}'

        self.worksheet.batch_clear([f'{left_top_cell}:{right_low_cell}'])


    def add_rating(self, participants: list[list[str, int]]) -> None:
        # clear one of rating tables and write the new data
        self.clear_table()
        self.worksheet.batch_update([
            {
                'range': f"{self._get_column('nickname')}3",
                'values': participants
            }
        ])


class Users(Connect):
    """Class for the work with the data in the admin worksheet with the all users"""

    CELLS_COLS = {
        "username": "A",
        "chat_id": "B",
        "nickname": "C",
        "score": "D"
    }
    SHEET_NAME = "Пользователи"


    def __init__(self, *args, **kwargs):
        super().__init__(SPREADSHEET_ID)
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)


    def update_scores(self):
        # update the scores of users in the table with all users
        update_data = []

        db = Database()
        new_scores = db.get_data_list(PROMPT_VIEW_LAST_SCORES)

        nicknames_from_gs = self.worksheet.col_values(3)[1:]

        for item in new_scores:
            row = nicknames_from_gs.index(item['nickname']) + 2
            cell = f"{self.CELLS_COLS['score']}{row}"
            update_data.append({
                'range': cell,
                'values': [[item['all_scores']]]
            })
            
        self.worksheet.batch_update(update_data)


