from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model
from nonebot_plugin_saa import Text, Image, MessageFactory


class BiliUserInfo:
    def __init__(self, mid: int, uname: str, if_following: None|bool = None) -> None:
        self.mid: int = mid
        self.uname: str = uname
        self.if_following: None|bool = if_following

    def __str__(self) -> str:
        return f'uid:{self.mid}\n昵称:{self.uname}'

class MsgInfo(Model):
    msg_key: Mapped[int] = mapped_column(primary_key=True)
    aid: Mapped[int]
    sharer_uid: Mapped[int]

class WhiteList(Model):
    group_id: Mapped[int]
    bili_user_id: Mapped[int]
    nick_name: Mapped[str] = mapped_column(default='')

    __table_args__ = (
        PrimaryKeyConstraint('group_id', 'bili_user_id'),
    )


class VedioInfo:    
    def __init__(self, title: str, url: str, up: str, cover_url: str, duration: int, sharer: str|None = None) -> None:
        self.title: str = title
        self.url: str = url
        self.up: str = up
        self.cover_url: str = cover_url
        self.duration: int = duration
        self.sharer: str|None = sharer

    def get_duration_str(self) -> str:
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    def get_msg_to_send(self) -> MessageFactory:
        msg = MessageFactory([
            Image(image=self.cover_url), 
            Text(f'标题:{self.title}\n'), 
            Text(f'UP主:{self.up}\n'), 
            Text(f'时长:{self.get_duration_str()}\n'),
            Text(f'链接:{self.url}\n'),
            Text(f'by {self.sharer}')
            ])
        return msg
