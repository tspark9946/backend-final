import base64
import hmac
import time
import re

import jwt
import sqlalchemy.exc

from jwt.exceptions import ExpiredSignatureError, DecodeError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from common.consts import EXCEPT_PATH_LIST, EXCEPT_PATH_REGEX, JWT_SECRET, JWT_ALGORITHM
from common.config import conf
from database.conn import db
from schemas.apikey import ApiKeys
from schemas.sign import User
from models.user import UserToken
from errors import exceptions as ex
from utils.date_utils import D
from utils.logger import api_logger
from utils.query_utils import to_dict

# 들어오는 모든요청에 대한 토큰을 검사하는 미들웨어
# api가 아니라 템플릿을 이용한 렌드링을 위한 endpoint로 접속시 쿠키에서 토큰을 가져오게 해주는 역할을 함

async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    #request.state에 어떤정보든 추가할 수 있음
    # 로그인후 user정보를 넣어놓고 route내 함수호출시 사용자정보등을 사용하면 됨
    request.state.user = None
    request.state.service = None

    ip = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else request.client.host
    request.state.ip = ip.split(",")[0] if "," in ip else ip
    headers = request.headers
    cookies = request.cookies

    url = request.url.path
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url != "/":
            await api_logger(request=request, response=response)
        return response

    try:
        if url.startswith("/api"):
            # api 인경우 헤더로 토큰 검사
            if url.startswith("/api/services"):
                qs = str(request.query_params)
                qs_list = qs.split("&")
                session = next(db.session())
                if not conf().DEBUG:
                    try:
                        qs_dict = {qs_split.split("=")[0]: qs_split.split("=")[1] for qs_split in qs_list}
                    except Exception:
                        raise ex.APIQueryStringEx()

                    qs_keys = qs_dict.keys()

                    if "key" not in qs_keys or "timestamp" not in qs_keys:
                        raise ex.APIQueryStringEx()

                    if "secret" not in headers.keys():
                        raise ex.APIHeaderInvalidEx()

                    api_key = ApiKeys.get(session=session, access_key=qs_dict["key"])

                    if not api_key:
                        raise ex.NotFoundAccessKeyEx(api_key=qs_dict["key"])
                    mac = hmac.new(bytes(api_key.secret_key, encoding='utf8'), bytes(qs, encoding='utf-8'), digestmod='sha256')
                    d = mac.digest()
                    validating_secret = str(base64.b64encode(d).decode('utf-8'))

                    if headers["secret"] != validating_secret:
                        raise ex.APIHeaderInvalidEx()

                    now_timestamp = int(D.datetime(diff=9).timestamp())
                    if now_timestamp - 10 > int(qs_dict["timestamp"]) or now_timestamp < int(qs_dict["timestamp"]):
                        raise ex.APITimestampEx()

                    user_info = to_dict(api_key.users)
                    request.state.user = UserToken(**user_info)
                    # session.close()

                else:
                    # Request User 가 필요함
                    if "authorization" in headers.keys():
                        key = headers.get("Authorization")
                        api_key_obj = ApiKeys.get(session=session, access_key=key)
                        user_info = to_dict(User.get(session=session, sign_id=api_key_obj.user_id))
                        request.state.user = UserToken(**user_info)
                        # 토큰 없음
                    else:
                        if "Authorization" not in headers.keys():
                            raise ex.NotAuthorized()
                session.close()
                response = await call_next(request)
                return response
            else:
                if "authorization" in headers.keys():
                    token_info = await token_decode(access_token=headers.get("Authorization"))
                    request.state.user = UserToken(**token_info)
                    # 토큰 없음
                else:
                    if "Authorization" not in headers.keys():
                        raise ex.NotAuthorized()
        else:
            # 템플릿 렌더링인 경우 쿠키에서 토큰 검사
            cookies["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzaWduX2lkIjoxMiwic2lnbl9lbWFpbCI6InN0cmluZ0BkYXVtLm5ldCIsInNpZ25fbmFtZSI6Ilx1ZDY0ZFx1YWUzOFx1YjNkOSIsInNpZ25fY2VsbHBob25lIjoiMDEwLTU1MjMtMTIzNCIsImhvc3BpdGFsX2lkIjoxLCJleHAiOjE2NjQ1MDcxMDR9.BgNiSuKdvn-6HA18U_JjtUV2heno4wvpnsjyWBv8_io"

            if "Authorization" not in cookies.keys():
                raise ex.NotAuthorized()

            token_info = await token_decode(access_token=cookies.get("Authorization"))
            request.state.user = UserToken(**token_info)
        response = await call_next(request)
        await api_logger(request=request, response=response)
    except Exception as e:

        error = await exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)

    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def token_decode(access_token):
    """
    :param access_token:
    :return:
    """
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except DecodeError:
        raise ex.TokenDecodeEx()
    return payload


async def exception_handler(error: Exception):
    print(error)
    if isinstance(error, sqlalchemy.exc.OperationalError):
        error = ex.SqlFailureEx(ex=error)
    if not isinstance(error, ex.APIException):
        error = ex.APIException(ex=error, detail=str(error))
    return error
