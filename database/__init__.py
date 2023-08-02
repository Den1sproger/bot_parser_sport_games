from .db_work import Database, Database_Thread
from .db_config import TOURNAMENT_TYPES


PROMPT_VIEW_USERS = "SELECT chat_id FROM users;"
PROMPT_VIEW_LAST_SCORES = "SELECT nickname, all_scores FROM users;"


def get_prompt_view_games(tourn_type: str) -> str:
    return "SELECT game_key, sport, begin_time, first_team, first_coeff, second_team," \
        f"second_coeff, draw_coeff, url FROM games WHERE game_status=1 AND tourn_type='{tourn_type}';"


def get_prompt_view_games_id(tourn_type: str = None) -> str:
    if tourn_type:
        return f"SELECT game_key FROM games WHERE game_status<>3 AND tourn_type='{tourn_type}';"
    else:
        return f"SELECT game_key FROM games WHERE game_status<>3;"


def get_prompt_view_nicknames_by_tourn_type(tourn_type: str) -> str:
    return f"SELECT nickname FROM participants WHERE tournament LIKE '%{tourn_type.capitalize()}%';"


def get_prompt_delete_games(tourn_type: str) -> str:
    return f"DELETE FROM games WHERE tourn_type='{tourn_type}';"


def get_prompt_delete_answers(tourn_type: str) -> str:
    return f"DELETE FROM answers WHERE tournament LIKE '%{tourn_type.upper()}%';"


def get_prompt_delete_rating(tourn_type: str) -> str:
    return f"DELETE FROM participants WHERE tournament LIKE '%{tourn_type.upper()}%';"


def get_prompt_view_rating(tourn_name: str) -> str:
    return f"SELECT nickname, scores FROM participants WHERE tournament='{tourn_name}' ORDER BY scores DESC;"


def get_prompt_view_nicknames_by_tourn(tourn_name: str) -> str:
    return f"SELECT nickname FROM participants WHERE tournament='{tourn_name}';"


def get_prompt_add_user(username: str,
                        chat_id: str,
                        nickname: str) -> str:
    return f"INSERT INTO users (username, chat_id, nickname, all_scores)" \
           f"VALUES ('{username}', '{chat_id}', '{nickname}', 0);"


def get_prompt_register_participant(nickname: str,
                                    tournament: str) -> str:
    return f"INSERT INTO participants (nickname, tournament, scores) VALUES ('{nickname}', '{tournament}', 0);"


def get_prompt_add_scores(adding_scores: int,
                          nickname: str,
                          tournament: str) -> list[str]:
    return [f"UPDATE participants SET scores=scores+{adding_scores} WHERE nickname='{nickname}' AND tournament='{tournament}';",
           f"UPDATE users SET all_scores=all_scores+{adding_scores} WHERE nickname='{nickname}';"]


def get_prompt_add_game(game_key: str,
                        sport: str,
                        begin_time: str,
                        coeffs: dict[str],
                        url: str,
                        tourn_type: str) -> str:
    keys = list(coeffs.keys())
    team_1 = keys[0]
    team_2 = keys[1]
    coeff_1 = coeffs[team_1]
    coeff_2 = coeffs[team_2]
    
    try: draw_coeff = coeffs['Ничья']
    except KeyError:
        return f"INSERT INTO games (game_key, sport, begin_time, first_team, first_coeff, second_team, second_coeff," \
            f" url, game_status, tourn_type) VALUES ('{game_key}', '{sport}', '{begin_time}'," \
            f" '{team_1}', '{coeff_1}', '{team_2}', '{coeff_2}', '{url}', 1, '{tourn_type}');"
    else:
        return f"INSERT INTO games (game_key, sport, begin_time, first_team, first_coeff, second_team, second_coeff," \
            f" draw_coeff, url, game_status, tourn_type) VALUES ('{game_key}', '{sport}', '{begin_time}'," \
            f" '{team_1}', '{coeff_1}', '{team_2}', '{coeff_2}', '{draw_coeff}', '{url}', 1, '{tourn_type}');"


def get_prompt_update_status(game_key: str,
                             status: int) -> str:
    return f"UPDATE games SET game_status={status} WHERE game_key='{game_key}';"


def get_prompt_view_users_by_answer(game_key: str,
                                    tournament: str) -> str:
    return f"SELECT chat_id, answer, tournament FROM answers WHERE game_key='{game_key}'" \
           f" AND tournament LIKE '%{tournament.lower()}%';"


def get_prompt_view_game_coeffs(game_key: str) -> str:
    return f"SELECT first_coeff, second_coeff, draw_coeff FROM games WHERE game_key='{game_key}';"


def get_prompt_view_username_by_id(chat_id: str) -> str:
    return f"SELECT username FROM users WHERE chat_id='{chat_id}';"


def get_prompt_view_chat_id_by_nick(nickname: str) -> str:
    return f"SELECT chat_id FROM users WHERE nickname='{nickname}';"


def get_prompt_view_nick_by_id(chat_id: str) -> str:
    return f"SELECT nickname FROM users WHERE chat_id='{chat_id}';"


__all__ = [
    'Database',
    'Database_Thread',
    'TOURNAMENT_TYPES',
    'PROMPT_VIEW_USERS',
    'PROMPT_VIEW_LAST_SCORES',
    'get_prompt_view_nicknames_by_tourn',
    'get_prompt_view_rating',
    'get_prompt_delete_games',
    'get_prompt_view_games',
    'get_prompt_view_games_id',
    'get_prompt_add_user',
    'get_prompt_register_participant',
    'get_prompt_add_scores',
    'get_prompt_add_game',
    'get_prompt_update_status',
    'get_prompt_view_username_by_id',
    'get_prompt_view_nick_by_id',
    'get_prompt_view_chat_id_by_nick',
    'get_prompt_view_game_coeffs',
    'get_prompt_delete_rating',
    'get_prompt_delete_answers',
    'get_prompt_view_nicknames_by_tourn_type'
]
