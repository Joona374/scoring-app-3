from collections import defaultdict
from email.policy import default
from io import BytesIO
from openpyxl import Workbook, load_workbook
from db.models import TeamStatsTag
from routes.excel.team_stats.constants import CHANCE_ROW_MAPPING, FINAL_COLUMNS, VALUE_TO_CHANCE_COLUMN, RESULT_TO_SHIFT_MAP
from routes.excel.excel_utils import sanitize_opponent_name, workbook_to_bytesio


def get_chance_row(scoring_chance: TeamStatsTag):
    """
    Retrieves the corresponding row value from CHANCE_ROW_MAPPING based on the first non-None attribute
    found in the scoring_chance object.

    Args:
        scoring_chance (TeamStatsTag): An object containing team statistics attributes that correspond
            to keys in CHANCE_ROW_MAPPING.

    Returns:
        The mapped row value from CHANCE_ROW_MAPPING[row_name][value] for the first matching attribute.

    Raises:
        ValueError: If an exception occurs during attribute retrieval or mapping, with a message
            including the original exception and the scoring_chance object.
    """

    try:
        for row_name in CHANCE_ROW_MAPPING.keys():
            value = getattr(scoring_chance, row_name, None)
            if value:
                return CHANCE_ROW_MAPPING[row_name][value]
    except Exception as e:
        raise ValueError(f"In get_chance_row: {str(e)}", scoring_chance)  # fmt: skip


def get_chance_column(scoring_chance: TeamStatsTag) -> str:
    """
    Retrieves the chance column string based on the scoring chance attributes.
    This function iterates through FINAL_COLUMNS, checks for truthy values in the
    scoring_chance object, and maps the single found value to a chance column using
    VALUE_TO_CHANCE_COLUMN. It ensures exactly one attribute is set.
    Args:
        scoring_chance (TeamStatsTag): The team stats tag object containing attributes
            to check against FINAL_COLUMNS.
    Returns:
        str: The corresponding chance column string from VALUE_TO_CHANCE_COLUMN.
    Raises:
        RuntimeError: If no attributes are found or if multiple attributes are set.
    """

    found = []

    for attr in FINAL_COLUMNS:
        value = getattr(scoring_chance, attr, None)
        if value:
            found.append((attr, value))

    if not found:
        raise RuntimeError(...)

    if len(found) > 1:
        raise RuntimeError(f"Multiple chance columns set: {found}")

    value = found[0][1]
    return VALUE_TO_CHANCE_COLUMN[value]


def get_result_column_shifter(scoring_chance: TeamStatsTag):
    """
    Shifts the column position based on the outcome of the scoring chance.
    The column (decided by get_chance_column) is shifted depending on the outcome of the scoring chance,
    as determined by the play_result attribute of the scoring_chance.
    Args:
        scoring_chance (TeamStatsTag): The scoring chance object containing the play_result.
    Returns:
        int: The shift value for the column position.
    Raises:
        ValueError: If the play_result is invalid or not found in RESULT_TO_SHIFT_MAP.
    """


    shift = RESULT_TO_SHIFT_MAP.get(scoring_chance.play_result, None)

    if shift == None:
        raise ValueError("Invalid play_result in scoring_chance", scoring_chance)
    
    return shift


def calculate_numbers_for_cells(all_tags):
    """
    Calculate the number of occurrences for each shifted cell based on tags.
    Args:
        all_tags: List of tags to process.
    Returns:
        dict: Dictionary with cell keys (e.g., 'A1') and their occurrence counts.
    """

    cell_values = {}
    for tag in all_tags:
        row = get_chance_row(tag)
        col = get_chance_column(tag)
        col_shift = get_result_column_shifter(tag)
        shifted_col = chr(ord(col) + col_shift)

        if f"{shifted_col}{row}" in cell_values:
            cell_values[f"{shifted_col}{row}"] += 1
        else:
            cell_values[f"{shifted_col}{row}"] = 1

    return cell_values


def write_total_sheet(all_tags: list[TeamStatsTag], workbook: Workbook) -> None:
    """
    Writes a total statistics sheet to the given workbook.
    This function creates a new worksheet by copying the first worksheet in the workbook,
    renames it to "TOTAL STATS", calculates the total values for each cell based on the
    provided list of TeamStatsTag objects, and populates the sheet with these integer values.
    Args:
        all_tags (list[TeamStatsTag]): A list of TeamStatsTag objects containing the data
            to calculate totals from.
        workbook (Workbook): The openpyxl Workbook object to which the total sheet will be added.
    Returns:
        None: This function modifies the workbook in place and does not return a value.
    """

    team_stats_sheet = workbook.worksheets[0]

    total_sheet = workbook.copy_worksheet(team_stats_sheet)
    total_sheet.title = "TOTAL STATS"
    cell_values = calculate_numbers_for_cells(all_tags)
    for cell, value in cell_values.items():
        total_sheet[cell] = int(value)


def write_game_sheets(games_stats_dict: defaultdict[int, list[TeamStatsTag]], workbook: Workbook) -> None:
    """
    Writes individual game sheets to the workbook based on the provided game statistics.
    This function iterates over the games_stats_dict, where each entry corresponds to a game.
    For each game, it creates a copy of the first worksheet (team_stats_sheet), sets the sheet title
    to include the sanitized opponent name and game date, calculates the cell values from the
    TeamStatsTag list, and populates the sheet with integer values.
    Args:
        games_stats_dict (defaultdict[int, list[TeamStatsTag]]): A dictionary mapping game IDs to lists of TeamStatsTag objects.
        workbook (Workbook): The openpyxl Workbook object to which the game sheets will be added.
    Returns:
        None: This function does not return any value; it modifies the workbook in place.
    """

    team_stats_sheet = workbook.worksheets[0]

    # Write sheets for individual games
    for _, tags_list in games_stats_dict.items():
        game_object = tags_list[0].game
        game_sheet = workbook.copy_worksheet(team_stats_sheet)

        opponent_name = sanitize_opponent_name(game_object.opponent)
        game_sheet.title = f"{opponent_name} {game_object.date}"

        cell_values_for_game = calculate_numbers_for_cells(tags_list)
        for cell, value in cell_values_for_game.items():
            game_sheet[cell] = int(value)


def build_team_stats_workbook(all_tags: list[TeamStatsTag], games_stats_dict: defaultdict[int, list[TeamStatsTag]]) -> BytesIO:
    """
    Builds an Excel workbook containing team statistics by loading a template, writing total stats and per-game stats,
    removing the template sheet, and returning the workbook as a BytesIO object.
    Args:
        all_tags (list[TeamStatsTag]): A list of TeamStatsTag objects representing the total statistics to be written.
        games_stats_dict (defaultdict[int, list[TeamStatsTag]]): A dictionary where keys are game identifiers (int) and
            values are lists of TeamStatsTag objects for per-game statistics.
    Returns:
        BytesIO: A BytesIO object containing the generated Excel workbook with team stats.
    """

    # 1. Load the excel workbook
    workbook = load_workbook("excels/team_stats_template.xlsx")

    # 2. Write the totals stats to the workbook (edits workbook in place)
    write_total_sheet(all_tags, workbook)

    # 3. Write the per game stats on separate sheets to the workbook (edits workbook in place)
    write_game_sheets(games_stats_dict, workbook)

    # 4. Delete template sheet
    workbook.remove(workbook.worksheets[0])

    # 5. Convert the workbook to a BytesIO object to return
    output = workbook_to_bytesio(workbook)

    return output
