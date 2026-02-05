from io import BytesIO
from openpyxl import Workbook

from db.models import PlayerStatsTag, ShotResultTypes

def workbook_to_bytesio(workbook: Workbook) -> BytesIO:
    """
    Converts a Workbook object to a BytesIO stream.
    Args:
        workbook (Workbook): The workbook to convert.
    Returns:
        BytesIO: The workbook data as a BytesIO stream.
    """
    
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def get_outcome_cell_adjustment(tag: PlayerStatsTag) -> dict:
    """
    Calculates the adjustment to be made to a cell's row and column based on the outcome of a player's shot.
    Args:
        tag (PlayerStatsTag): An object containing information about the player's shot, including its result type.
    Returns:
        dict: A dictionary with 'row' and 'column' keys indicating the adjustment values to be applied.
    The adjustment is determined as follows:
        - If the shot result is CHANCE_AGAINST: column is incremented by 1.
        - If the shot result is GOAL_FOR: row is incremented by 1.
        - If the shot result is GOAL_AGAINST: both row and column are incremented by 1.
        - For CHANCE_FOR: no adjustment is made (row and column remain 0).
    """

    adjustment = {"row": 0, "column": 0}

    result_type = tag.shot_result.value

    if result_type == ShotResultTypes.CHANCE_AGAINST:
        adjustment["column"] = 1
    elif result_type == ShotResultTypes.GOAL_FOR:
        adjustment["row"] = 1
    elif result_type == ShotResultTypes.GOAL_AGAINST:
        adjustment["column"] = 1
        adjustment["row"] = 1

    return adjustment
