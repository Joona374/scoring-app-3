from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from typing import Any

from routes.excel.game_stats.game_stats_utils import STATS_CELL_VALUES, STATS_MAP_COORDINATES
from routes.excel.game_stats.image_utils import add_images_to_sheet, get_map_images


def write_stats_to_cells(sheet: Worksheet, cell_values: dict):
    for cell, value in cell_values.items():
        sheet[cell] = value


def write_total_sheet_for_game_stats(workbook: Workbook, total_stats: dict[str, dict]):
    total_sheet = workbook.worksheets[1]

    coordinates = total_stats[STATS_MAP_COORDINATES]
    map_images = get_map_images(coordinates)
    add_images_to_sheet(total_sheet, map_images)
    write_stats_to_cells(total_sheet, total_stats[STATS_CELL_VALUES])


def sanitize_opponent_name(name: str) -> str:
    if "/" in name:
        name = name.replace("/", "&")
    return name


def write_game_metadata(game_sheet: Worksheet, game: dict[str, Any]):
    opponent_name = sanitize_opponent_name(game["opponent"])
    game_sheet.title = f"{opponent_name} {game['date']}"

    game_sheet["C1"] = game["date"]
    game_sheet["G1"] = game["opponent"]
    game_sheet["T1"] = game["home"]


def write_per_game_sheets_for_game_stats(workbook: Workbook, per_game_stats: list[dict[str, Any]]):
    template_sheet = workbook.worksheets[0]

    per_game_stats.sort(key=lambda game: game["date"], reverse=True)
    for game in per_game_stats:
        game_sheet = workbook.copy_worksheet(template_sheet)
        write_game_metadata(game_sheet, game)

        coordinates = game[STATS_MAP_COORDINATES]
        map_images = get_map_images(coordinates)
        add_images_to_sheet(game_sheet, map_images)

        write_stats_to_cells(game_sheet, game[STATS_CELL_VALUES])


def create_game_stats_workbook(total_stats: dict[str, dict[str, int]], per_game_stats: list[dict[str, Any]]) -> Workbook:
    workbook = load_workbook("excels/game_stats_template.xlsx")

    write_total_sheet_for_game_stats(workbook, total_stats)
    write_per_game_sheets_for_game_stats(workbook, per_game_stats)

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])

    return workbook
