# Start page 'https://www.flashscorekz.com/favourites/'
import logging
import time
import urllib3

import requests
import gspread

from gspread.spreadsheet import Spreadsheet
from gspread.exceptions import APIError
from googlesheets import CREDENTIALS

# /home/tournament_management/

FILEPATH_JSON = "data_processing/scrapping/"



def send_msg(msg_text: str,
             chat_id: str | int,
             token: str,
             retry: int = 5) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        requests.post(
            url=url,
            timeout=5,
            verify=False,
            data={
                'chat_id':  int(chat_id),
                'text': msg_text,
            }
        )
    except Exception as _ex:
        if retry:
            logging.info(f"retry={retry} send_msg => {_ex}")
            retry -= 1
            time.sleep(5)
            send_msg(msg_text, chat_id, token, retry)
        else:
            logging.info(f'Cannot send message to chat_id = {chat_id}')



class Connect:
    """Connecting to googlesheets by service account"""

    MONTH_JSON = 'games_month.json'
    WEEK_JSON = 'games_week.json'
    DAY_JSON = 'games_day.json'
    
    def __init__(self,
                 spreadsheet_id: str,
                 *args, **kwargs) -> None:
        self.spreadsheet = Connect.connect_to_gs(spreadsheet_id=spreadsheet_id)

    
    @staticmethod
    def connect_to_gs(spreadsheet_id: str, retry: int = 5) -> Spreadsheet:
        # connectig to googlesheets
        try:
            gc = gspread.service_account_from_dict(CREDENTIALS,
                                                   client_factory=gspread.BackoffClient)
            spreadsheet = gc.open_by_key(spreadsheet_id)
        except (APIError, Exception) as _ex:
            if retry:
                logging.info(f'retry={retry} => spreadsheet {_ex}')
                retry -= 1
                time.sleep(5)
                return Connect.connect_to_gs(spreadsheet_id, retry)
            else:
                raise
        return spreadsheet


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