from typing import Any, List, Dict, Tuple, Optional
from app.plugins import _PluginBase
from app.core.event import eventmanager, Event
from app.schemas.types import EventType
from app.schemas import TransferInfo
from app.core.context import MediaInfo
from app.log import logger
import requests


class MediaNotification(_PluginBase):
    # 插件基本信息
    plugin_name = "媒体入库通知"
    plugin_desc = "媒体入库后向其他服务器发送通知。"
    plugin_icon = "refresh2.png"
    plugin_version = "0.1"
    plugin_author = "pattonbina"
    author_url = "https://github.com/pattonbina"
    plugin_config_prefix = "medianotification_"
    plugin_order = 15
    auth_level = 1

    # 私有属性
    _enabled = False
    _webhook_url = None
    _notify_type = None  # 可以设置通知类型，如电影/剧集/全部
    
    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self._webhook_url = config.get("webhook_url")
            self._notify_type = config.get("notify_type")

    def get_state(self) -> bool:
        return self._enabled

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        插件配置页面
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'webhook_url',
                                            'label': 'Webhook地址',
                                            'placeholder': 'http://your-server/webhook'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'notify_type',
                                            'label': '通知类型',
                                            'items': [
                                                {'title': '全部', 'value': 'ALL'},
                                                {'title': '仅电影', 'value': 'MOVIE'},
                                                {'title': '仅剧集', 'value': 'TV'}
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "webhook_url": "",
            "notify_type": "ALL"
        }

    @eventmanager.register(EventType.TransferComplete)
    def notify(self, event: Event):
        """
        发送通知
        """
        if not self._enabled or not self._webhook_url:
            return

        event_info: dict = event.event_data
        if not event_info:
            return

        # 获取媒体信息
        mediainfo: MediaInfo = event_info.get("mediainfo")
        if not mediainfo:
            return

        # 检查通知类型
        if self._notify_type != "ALL":
            if self._notify_type == "MOVIE" and mediainfo.type != "电影":
                return
            if self._notify_type == "TV" and mediainfo.type != "电视剧":
                return

        # 构建通知数据
        notify_data = {
            "title": mediainfo.title,
            "year": mediainfo.year,
            "type": mediainfo.type,
            "category": mediainfo.category,
            "overview": mediainfo.overview,
            "poster": mediainfo.poster,
            # 可以根据需要添加更多字段
        }

        try:
            # 发送通知
            response = requests.post(
                self._webhook_url,
                json=notify_data,
                timeout=10
            )
            if response.status_code == 200:
                logger.info(f"媒体入库通知发送成功：{mediainfo.title}")
            else:
                logger.error(f"媒体入库通知发送失败：{response.status_code}")
        except Exception as e:
            logger.error(f"媒体入库通知发送出错：{str(e)}")

    def stop_service(self):
        """
        退出插件
        """
        pass
