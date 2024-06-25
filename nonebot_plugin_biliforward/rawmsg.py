import time
import json

from .model import MsgInfo, VedioInfo
from .db import MsgInfoDatabase
from nonebot.log import logger


class RawMsg:
    def __init__(self, rawmsg: dict) -> None:
        self.msg_type: int = rawmsg['msg_type']
        self.msg_key: int = rawmsg['msg_key']
        self.timestamp: int = rawmsg['timestamp']
        self.aid: int|None = json.loads(rawmsg['content'])['id'] if self.msg_type == 7 else None
        self.sharer_uid: int = rawmsg['sender_uid']

    async def if_new(self, msg_db: MsgInfoDatabase) -> bool:
        now_time = time.time()

        if now_time - self.timestamp > 3600:
            return False
        
        msg = await msg_db.get_msg_info(msg_key=self.msg_key)
        if msg:
            return False
        
        return True
    
    def get_new_msginfo(self) -> MsgInfo:
        return MsgInfo(msg_key=self.msg_key, aid=self.aid, sharer_uid=self.sharer_uid)
