from fastapi import APIRouter, Response
import pandas as pd
from io import BytesIO

router = APIRouter(
    prefix="/excel",
    tags=["excel"],
    responses={404: {"description": "Not found"}},
)

@router.get("/download-test")
async def download_excel():
    test_data = [
        {"name": "Joona", "goals": 3},
        {"name": "Tero", "goals": 69}
    ]

    df = pd.DataFrame(test_data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Stats")

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stats.xlsx"}
    )