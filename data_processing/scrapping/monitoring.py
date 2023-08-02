import string

from database import (Database_Thread,
                      TOURNAMENT_TYPES,
                      get_prompt_view_games_id,
                      get_prompt_update_status,
                      get_prompt_view_users_by_answer,
                      get_prompt_add_scores,
                      get_prompt_view_game_coeffs,
                      get_prompt_view_nick_by_id)
from .parser import Parser
from ..sheets_work.participants import Users



class Monitoring(Parser):
    """Monitoring the games and update data in database"""

    CELLS_COLS = {
        "nickname": "A",
        "score": "B",
        "tourn_type": "C"
    }
    LENGTH = len(CELLS_COLS)
    BETWEEN = 1
    OFFSET = LENGTH + BETWEEN
    SHEET_NAME = 'Текущий рейтинг'
    

    def __init__(self, *tourn_types) -> None:
        for tt in tourn_types:
            assert tt in TOURNAMENT_TYPES, 'Unknown tournament type'
        self.tournament_types = tourn_types

        super().__init__()
        self.worksheet = self.spreadsheet.worksheet(self.SHEET_NAME)
        self.cells = string.ascii_uppercase
        

    def _get_column(self, column: str, tourn_type: str) -> str:
        if tourn_type == 'FAST':
            return self.CELLS_COLS[column]
        elif tourn_type == 'STANDART':
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET]
        else:
            return self.cells[self.cells.index(self.CELLS_COLS[column]) + self.OFFSET * 2]


    def check_status(self) -> None | list[str]:
        # main function
        # checking the status of the games and update data in database
        completed_types = []
        db = Database_Thread()
        update_data = []

        for type_ in self.tournament_types:

            games = db.get_data_list(               # get games
                get_prompt_view_games_id(type_)
            )
            if games:
                
                games_id = [i[0] for i in games]      # get keys of games
                for game in games_id:                                   # games iteration

                    status = self._get_data_time(game, data_key='DA')
                    if status in [2, 3]:                                # if the game time status is not 1
                        
                        if status == 3:                                 # if the game is over
                            
                            coeffs = db.get_data_list(
                                get_prompt_view_game_coeffs(game)
                            )[0]
                            coeffs = list(coeffs)
                            result = self.get_winner(game)   # winner

                            answers = db.get_data_list(
                                get_prompt_view_users_by_answer(game, type_)
                            )
                            for answer in answers:                        # game answers iteration
                                
                                if result == answer[1]:            # if user's answer is right
                                    # get the user internal nickname by Telegram chat id 
                                    nickname = db.get_data_list(            
                                        get_prompt_view_nick_by_id(answer[0])
                                    )[0][0]

                                    scores = self.get_scores_by_coeff(coeffs[result - 1])
                                    
                                    # update the user's scoes in the current table in the googlesheets
                                    cell, adding_scores = self.get_cell_add_score(
                                        score=scores, nickname=nickname,
                                        tourn_type=type_,
                                        tournament=answer[-1]
                                    )
                                    update_data.append({
                                        'range': cell, 'values': [[adding_scores]]
                                    })

                                    # update the user's scores in the participants table in the database
                                    prompts = get_prompt_add_scores(
                                        adding_scores=scores,
                                        nickname=nickname,
                                        tournament=answer[-1]
                                    )
                                    db.action(*prompts)
                            # update scores
                            self.worksheet.batch_update(update_data)
                        db.action(
                            get_prompt_update_status(game, status)
                        )

            else:       # tournament is over
                completed_types.append(type_)

        # update rating
        self.update_rating()

        # if the tournament or tournaments are over
        if completed_types:
            users = Users()
            users.update_scores()
            return completed_types


    def get_winner(self, game_id) -> int:
        # get the end scores of the teams
        data = self._create_game_request(
            url=f'https://local-ruua.flashscore.ninja/46/x/feed/dc_1_{game_id}'
        )
        string = {}
        for item in data:
            key = item.split('÷')[0]
            value = item.split('÷')[-1]
            string[key] = value

        score_1 = string['DE']
        score_2 = string['DF']
        if score_1 > score_2:
            return 1        # the first team win
        elif score_1 < score_2:
            return 2        # the second team win
        else:
            return 3        # draw
        

    def get_scores_by_coeff(self, coeff: str) -> int:
        # get the quantity of scores by coefficient
        coefficient = float(coeff.replace(',', '.'))
        if coefficient < 1.26:
            return 2
        
        translate = []
        count = 126
        for score in range(3, 20):
            interval = [i / 100 for i in range(count, count + 50)]
            if coefficient in interval:
                return score
            translate.append(interval)
            count += 50
        else:
            if coefficient >= 9.76:
                return 20
            

    def get_cell_add_score(self,
                  nickname: str,
                  score: int,
                  tourn_type: str,
                  tournament: str) -> str and int:
        # get the cell for the update score of the participant in the table
        participants = self.worksheet.col_values(
            self.cells.index(self._get_column("nickname", tourn_type)) + 1
        )
        last_row = len(participants)
        cells_range = f"{self._get_column('nickname', tourn_type)}3:" \
                      f"{self._get_column('tourn_type', tourn_type)}{last_row}"
        data = self.worksheet.get(cells_range)

        for item in data:
            if item[0] == nickname and item[-1] == tournament:
                old_scores = int(item[1]) 
                row = data.index(item) + 3
                return f"{self._get_column('score', tourn_type)}{row}", old_scores + score


    def update_rating(self):
        # update the sheet with the raiting of the participants'
        cells = string.ascii_uppercase

        for type_ in self.tournament_types:
            first_column = self._get_column("nickname", type_)
            last_row = len(self.worksheet.col_values(self.cells.index(first_column) + 1))
            cells_range = f'{first_column}3:' \
                          f'{self._get_column("tourn_type", type_)}{last_row}'
            
            self.worksheet.sort(
                (cells.index(self._get_column("tourn_type", type_)) + 1, 'des'),
                (cells.index(self._get_column("score", type_)) + 1, 'des'),
                range=cells_range
            )


        
