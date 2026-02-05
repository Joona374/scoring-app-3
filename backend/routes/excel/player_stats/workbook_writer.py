from collections import defaultdict
from openpyxl import Workbook

from routes.excel.player_stats.player_stats_utils import PlayerStats


def write_player_sheets(workbook: Workbook, players_to_analyze: defaultdict[int, PlayerStats]) -> None:
    FIRST_GAME_STAST_ROW = 54

    template_sheet = workbook.worksheets[0]
    sorted_players = dict(sorted(players_to_analyze.items(), key=lambda item: item[1]["last_name"]))

    for _, player_data in sorted_players.items():
        game_sheet = workbook.copy_worksheet(template_sheet)
        game_sheet.title = f"{player_data["last_name"].upper()} {player_data["first_name"]}"

        for cell, value in player_data["cell_values"].items():
            game_sheet[cell] = value

        for i, game in enumerate(player_data["per_game_stats"]):
            row = FIRST_GAME_STAST_ROW + i
            for col, value in game.items():
                if col == "date":
                    continue
                cell = f"{col}{row}"
                game_sheet[cell] = value

        # Delete template sheet
    workbook.remove(workbook.worksheets[0])
