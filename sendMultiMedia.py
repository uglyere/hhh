from telethon.tl import types, functions
from telethon.tl.tlobject import TLObject
from telethon.tl.types import (
    InputMediaUploadedPhoto,
    InputMediaUploadedDocument,
    InputSingleMedia,
    InputMediaPhotoExternal,
    InputPeerUser,
    InputPeerChat,
    InputPeerChannel,
    MessageEntityBold,
    MessageEntityItalic,
    InputDocument,
)
import os
import random

class MySendMultiMediaRequest(TLObject):
    __slots__ = ["peer", "multi_media", "reply_to", "message", "random_id", "schedule_date"]

    def __init__(self, *, peer, multi_media, reply_to=None, message="", random_id=None, schedule_date=None):
        self.peer = peer
        self.multi_media = multi_media
        self.reply_to = reply_to
        self.message = message
        self.random_id = random_id
        self.schedule_date = schedule_date

    def to_dict(self):
        return {
            "_": "messages.sendMultiMedia",
            "peer": self.peer,
            "multi_media": self.multi_media,
            "reply_to": self.reply_to,
            "message": self.message,
            "random_id": self.random_id,
            "schedule_date": self.schedule_date,
        }

    def on_send(self, client):
        return functions.messages.SendMultiMedia(
            peer=self.peer,
            multi_media=self.multi_media,
            reply_to_msg_id=self.reply_to,
            message=self.message,
            random_id=self.random_id or client.rnd_id(),
            schedule_date=self.schedule_date
        )

# Функция для отправки медиа
async def custom_send_multi_media(client, chat_id, photo_paths, caption=None, reply_to_msg_id=None):
    media_list = []
    for path in photo_paths:
        if not os.path.exists(path):
            continue
        file = await client.upload_file(path)
        input_media = InputMediaUploadedPhoto(file=file)
        media = InputSingleMedia(
            media=input_media,
            message=caption or "",
            entities=[],
            random_id=random.randint(0, 0x7FFFFFFF)
        )
        media_list.append(media)

    if not media_list:
        return

    peer = await client.get_input_entity(chat_id)

    # Собственный TLRequest
    req = MySendMultiMediaRequest(
        peer=peer,
        multi_media=media_list,
        reply_to=reply_to_msg_id
    )

    # Отправка
    await client(req.on_send(client))
