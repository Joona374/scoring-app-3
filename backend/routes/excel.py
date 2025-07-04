from fastapi import APIRouter, Response
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook, Workbook

router = APIRouter(
    prefix="/excel",
    tags=["excel"],
    responses={404: {"description": "Not found"}},
)

@router.get("/download-test")
async def download_excel():
    workbook = load_workbook("mock_excel.xlsx")
    player_template = workbook.active

    names = ["Pekka", "Tero", "Pasi", "Harri", "Kari"]

    for i in range(5):
        new_sheet = workbook.copy_worksheet(player_template)
        new_sheet.title = names[i]
        new_sheet["B1"] = names[i]
        new_sheet["D1"] = i * 2

    workbook.remove(workbook.worksheets[0])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stats.xlsx"}
    )