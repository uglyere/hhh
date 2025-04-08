from hikkatl.types import (
    InputPeerEmpty,
    InputMediaUploadedPhoto,
    InputSingleMedia,
    InputPeerSelf
)
from hikkatl.functions import InvokeWithLayerRequest
from hikkatl.types import (
    messages,
)
from hikkatl import TLRequest
from hikkatl.types import (
    InputPeer,
    InputMedia,
)
from hikkatl.core import TLObject
from hikkatl.all import MessageEntityTextUrl
import random
from datetime import datetime


class MySendMultiMediaRequest(TLRequest):
    __slots__ = ['peer', 'reply_to_msg_id', 'multi_media', 'silent', 'background', 'clear_draft', 'schedule_date']

    def __init__(self, peer, multi_media, reply_to_msg_id=None, silent=False,
                 background=False, clear_draft=False, schedule_date=None):
        self.peer = peer
        self.multi_media = multi_media
        self.reply_to_msg_id = reply_to_msg_id
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.schedule_date = schedule_date

    def to_dict(self):
        return {
            "_": "messages.sendMultiMedia",
            "peer": self.peer,
            "multi_media": self.multi_media,
            "reply_to_msg_id": self.reply_to_msg_id,
            "silent": self.silent,
            "background": self.background,
            "clear_draft": self.clear_draft,
            "schedule_date": self.schedule_date
        }


async def custom_send_multi_media(client, peer, photo_paths: list, caption: str = None,
                                  reply_to_msg_id: int = None, silent: bool = False,
                                  schedule_date: int = None):
    """
    Ручная реализация отправки мультимедиа как альбома, без использования SendMultiMediaRequest из Telethon
    """

    input_peer = await client.get_input_entity(peer)

    # Загружаем все изображения
    media_files = []
    for photo_path in photo_paths:
        file = await client.upload_file(photo_path)
        media_files.append(file)

    # Формируем список InputSingleMedia
    multi_media = []
    for i, file in enumerate(media_files):
        input_media = InputMediaUploadedPhoto(file=file)
        multi_media.append(InputSingleMedia(
            media=input_media,
            message=caption if i == 0 and caption else "",
            entities=[],
            random_id=random.getrandbits(64)
        ))

    # Составляем свой объект запроса
    request = MySendMultiMediaRequest(
        peer=input_peer,
        multi_media=multi_media,
        reply_to_msg_id=reply_to_msg_id,
        silent=silent,
        background=False,
        clear_draft=False,
        schedule_date=datetime.fromtimestamp(schedule_date) if schedule_date else None
    )

    # Отправляем запрос через client._call
    return await client._call(request)
