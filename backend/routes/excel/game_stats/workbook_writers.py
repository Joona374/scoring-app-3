import tempfile
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.drawing.image import Image as EXCLImage
from PIL import Image

from routes.excel.stats_utils import STATS_CELL_VALUES, STATS_MAP_COORDINATES
from routes.excel.image_utils import get_map_images, scale_image


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


def add_images_to_sheet(sheet: Worksheet, map_images: dict[str, Image.Image]):
    """
    Adds scaled images to a worksheet at predefined cell positions based on a configuration dictionary.
    This function processes a dictionary of PIL Image objects, scales each image according to the
    specified scale factor, saves them temporarily as PNG files, and inserts them into the worksheet
    at the designated cell locations. The configuration is hardcoded for specific image names.
    Parameters:
    - sheet (Worksheet): The openpyxl worksheet object where the images will be added.
    - map_images (dict[str, Image.Image]): A dictionary mapping image names (e.g., "net_for", "ice_for")
      to PIL Image objects that will be added to the sheet.
    The image configuration includes:
    - "net_for": Scaled to 0.81 and placed at cell "T20".
    - "ice_for": Scaled to 0.73 and placed at cell "T34".
    - "net_vs": Scaled to 0.81 and placed at cell "Y20".
    - "ice_vs": Scaled to 0.73 and placed at cell "Y34".
    Note: Temporary PNG files are created and not automatically deleted (delete=False in NamedTemporaryFile).
    Ensure proper cleanup to avoid accumulating temporary files.
    """

    image_config = {
        "net_for": {"scale": 0.81, "cell": "T20"}, 
        "ice_for": {"scale": 0.73, "cell": "T34"},
        "net_vs": {"scale": 0.81, "cell": "Y20"}, 
        "ice_vs": {"scale": 0.73, "cell": "Y34"}} # fmt: skip

    for img_name, config in image_config.items():
        img = map_images[img_name]
        scaled_img = scale_image(img, config["scale"])

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            scaled_img.save(tmp_img.name)
            excl_img = EXCLImage(tmp_img.name)

        sheet.add_image(excl_img, config["cell"])


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
