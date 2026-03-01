from collections import defaultdict
from io import BytesIO
import tempfile
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.drawing.image import Image as EXCLImage
from openpyxl import load_workbook
from PIL import Image

from routes.excel.excel_utils import workbook_to_bytesio
from routes.excel.stats_utils import STATS_CELL_VALUES, STATS_MAP_COORDINATES, STATS_PER_GAME_STATS
from routes.excel.player_stats.player_stats_utils import PlayerStats
from routes.excel.image_utils import get_map_images, scale_image


def sort_players_by_last_name(unsroted_players: defaultdict[int, PlayerStats]) -> dict[int, PlayerStats]:
    return dict(sorted(unsroted_players.items(), key=lambda item: item[1]["last_name"]))


def write_name_to_sheet(player_data: PlayerStats, sheet: Worksheet) -> None:
    sheet.title = f"{player_data["last_name"].upper()} {player_data["first_name"]}"


def write_data_to_cells(player_data: PlayerStats, sheet: Worksheet) -> None:
    for cell, value in player_data[STATS_CELL_VALUES].items():
        sheet[cell] = value


def write_game_summaries_to_sheet(player_data: PlayerStats, sheet: Worksheet):
    FIRST_GAME_STAST_ROW = 54

    for i, game in enumerate(player_data[STATS_PER_GAME_STATS]):
        row = FIRST_GAME_STAST_ROW + i
        for col, value in game.items():
            if col == "date":
                continue
            cell = f"{col}{row}"
            sheet[cell] = value


def add_images_to_sheet(map_images: dict[str, Image.Image], sheet: Worksheet):
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
        "net_for": {"scale": 0.81, "cell": "S19"},
        "ice_for": {"scale": 0.73, "cell": "S31"},
    }

    for img_name, config in image_config.items():
        img = map_images[img_name]
        scaled_img = scale_image(img, config["scale"])

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            scaled_img.save(tmp_img.name)
            excl_img = EXCLImage(tmp_img.name)

        sheet.add_image(excl_img, config["cell"])


def write_players_sheet(sheet: Worksheet, player_data: PlayerStats):

    write_name_to_sheet(player_data, sheet)
    write_data_to_cells(player_data, sheet)
    write_game_summaries_to_sheet(player_data, sheet)
    map_images = get_map_images(player_data[STATS_MAP_COORDINATES])
    add_images_to_sheet(map_images, sheet)


def write_player_sheets(workbook: Workbook, players_to_analyze: defaultdict[int, PlayerStats]) -> None:

    template_sheet = workbook.worksheets[0]
    sorted_players = sort_players_by_last_name(players_to_analyze)

    for _, player_data in sorted_players.items():
        player_sheet = workbook.copy_worksheet(template_sheet)
        write_players_sheet(player_sheet, player_data)

    # Delete template sheet
    workbook.remove(workbook.worksheets[0])


def build_player_stats_workbook(players_to_analyze: defaultdict[int, PlayerStats]) -> BytesIO:
    """
    Builds an Excel workbook with player statistics.
    Loads a template workbook, writes individual player stats sheets,
    and returns the workbook as a BytesIO object.
    Args:
        players_to_analyze (defaultdict[int, PlayerStats]): Dictionary of player stats keyed by player ID.
    Returns:
        BytesIO: The generated Excel workbook as a BytesIO object.
    """

    # 1. Create the excel file
    workbook = load_workbook("excels/players_summary_template.xlsx")

    # 2. Create + write a sheet with stats for each player
    write_player_sheets(workbook, players_to_analyze)

    # 3. Convert the workbook to a BytesIO object to return
    output = workbook_to_bytesio(workbook)

    return output
