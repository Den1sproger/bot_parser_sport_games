# Start page 'https://www.flashscorekz.com/favourites/'

import gspread

from googlesheets import CREDENTIALS


FILEPATH_JSON = "/home/tournament_management/data_processing/scrapping/"



class Connect:
    """Connecting to googlesheets by service account"""

    WEEK_JSON = 'games_week.json'
    DAY_JSON = 'games_day.json'
    
    def __init__(self,
                 spreadsheet_id: str,
                 *args, **kwargs) -> None:
        # connectig to googlesheets
        self.gc = gspread.service_account_from_dict(CREDENTIALS,
                                                    client_factory=gspread.BackoffClient)
        self.spreadsheet = self.gc.open_by_key(spreadsheet_id)


    def __del__(self):
        return

