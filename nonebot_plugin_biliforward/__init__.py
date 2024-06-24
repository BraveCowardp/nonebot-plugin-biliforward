from nonebot.plugin import PluginMetadata
from nonebot import require, on_command, get_bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from nonebot.log import logger
import asyncio
import time

require("nonebot_plugin_saa")
require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_saa import Image, Text, enable_auto_select_bot, TargetQQGroup
from nonebot_plugin_orm import async_scoped_session, get_session
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .biliapi import BiliApi
from .qrcodestatus import QrCodeStatus
from .db import MsgInfoDatabase, WhiteListDatabase
from .model import WhiteList

__plugin_meta__ = PluginMetadata(
    name="b站消息转发",
    description="通过扫码登录b站，并把其他人通过私信分享的视频转发到qq群",
    usage="请查看README",

    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/BraveCowardp/nonebot-plugin-biliforward",
    # 发布必填。

    config=Config,
    # 插件配置项类，如无需配置可不填写。

    supported_adapters={"~onebot.v11"},
    # 支持的适配器集合，其中 `~` 在此处代表前缀 `nonebot.adapters.`，其余适配器亦按此格式填写。
    # 若插件可以保证兼容所有适配器（即仅使用基本适配器功能）可不填写，否则应该列出插件支持的适配器。
)

bili_login = on_command('登录b站', permission=SUPERUSER)
bili_user_info = on_command('b站登录用户信息')
add_whitelist = on_command('添加b站转发白名单')

enable_auto_select_bot()

@bili_login.handle()
async def handle_bili_login():
    img, qrcode_key = await BiliApi.login()
    if not img or not qrcode_key:
        await bili_login.finish(f"请求失败，请查看日志")
    await Image(img).send()

    start_time = time.time()
    while True:
        qr_code = await BiliApi.qr_check(qrcode_key)
        if qr_code == QrCodeStatus.SUCCESS:
            await Text("登录成功").finish()

        if qr_code == QrCodeStatus.INVALID:
            await Text("二维码已失效").finish()

        if time.time() - start_time > 180:
            await Text("超时").finish()
        await asyncio.sleep(2)

@bili_user_info.handle()
async def handle_bili_user_info():
    user_info = await BiliApi.basic_info()
    if not user_info:
        await bili_login.finish(f"请求失败，请查看日志")

    await Text(str(user_info)).finish()

@add_whitelist.handle()
async def handle_add_whitelist(event: GroupMessageEvent, session: async_scoped_session, args: Message = CommandArg()):
    info_list = args.extract_plain_text().split()
    if len(info_list) != 1:
        await Text("参数个数有误，应为b站用户id").finish()
    
    try:
        bili_user_id = int(info_list[0])
    except ValueError:
        await Text("类型错误，b站用户id应为纯数字").finish()
    
    user_info = await BiliApi.fetch_target_user_info(user_id=bili_user_id)
    if not user_info:
        await Text("用户信息获取失败").finish()

    whitelistdatabase = WhiteListDatabase(session=session)
    whitelist = await whitelistdatabase.get_whitelist(group_id=event.group_id, bili_user_id=bili_user_id)
    if whitelist:
        await Text(f"用户{user_info.uname}(uid:{user_info.mid})已在本群转发白名单").finish()

    result = None
    if not user_info.if_following:
        result = await BiliApi.follow_user(user_id=bili_user_id)
        if not result:
            await Text("用户关注失败").finish()

    result = await whitelistdatabase.insert_whitelist_info(external_whitelist=WhiteList(group_id=event.group_id, bili_user_id=bili_user_id))
    if result:
        await whitelistdatabase.commit()
        await Text(f"用户{user_info.uname}(uid:{user_info.mid})已关注并添加到本群转发白名单").finish()

@scheduler.scheduled_job('cron', second='*/10')
async def bili_fetch_msg():
    session = get_session()
    whitelistdatabase = WhiteListDatabase(session=session)
    msginfodatabase = MsgInfoDatabase(session=session)
    bili_user_id_list = await whitelistdatabase.get_user_id_distinct_list()
    for bili_user_id in bili_user_id_list:
        user_info = None
        group_id_list = None
        raw_msg_list = await BiliApi.fetch_msg(talker_id=bili_user_id)
        if not raw_msg_list:
            continue
        for raw_msg in raw_msg_list:
            if raw_msg.aid and await raw_msg.if_new(msg_db=msginfodatabase):
                if not user_info:
                    user_info = await BiliApi.fetch_target_user_info(user_id=raw_msg.sharer_uid)
                videoinfo = await BiliApi.fetch_video_info(aid=raw_msg.aid)
                if videoinfo:
                    if user_info:
                        videoinfo.sharer = user_info.uname
                    msg = videoinfo.get_msg_to_send()
                    if not group_id_list:
                        group_id_list = await whitelistdatabase.get_group_id_by_user_id(bili_user_id=bili_user_id)
                    for group_id in group_id_list:
                        await msg.send_to(target=TargetQQGroup(group_id=group_id))
                    await msginfodatabase.insert_msg_info(external_msg=raw_msg.get_new_msginfo())
                    await msginfodatabase.commit()
    await session.close()