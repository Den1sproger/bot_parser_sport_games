from googlesheets import COMPARISON_SPREADSHEET_ID
from ..config import Connect
from database import (Database,
                      get_prompt_view_nick_by_id,
                      TOURNAMENT_TYPES)



class Comparison(Connect):
    """Class for the work with the comparison list of users"""

    CHAT_ID_COLUMN = 2

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(COMPARISON_SPREADSHEET_ID)
        self.wss = self.spreadsheet.worksheets()


    def get_tournaments(self, tourn_type: str) -> list[list[str, int]]:
        assert tourn_type in TOURNAMENT_TYPES, 'Unknown tournament type'

        data = []
        db = Database()
        for ws in self.wss:
            if tourn_type in ws.title.upper():
                chat_ids = set(ws.col_values(self.CHAT_ID_COLUMN)[1:])
                for chat_id in chat_ids:
                    try:
                        nickname = db.get_data_list(
                            get_prompt_view_nick_by_id(chat_id)
                        )[0]['nickname']
                    except (KeyError, IndexError):
                        pass
                    else:
                        data.append([nickname, 0, ws.title])
                        
        return data