from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.schemas.email import EmailModel
from app.utils.mail import create_message, mail

router = APIRouter()


@router.get("/")
async def index():
    """
    ELB 상태 체크용 API
    :return:
    """
    current_time = datetime.now()  # + timedelta(hours=9)
    return Response(f"Notification API (KST {current_time.strftime('%Y-%m-%d %H:%M:%S')})")


@router.get("/lifecheck")
async def read_root(request: Request):
    print(request.state.__dict__)

    return {"Hello": "World"}


@router.post("/send_email")
async def simple_send(email: EmailModel) -> JSONResponse:
    emails = email.address
    html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """

    message = create_message(subject="Fastapi-Mail module", recipients=emails, body=html)

    await mail.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
