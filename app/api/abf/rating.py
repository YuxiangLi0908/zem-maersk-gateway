"""ABF rating adapter placeholder."""

from fastapi import HTTPException, status


async def get_rating(*_args, **_kwargs):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ABF询价接口尚未配置",
    )

