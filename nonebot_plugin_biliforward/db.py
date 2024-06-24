from nonebot.log import logger
from .model import MsgInfo, WhiteList
from sqlalchemy import text
from sqlalchemy.future import select
from nonebot_plugin_orm import async_scoped_session, AsyncSession


class MsgInfoDatabase:
    def __init__(self, session: async_scoped_session|AsyncSession) -> None:
        self.session = session

    async def get_msg_info(self, msg_key: int) -> MsgInfo|None:
        # 查询消息
        if not (msg := await self.session.get(MsgInfo, msg_key)):
            return None
        return msg
    
    async def insert_msg_info(self, external_msg: MsgInfo) -> bool:
        try:
            self.session.add(external_msg)
        except Exception as e:
            logger.error(f'插入信息表时发生错误:\n{e}')
            await self.session.rollback()
            return False
        else:
            #logger.info(f'插入信息表成功')
            return True
        
    async def commit(self) -> None:
        await self.session.commit()

class WhiteListDatabase:
    def __init__(self, session: async_scoped_session|AsyncSession) -> None:
        self.session = session

    async def get_user_id_distinct_list(self) -> list[int]:
        stmt = select(WhiteList.bili_user_id).distinct()
        cursor = await self.session.execute(statement=stmt)
        return [_.bili_user_id for _ in cursor.fetchall()]
    
    async def get_group_id_by_user_id(self, bili_user_id: int) -> list[int]:
        stmt = select(WhiteList.group_id).where(WhiteList.bili_user_id == bili_user_id)
        cursor = await self.session.execute(statement=stmt)
        return [_.group_id for _ in cursor.fetchall()]
    
    async def get_whitelist(self, group_id: int, bili_user_id: int) -> WhiteList|None:
        # 查询白名单
        if not (whitelist := await self.session.get(WhiteList, (group_id, bili_user_id))):
            return None
        return whitelist
    
    async def insert_whitelist_info(self, external_whitelist: WhiteList) -> bool:
        try:
            self.session.add(external_whitelist)
        except Exception as e:
            logger.error(f'插入信息表时发生错误:\n{e}')
            await self.session.rollback()
            return False
        else:
            #logger.info(f'插入信息表成功')
            return True

    async def commit(self) -> None:
        await self.session.commit()