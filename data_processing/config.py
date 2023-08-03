# Start page 'https://www.flashscorekz.com/favourites/'
import logging
import time

import gspread

from googlesheets import CREDENTIALS


FILEPATH_JSON = "/home/tournament_management/data_processing/scrapping/"



class Connect:
    """Connecting to googlesheets by service account"""

    MONTH_JSON = 'games_month.json'
    WEEK_JSON = 'games_week.json'
    DAY_JSON = 'games_day.json'
    
    def __init__(self,
                 spreadsheet_id: str,
                 retry: int = 5,
                 *args, **kwargs) -> None:
        # connectig to googlesheets
        try:
            self.gc = gspread.service_account_from_dict(CREDENTIALS,
                                                        client_factory=gspread.BackoffClient)
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
        except Exception as _ex:
            if retry:
                logging.info(f'retry={retry} => spreadsheet {_ex}')
                retry -= 1
                time.sleep(5)
                self.__init__(spreadsheet_id, retry)
            else:
                raise


    def _get_json_path(self, type_: str) -> str:
        path = FILEPATH_JSON
        if type_ == 'FAST':
            path += self.DAY_JSON
        elif type_ == 'STANDART':
            path += self.WEEK_JSON
        else:
            path += self.MONTH_JSON
        return path


    def __del__(self):
        return

