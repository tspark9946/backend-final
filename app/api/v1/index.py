from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()


@router.get("/")
async def index():
    """
    ELB 상태 체크용 API
    :return:
    """
    current_time = datetime.now()  # + timedelta(hours=9)
    return Response(
        f"Notification API (KST {current_time.strftime('%Y-%m-%d %H:%M:%S')})"
    )


@router.get("/lifecheck")
async def read_root(request: Request):
    print(request.state.__dict__)

    return {"Hello": "World"}
