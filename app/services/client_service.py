from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Client, Tel
from app.errors import ClientNotFound, TelNotFound
from app.schemas.client import ClientCreate


class ClientService:
    async def create_client(self, session: AsyncSession, client_data: ClientCreate) -> Client:
        client = Client(**client_data.model_dump())
        session.add(client)
        await session.commit()
        await session.refresh(client)
        return client

    async def get_client(self, session: AsyncSession, client_id: int) -> Client | None:
        statement = select(Client).where(Client.client_id == client_id)  # .options(selectinload(Client.tels))
        results = await session.exec(statement)
        return results.first()

    async def get_clients(
        self, session: AsyncSession, hospital_id: int, skip: int = 0, limit: int = 100
    ) -> list[Client]:
        # 지연로딩 설정이 없을경우 selectinload 옵션을 사용하여 관련된 텔레폰 정보를 함께 가져올 수 있습니다.
        statement = (
            select(Client).where(Client.hospital_id == hospital_id).offset(skip).limit(limit)
        )  # .options(selectinload(Client.tels))
        results = await session.exec(statement)
        return results.all()

    async def update_client(self, session: AsyncSession, client_id: int, client_data: dict) -> Client:
        client = await self.get_client(session=session, client_id=client_id)
        if not client:
            raise ClientNotFound()

        for key, value in client_data.items():
            setattr(client, key, value)

        await session.commit()
        await session.refresh(client)

        return client

    async def delete_client(self, session: AsyncSession, client_id: int) -> bool:
        client = await self.get_client(session=session, client_id=client_id)
        if client is not None:
            await session.delete(client)
            await session.commit()
            return True
        else:
            return False

    async def get_tel(self, session: AsyncSession, tel_id: int) -> Tel | None:
        statement = select(Tel).where(Tel.tel_id == tel_id)
        results = await session.exec(statement)
        return results.first()

    async def get_tels(self, session: AsyncSession, client_id: int) -> list[Tel]:
        statement = select(Tel).where(Tel.client_id == client_id)
        results = await session.exec(statement)
        return results.all()

    async def create_tel(self, session: AsyncSession, tel_data: dict) -> Tel:
        tel = Tel(**tel_data)
        session.add(tel)
        await session.commit()
        await session.refresh(tel)
        return tel

    async def update_tel(self, session: AsyncSession, tel_id: int, tel_data: dict) -> Tel:
        tel = await self.get_tel(session=session, tel_id=tel_id)
        if not tel:
            raise TelNotFound()

        for key, value in tel_data.items():
            setattr(tel, key, value)

        await session.commit()
        await session.refresh(tel)

        return tel

    async def delete_tel(self, session: AsyncSession, tel_id: int) -> bool:
        tel = await self.get_tel(session=session, tel_id=tel_id)
        if tel is not None:
            await session.delete(tel)
            await session.commit()
            return True
        else:
            return False

    async def delete_tel_with_client_id(self, session: AsyncSession, client_id: int) -> bool:
        # 1. client_id가 일치하는 모든 Tel 레코드를 삭제하는 구문 생성
        statement = delete(Tel).where(Tel.client_id == client_id)

        # 2. 쿼리 실행
        result = await session.exec(statement)

        # 3. 변경 사항 반영
        await session.commit()

        # rowcount를 통해 실제 삭제된 데이터가 있는지 확인 (선택 사항)
        return result.rowcount > 0

    async def create_client_with_tels(self, session: AsyncSession, client_in: ClientCreate) -> Client:
        """
        Client와 (선택 사항인) Tel 목록을 하나의 트랜잭션으로 생성합니다.
        tels 데이터가 없어도 안전하게 동작합니다.
        """
        try:
            # 1. Client 데이터에서 'tels' 필드가 있다면 분리하고, 나머지는 Client 객체로 생성
            # model_dump() 시 exclude를 사용하여 관계 데이터를 제외한 순수 필드만 추출합니다.
            client_data = client_in.model_dump(exclude={"tels"})
            db_client = Client(**client_data)

            # 2. tels 데이터가 리스트로 존재하는지 확인 (Walrus operator := 사용)
            if tels_list := getattr(client_in, "tels", []):
                for tel_data in tels_list:
                    # tel_data(Pydantic)를 dict로 변환
                    tel_dict = tel_data.model_dump()

                    # 부모(Client)의 인증 정보를 자식(Tel)에게도 복사
                    tel_dict["created_sign_id"] = client_data.get("created_sign_id")
                    tel_dict["created_sign_name"] = client_data.get("created_sign_name")
                    # 필요하다면 hospital_id도 동일하게 처리
                    tel_dict["hospital_id"] = client_data.get("hospital_id")

                    # Relationship을 통해 자동 FK 매핑
                    new_tel = Tel(**tel_dict)
                    db_client.tels.append(new_tel)

            # 3. DB 세션 추가 및 커밋
            # db_client만 add 해도 연결된 모든 new_tel 객체가 함께 session에 등록됩니다.
            session.add(db_client)
            await session.commit()

            # 4. 최신 상태 반영 (DB에서 생성된 PK 및 Server Default 값 로드)
            await session.refresh(db_client)
            return db_client

        except SQLAlchemyError as e:
            # 오류 발생 시 원자성(Atomicity)을 위해 롤백
            await session.rollback()
            # 로깅을 추가하거나 상위 레이어로 에러를 전파합니다.
            raise e

    async def update_client_with_tels(
        self, session: AsyncSession, client_id: int, client_data_dict: dict
    ) -> Client:
        try:
            # 1. Client 로드 (tels 관계 포함)
            # 만약 get_client에서 selectinload가 안되어 있다면 여기서 명시적으로 로드하는 것이 좋습니다.
            client = await self.get_client(session=session, client_id=client_id)
            if not client:
                raise ClientNotFound()

            hospital_id = client_data_dict.get("hospital_id")
            sign_id = client_data_dict.get("updated_sign_id")
            sign_name = client_data_dict.get("updated_sign_name")

            # 2. 'tels' 데이터 분리
            tels_list = client_data_dict.pop("tels", None)

            # 3. Client 기본 정보 업데이트
            for key, value in client_data_dict.items():
                if hasattr(client, key):
                    setattr(client, key, value)

            # 4. Tel 데이터 처리 (Upsert)
            if tels_list is not None:
                # 현재 이 클라이언트가 가진 기존 전화번호들을 매핑 (빠른 조회를 위해)
                existing_tels = {t.tel_id: t for t in client.tels}

                # tel_list 없는 경우 기존 텔레폰 전체 삭제를 원할시 주석해제
                # # 새로 요청받은 tel_id 집합 (신규 생성 건은 None이므로 제외)
                # incoming_tel_ids = {item["tel_id"] for item in tels_list if item.get("tel_id")}

                # # --- [삭제 로직] ---
                # # 기존 ID 중 요청 데이터에 없는 ID는 삭제 대상으로 판단
                # for tid, tel_obj in existing_tels.items():
                #     if tid not in incoming_tel_ids:
                #         await session.delete(tel_obj)

                for tel_item in tels_list:
                    tid = tel_item.get("tel_id")

                    # (Case A) 기존 데이터 수정: tel_id가 있고 기존 목록에 존재하는 경우
                    if tid and tid in existing_tels:
                        target_tel = existing_tels[tid]
                        target_tel.updated_sign_id = sign_id
                        target_tel.updated_sign_name = sign_name
                        for k, v in tel_item.items():
                            if k not in ["tel_id", "created_sign_id", "created_sign_name"]:
                                setattr(target_tel, k, v)

                    # (Case B) 신규 데이터 추가: tel_id가 없거나 매칭되는 게 없는 경우
                    else:
                        # tel_id는 DB에서 자동생성되도록 제거 후 생성
                        new_tel_data = {k: v for k, v in tel_item.items() if k != "tel_id"}
                        new_tel = Tel(
                            **new_tel_data,
                            client_id=client_id,
                            hospital_id=hospital_id,
                            created_sign_id=sign_id,  # 신규 추가이므로 생성 정보 삽입
                            created_sign_name=sign_name,
                        )
                        session.add(new_tel)

            # 5. 트랜잭션 커밋 (에러 발생 시 위 작업 전체가 롤백됨)
            await session.commit()
            await session.refresh(client)
            return client

        except Exception as e:
            await session.rollback()
            raise e
