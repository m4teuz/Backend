import time
from ... import logger
from typing import Any, Dict
from httpx import AsyncClient
from fastapi import APIRouter, Path
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/assets",
    # dependencies=[Depends(get_token_header)],
    responses={404: {"message": "Are you lost?", "ok": False}},
    tags=['internals'],
)

client = AsyncClient()

@router.get("/image/{quality}/{filename}", response_model=Dict[str, Any], status_code=200)
async def image_path(quality: str = Path(..., title="Quality for the requesting image"), filename: str =  Path(..., title="Filename for the requesting image")):
    path = f"https://image.tmdb.org/t/p/{quality}/{filename}"
    req = client.build_request("GET", path)
    r = await client.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(),
        background=BackgroundTask(r.aclose),
        headers=r.headers
    )

@router.get("/thumbnail/{file_id}", response_model=Dict[str, Any], status_code=200)
async def image_path(file_id: str = Path(title:="File ID of the thumbnail that needs to be generated")):
    from main import drive
    if not drive:
        return {"ok": False, "message": "Drive is not initialized"}
    start = time.perf_counter()
    thumb_url = drive.get_thumbnail_url(file_id)
    if not thumb_url:
        return {"ok": False, "message": "Thumbnail not found"}
    print(f"Thumbnail URL: {thumb_url}")
    req = client.build_request("GET", thumb_url)
    r = await client.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(),
        background=BackgroundTask(r.aclose),
        headers=r.headers
    )