from io import BytesIO
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from routes.excel.excel_utils import workbook_to_bytesio
from routes.excel.excel_utils import sanitize_opponent_name, workbook_to_bytesio
from routes.excel.player_plus_minus.constants import FIRST_DEFENDER_ROW, FIRST_FORWARD_ROW, NAME_COLUMNS, RESULT_TO_COLUMN_MAP, GameDataStructure, PlayerData


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


def write_totals_sheet(total_stats, workbook: Workbook):
    total_sheet = copy_template_sheet(workbook, sheet_title="YHTEENSÄ")

    for i, defender in enumerate(total_stats["defenders"]):
        row = FIRST_DEFENDER_ROW + i
        for name_col in NAME_COLUMNS:
            total_sheet[f"{name_col}{row}"] = defender["name"]
        for key, value in defender["stats"].items():
            column = RESULT_TO_COLUMN_MAP[key]
            total_sheet[f"{column}{row}"] = value

    for i, forward in enumerate(total_stats["forwards"]):
        row = FIRST_FORWARD_ROW + i
        for name_col in NAME_COLUMNS:
            total_sheet[f"{name_col}{row}"] = forward["name"]
        for key, value in forward["stats"].items():
            column = RESULT_TO_COLUMN_MAP[key]
            total_sheet[f"{column}{row}"] = value


def write_avg_sheet(total_stats, workbook: Workbook):
    total_avg_sheet = copy_template_sheet(workbook, sheet_title="KESKIARVOT")

    for i, defender in enumerate(total_stats["defenders"]):
        row = FIRST_DEFENDER_ROW + i
        games_played = defender["GP"]
        for name_col in NAME_COLUMNS:
            total_avg_sheet[f"{name_col}{row}"] = defender["name"]
        for key, value in defender["stats"].items():
            column = RESULT_TO_COLUMN_MAP[key]
            total_avg_sheet[f"{column}{row}"] = value / games_played

    for i, forward in enumerate(total_stats["forwards"]):
        games_played = forward["GP"]
        row = FIRST_FORWARD_ROW + i
        for name_col in NAME_COLUMNS:
            total_avg_sheet[f"{name_col}{row}"] = forward["name"]
        for key, value in forward["stats"].items():
            column = RESULT_TO_COLUMN_MAP[key]
            total_avg_sheet[f"{column}{row}"] = value / games_played


def write_game_sheet(game: GameDataStructure, workbook: Workbook):
    """
    Writes game data to a new sheet in the provided workbook.
    Creates a new sheet with a title based on the opponent name and game date,
    copies a template sheet, and populates it with player statistics for defenders
    and forwards. For each player, their name is written to specified name columns,
    and their stats are mapped to corresponding columns using RESULT_TO_COLUMN_MAP.
    Args:
        game (GameDataStructure): A dictionary-like object containing game data,
            including opponent, date, and roster organized by positions with player
            names and stats.
        workbook (Workbook): The openpyxl Workbook object to which the new sheet
            will be added.
    Returns:
        None: This function modifies the workbook in place and does not return a value.
    """

    sheet_title = f"{sanitize_opponent_name(game["opponent"])} {game['date']}"
    game_sheet = copy_template_sheet(workbook, sheet_title=sheet_title)

    for i, defender in enumerate(game["roster_by_positions"]["defenders"]):
        row = FIRST_DEFENDER_ROW + i
        for name_col in NAME_COLUMNS:
            game_sheet[f"{name_col}{row}"] = defender["name"]
        for key, value in defender["stats"].items():
            column = RESULT_TO_COLUMN_MAP[key]
            game_sheet[f"{column}{row}"] = value

    for i, forward in enumerate(game["roster_by_positions"]["forwards"]):
        row = FIRST_FORWARD_ROW + i
        for name_col in NAME_COLUMNS:
            game_sheet[f"{name_col}{row}"] = forward["name"]
        for key, value in forward["stats"].items():
            column = RESULT_TO_COLUMN_MAP[key]
            game_sheet[f"{column}{row}"] = value


def write_game_sheets(data_for_games: list[GameDataStructure], workbook: Workbook):
    """
    Writes game sheets to the workbook for each game in the provided data.
    Args:
        data_for_games (list[GameDataStructure]): List of game data structures.
        workbook (Workbook): The workbook to write to.
    """

    for game in data_for_games:
        write_game_sheet(game, workbook)


def build_plusminus_workbook(total_stats: dict[int, PlayerData], data_for_games: list[GameDataStructure]) -> BytesIO:
    """
    Builds a plus-minus workbook by loading a template Excel file, populating it with total stats, average stats, and individual game sheets, then removing the template sheet and returning the workbook as a BytesIO object.
    Args:
        total_stats (dict[int, PlayerData]): A dictionary mapping player IDs to their total statistics data.
        data_for_games (list[GameDataStructure]): A list of game data structures, each containing information for a specific game.
    Returns:
        BytesIO: A BytesIO object containing the generated Excel workbook.
    """

    # 1. Load the excel file into a workbook object
    workbook = load_workbook("excels/plus_minus_template.xlsx")

    # 2. Write the total sheet (edits workbook in place)
    write_totals_sheet(total_stats, workbook)

    # 3. Write the avg sheet aka totals / games played (edits workbook in place)
    write_avg_sheet(total_stats, workbook)

    # 4. Write separate sheet for each game (edits workbook in place)
    write_game_sheets(data_for_games, workbook)

    # 5. Delete the empty template sheet from the workbook
    workbook.remove(workbook.worksheets[0])

    # 6. Convert the workbook to a BytesIO object to return
    output = workbook_to_bytesio(workbook)

    return output
