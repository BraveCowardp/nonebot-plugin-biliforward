import httpx
import qrcode
from nonebot import logger
from typing import Tuple
from io import BytesIO
from pathlib import Path
import aiofiles
import json
import traceback

from .qrcodestatus import QrCodeStatus
from .actcode import ActCode
from .model import BiliUserInfo, VedioInfo
from .rawmsg import RawMsg
import nonebot_plugin_localstore as store

headers = {
    'User-Agent': 'curl/7.64.1',  # 模拟 curl 的用户代理
    'Accept': '*/*',  # curl 默认添加的 Accept 头部
}

post_headers = {
    'User-Agent': 'curl/7.64.1',  # 模拟 curl 的用户代理
    'Accept': '*/*',  # curl 默认添加的 Accept 头部
    'Content-Type': 'application/x-www-form-urlencoded',
}

PLUGIN_NAME = 'nonebot-plugin-biliforward'

GET_QR = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
POLL_QR = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
GET_USER_INFO = 'https://api.bilibili.com/x/web-interface/nav'
FETCH_MSG = 'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs'
FETCH_VEDIO_INFO = 'https://api.bilibili.com/x/web-interface/view'
FETCH_TARGET_USER_INFO = 'https://api.bilibili.com/x/web-interface/card'
MODIFY_RELATION = 'https://api.bilibili.com/x/relation/modify'

async def save_cookie(file: Path, client: httpx.AsyncClient):
    cookie = dict(client.cookies)
    logger.debug(f"write into file:{file}\ncookie:{cookie}")
    async with aiofiles.open(file, 'w') as f:
        await f.write(json.dumps(cookie))

async def load_cookie(file: Path, client: httpx.AsyncClient):
    async with aiofiles.open(file, 'r') as f:
        cookies_dict = dict(json.loads(await f.read()))
    client.cookies.update(cookies=cookies_dict)


class BiliApi:
    @staticmethod
    async def login() -> Tuple[bytes|None, str|None]:
        qrcode_key: None|str = None
        img: None|bytes = None
        async with httpx.AsyncClient() as client:
            respose = await client.get(url=GET_QR, headers=headers, timeout=90)

        try:
            qrcode_key = respose.json()['data']['qrcode_key']
            url = respose.json()['data']['url']
            qr = qrcode.make(url)
            byte_stream = BytesIO()
            qr.save(byte_stream, 'PNG')
            img = byte_stream.getvalue()
        except:
            logger.debug(f"status code:{respose.status_code}")
            logger.debug(f"response:{respose.json()}")

        return img, qrcode_key

    @staticmethod
    async def qr_check(qrcode_key: str) -> QrCodeStatus|None:
        qr_code: int|None = None
        params = {
            'qrcode_key': qrcode_key
            }
        async with httpx.AsyncClient() as client:
            respose = await client.get(url=POLL_QR, params=params, headers=headers, timeout=90)
            try:
                qr_code = respose.json()['data']['code']
                cookie_file = store.get_data_file(PLUGIN_NAME, "cookie")
                if qr_code == QrCodeStatus.SUCCESS.value:
                    await save_cookie(file=cookie_file, client=client)

            except:
                logger.debug(f"status code:{respose.status_code}")
                logger.debug(f"response:{respose.json()}")

        return qr_code if qr_code == None else QrCodeStatus(qr_code)
    
    @staticmethod
    async def basic_info() -> BiliUserInfo|None:
        user_info: BiliUserInfo|None = None

        async with httpx.AsyncClient() as client:
            cookie_file = store.get_data_file(PLUGIN_NAME, "cookie")
            await load_cookie(file=cookie_file, client=client)
            respose = await client.get(url=GET_USER_INFO, headers=headers, timeout=90)
            try:
                mid = respose.json()['data']['mid']
                uname = respose.json()['data']['uname']
                user_info = BiliUserInfo(mid, uname)

            except:
                logger.debug(f"status code:{respose.status_code}")
                logger.debug(f"response:{respose.json()}")

        return user_info
    
    @staticmethod
    async def fetch_msg(talker_id: int) -> None|list[RawMsg]:
        msg_list: None|list[RawMsg] = None
        params = {
            'talker_id': talker_id,
            'session_type': 1,
            'size':10
            }
        async with httpx.AsyncClient() as client:
            cookie_file = store.get_data_file(PLUGIN_NAME, "cookie")
            await load_cookie(file=cookie_file, client=client)
            respose = await client.get(url=FETCH_MSG, params=params, headers=headers, timeout=90)
            try:
                msg_list = []
                for message in respose.json()['data']['messages']:
                    msg_list.append(RawMsg(message))
            except:
                logger.debug(traceback.format_exc())
                logger.debug(f"status code:{respose.status_code}")
                logger.debug(f"response:{respose.json()}")

        return msg_list
    
    @staticmethod
    async def fetch_video_info(aid: int) -> None|VedioInfo:
        videoinfo: None|VedioInfo = None
        params = {
            'aid': aid
            }
        async with httpx.AsyncClient() as client:
            cookie_file = store.get_data_file(PLUGIN_NAME, "cookie")
            await load_cookie(file=cookie_file, client=client)
            respose = await client.get(url=FETCH_VEDIO_INFO, params=params, headers=headers, timeout=90)
            try:
                data = respose.json()['data']
                title = data['title']
                bvid = data['bvid']
                url = f'https://www.bilibili.com/video/{bvid}'
                up = data['owner']['name']
                cover_url = data['pic']
                duration = data['duration']
                videoinfo = VedioInfo(title=title, url=url, up=up, cover_url=cover_url, duration=duration)
            except:
                logger.debug(f"status code:{respose.status_code}")
                logger.debug(f"response:{respose.json()}")

        return videoinfo
    
    @staticmethod
    async def fetch_target_user_info(user_id: int) -> None|BiliUserInfo:
        userinfo: None|BiliUserInfo = None
        params = {
            'mid': user_id
            }
        async with httpx.AsyncClient() as client:
            cookie_file = store.get_data_file(PLUGIN_NAME, "cookie")
            await load_cookie(file=cookie_file, client=client)
            respose = await client.get(url=FETCH_TARGET_USER_INFO, params=params, headers=headers, timeout=90)
            try:
                data = respose.json()['data']
                userinfo = BiliUserInfo(mid=user_id, uname=data['card']['name'], if_following=data['following'])
            except:
                logger.debug(f"status code:{respose.status_code}")
                logger.debug(f"response:{respose.json()}")

        return userinfo
    
    @staticmethod
    async def follow_user(user_id: int) -> None|bool:
        result: None|bool = None
        data = {
            'fid': user_id,
            'act': ActCode.follow.value,
            're_src': 11
            }
        async with httpx.AsyncClient() as client:
            cookie_file = store.get_data_file(PLUGIN_NAME, "cookie")
            await load_cookie(file=cookie_file, client=client)
            respose = await client.post(url=MODIFY_RELATION, data=data, headers=post_headers, timeout=90)
            try:
                code = respose.json()['code']
                if code == 0:
                    result = True
            except:
                logger.debug(f"status code:{respose.status_code}")
                logger.debug(f"response:{respose.json()}")

        return result