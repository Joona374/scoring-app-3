import tempfile
from PIL import Image, ImageDraw
from routes.excel.stats_utils import MapCategories
from db.models import ShotResultTypes


def draw_x(img_draw: ImageDraw.ImageDraw, x: int, y: int, color: str, size: int = 12, thicknes: int = 7) -> None:
    """
    Draws a X marker on a image (for goal)
    """
    img_draw.line((x - size, y - size, x + size, y + size), fill=color, width=thicknes)
    img_draw.line((x - size, y + size, x + size, y - size), fill=color, width=thicknes)


def draw_o(img_draw: ImageDraw.ImageDraw, x: int, y: int, color: str, r: int = 10, width: int = 5):
    """
    Draws a X marker on a image (for a scoring chance)
    """
    img_draw.ellipse((x - r, y - r, x + r, y + r), outline=color, width=width)


def draw_map_image(goals: list[tuple[int, int]], chances: list[tuple[int, int]], img_path: str, color: str) -> Image.Image:
    """
    Draws markers on a map image for goals and chances.
    Args:
        goals (list[tuple[int, int]]): List of (x, y) coordinates for goals.
        chances (list[tuple[int, int]]): List of (x, y) coordinates for chances.
        img_path (str): Path to the template image file.
        color (str): Color for the markers.
    Returns:
        Image.Image: The modified image with markers drawn.
    """

    with Image.open(img_path) as img:
        img = img.copy().convert("RGB")
    draw = ImageDraw.Draw(img)

    x_scale = img.width / 100
    y_scale = img.height / 100

    # Remove to avoid drawing duplicates
    for goal in goals:
        if goal in chances:
            chances.remove(goal)

    for chance in chances:
        px = int(round(chance[0] * x_scale))
        py = int(round(chance[1] * y_scale))
        draw_o(draw, px, py, color)

    for goal in goals:
        px = int(round(goal[0] * x_scale))
        py = int(round(goal[1] * y_scale))
        draw_x(draw, px, py, "black")

    return img


def get_map_images(coords: dict) -> dict[str, Image.Image]:
    """
    Generates map images for goals and chances for and against, on net and ice.
    Args:
        coords (dict): Coordinates for shots, categorized by result and map category.
    Returns:
        dict[str, Image.Image]: Dictionary with keys 'net_for', 'ice_for', 'net_vs', 'ice_vs' containing the generated images.
    """

    NET_IMG = "excels/images/maali.jpg"
    ICE_IMG = "excels/images/kaukalo.png"

    net_for_img = draw_map_image(
        goals=coords[ShotResultTypes.GOAL_FOR][MapCategories.NET], 
        chances=coords[ShotResultTypes.CHANCE_FOR][MapCategories.NET],
        img_path= NET_IMG, 
        color="green") # fmt: skip

    ice_for_img = draw_map_image(
        goals=coords[ShotResultTypes.GOAL_FOR][MapCategories.ICE], 
        chances=coords[ShotResultTypes.CHANCE_FOR][MapCategories.ICE],
        img_path= ICE_IMG, 
        color="green") # fmt: skip

    net_vs_img = draw_map_image(
        goals=coords[ShotResultTypes.GOAL_AGAINST][MapCategories.NET], 
        chances=coords[ShotResultTypes.CHANCE_AGAINST][MapCategories.NET],
        img_path= NET_IMG, 
        color="red") # fmt: skip

    ice_vs_img = draw_map_image(
        goals=coords[ShotResultTypes.GOAL_AGAINST][MapCategories.ICE], 
        chances=coords[ShotResultTypes.CHANCE_AGAINST][MapCategories.ICE],
        img_path= ICE_IMG, 
        color="red") # fmt: skip

    return {"net_for": net_for_img, "ice_for": ice_for_img, "net_vs": net_vs_img, "ice_vs": ice_vs_img}


def scale_image(img: Image.Image, scale: float) -> Image.Image:
    """
    Scales an image by a given factor using high-quality Lanczos resampling.
    Args:
        img (Image.Image): The input PIL Image object to be scaled.
        scale (float): The scaling factor. Values greater than 1.0 enlarge the image, 
                       while values less than 1.0 shrink it. Must be positive.
    Returns:
        Image.Image: A new PIL Image object representing the scaled image.
    """

    new_width = int(round(img.width * scale))
    new_height = int(round(img.height * scale))
    scaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return scaled_img
