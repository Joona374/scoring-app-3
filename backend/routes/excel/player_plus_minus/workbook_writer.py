from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from db.models import Game, Positions
from routes.excel.player_plus_minus.plus_minus_domain import FIRST_DEFENDER_ROW, FIRST_FORWARD_ROW, NAME_COLUMNS, PlusMinusPlayer
from routes.excel.excel_utils import sanitize_opponent_name, workbook_to_bytesio
from routes.excel.player_plus_minus.plus_minus_utils import (
    format_player_name,
    get_column_for_stat,
    get_players_in_game,
    should_skip_goalie,
)


def copy_template_sheet(workbook: Workbook, sheet_title: str | None = None, idx: int = 0) -> Worksheet:
    """
    Copies a template sheet from the workbook and optionally sets its title.
    Args:
        workbook (Workbook): The workbook containing the sheets.
        sheet_title (str | None): Optional title for the copied sheet. Defaults to None.
        idx (int): Index of the template sheet to copy. Defaults to 0.
    Returns:
        None
    """

    template_sheet = workbook.worksheets[idx]
    new_sheet = workbook.copy_worksheet(template_sheet)

    if sheet_title:
        new_sheet.title = sheet_title

    return new_sheet


def add_player_to_total_sheets(player: PlusMinusPlayer, players: list[PlusMinusPlayer], total_sheet: Worksheet, avg_sheet: Worksheet, current_rows: dict[Positions, int]):
    """Write player's total and average stats to the summary sheets."""
    # Write the name of the player to each of the 4 columns
    formated_name = format_player_name(player, players)
    for name_col in NAME_COLUMNS:
        total_sheet[f"{name_col}{current_rows[player.position]}"] = formated_name
        avg_sheet[f"{name_col}{current_rows[player.position]}"] = formated_name

    stats = player.get_total_stats()
    games_played = player.get_games_played()

    for strength, stat1 in stats.items():
        for participation_type, stat2 in stat1.items():
            for result, value in stat2.items():

                # Write the data for each [strength][participation_type][result] combination to both total_sheet and avg_sheet
                column = get_column_for_stat(strength, participation_type, result)
                total_sheet[f"{column}{current_rows[player.position]}"] = value
                avg_sheet[f"{column}{current_rows[player.position]}"] = value / games_played

    current_rows[player.position] += 1


def add_player_to_game_sheet(player: PlusMinusPlayer, players: list[PlusMinusPlayer], game: Game, sheet: Worksheet, current_rows: dict[Positions, int]):
    """Write player's stats for a specific game to the game sheet."""
    # Write the name of the player to each of the 4 columns
    formated_name = format_player_name(player, players)
    for name_col in NAME_COLUMNS:
        sheet[f"{name_col}{current_rows[player.position]}"] = formated_name

    stats = player.get_game_stats(game.id)

    for strength, stat1 in stats.items():
        for participation_type, stat2 in stat1.items():
            for result, value in stat2.items():

                # Write the data for each [strength][participation_type][result] combination to the sheet
                column = get_column_for_stat(strength, participation_type, result)
                row = current_rows[player.position]
                sheet[f"{column}{row}"] = value

    current_rows[player.position] += 1


def write_total_sheets(players: dict[int, PlusMinusPlayer], workbook: Workbook):
    """Create and populate total and average total sheets."""
    total_sheet = copy_template_sheet(workbook, sheet_title="YHTEENSÄ")
    avg_sheet = copy_template_sheet(workbook, sheet_title="KA. YHTEENSÄ")
    current_rows = {Positions.DEFENDER: FIRST_DEFENDER_ROW, Positions.FORWARD: FIRST_FORWARD_ROW}

    for player in sorted(players.values(), key=lambda p: p.last_name):
        if should_skip_goalie(player):
            continue

        # Edits total_sheet and avg_sheet
        add_player_to_total_sheets(player=player, players=list(players.values()), total_sheet=total_sheet, avg_sheet=avg_sheet, current_rows=current_rows)


def write_game_sheets(games: list[Game], players: dict[int, PlusMinusPlayer], workbook: Workbook):
    """Create a separate sheet for each game with player stats."""
    for game in games:
        sheet_title = f"{sanitize_opponent_name(game.opponent)} {game.date}"
        game_sheet = copy_template_sheet(workbook, sheet_title=sheet_title)

        players_in_game = get_players_in_game(game, players)
        current_rows = {Positions.DEFENDER: FIRST_DEFENDER_ROW, Positions.FORWARD: FIRST_FORWARD_ROW}

        for player in players_in_game:
            if should_skip_goalie(player):
                continue

            add_player_to_game_sheet(player, players_in_game, game, game_sheet, current_rows)


def build_workbook(players: dict[int, PlusMinusPlayer], games: list[Game]):
    """Build complete Excel workbook with total and per-game sheets."""
    # 1. Load the excel file into a workbook object
    workbook = load_workbook("excels/plus_minus_template.xlsx")

    # 2. Write the total and total avg sheet (edits workbook in place)
    write_total_sheets(players, workbook)

    # 3. Write a separate sheet for each game (edits workbook in place)
    write_game_sheets(games, players, workbook)

    # 4. Delete the empty template sheet from the workbook
    workbook.remove(workbook.worksheets[0])

    # 5. Convert the workbook to a BytesIO object to return
    output = workbook_to_bytesio(workbook)

    return output
