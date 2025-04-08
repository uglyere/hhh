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
    CONSTRUCTOR_ID = 0x6e8a74d8  # Это должен быть правильный constructor_id для messages.sendMultiMedia
    SUBCLASS_OF_ID = 0x8af52aac  # Updates

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
            "_": "MySendMultiMediaRequest",
            "peer": self.peer,
            "multi_media": self.multi_media,
            "reply_to": self.reply_to,
            "message": self.message,
            "random_id": self.random_id,
            "schedule_date": self.schedule_date,
        }

    def __bytes__(self):
        return b''.join((
            b'\xd8t\x8an',  # CONSTRUCTOR_ID
            self.serialize_bytes(self.peer),
            self.serialize_bytes(self.multi_media),
            b'\xb8\x1d\xf5\xa5' if self.reply_to else b'',  # Это Serialize self.reply_to с учетом флага
            self.serialize_bytes(self.message),
            self.serialize_bytes(self.random_id or 0),
            self.serialize_bytes(self.schedule_date) if self.schedule_date else b''
        ))

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

    req = MySendMultiMediaRequest(
        peer=peer,
        multi_media=media_list,
        reply_to=reply_to_msg_id
    )

    # Отправка запроса
    result = await client._call_function('messages.sendMultiMedia', req)
    return result
