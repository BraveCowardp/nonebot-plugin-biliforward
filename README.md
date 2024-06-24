<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-biliforward

_✨ B站视频转发插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/BraveCowardp/nonebot-plugin-biliforward.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-biliforward">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-biliforward.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 介绍

让机器人登录B站账号，在B站中向机器人登录的B站账号分享视频，机器人可以把收到的分享转发到qq群聊中

（群友希望把视频分享给小群里的好厚米，但是有些群友设备从B站向qq分享视频不方便，于是此插件应运而生）

欢迎提建议和issue

## 💿 安装

<details open>
<summary>使用 nb-cli 安装(推荐！)</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-biliforward

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-biliforward
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-biliforward
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-biliforward
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-biliforward
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_biliforward"]

</details>

## 🎉 使用
### 更新数据模型 <font color=#fc8403 >使用必看！！！！！</font>
本插件使用了官方推荐的`nonebot-plugin-orm`插件操作数据库，安装插件或更新插件版本后，在启动机器人前，都需要执行此命令。
```shell
nb orm upgrade
```
手动执行下列命令检查数据库模式是否与模型定义一致。机器人启动前也会自动运行此命令，并在检查失败时阻止启动。
```shell
nb orm check
```
看到`没有检测到新的升级操作`字样时，表明数据库模型已经成功创建或更新，可以启动机器人
### 指令表
| 指令 | 参数 | 权限 | 需要@ | 范围 | 说明 |
|:----|:----|:----|:----|:----|:----|
| 登录b站 | 无 | 超级管理员 | 否 | 建议私聊使用 | 通过扫码让机器人登录B站账号，建议此账号只给机器人使用，并且一个机器人只允许登录一个账号，所有群聊通用 |
| b站登录用户信息 | 无 | 群员 | 否 | 群聊 | 查看机器人登录的B站用户信息 |
| 添加b站转发白名单 | bili_uid | 群员 | 否 | 群聊 | 添加B站用户到此群聊白名单，此用户向机器人用户分享的视频将会被发送到此群 |

## TODO
- [ ] 优化视频信息排版，可能会使用html渲染成图片 ~~(正在学习)~~
- [ ] 增加取消白名单功能
- [ ] web端可以通过在评论区@机器人转发视频