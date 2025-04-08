import os
import random
from hikkatl.types import (  # type: ignore
    InputPeerUser,
    InputPeerChat,
    InputPeerChannel,
    InputMediaUploadedPhoto,
    InputSingleMedia,
    InputReplyToMessage,
)
from hikkatl.functions import InvokeWithLayerRequest  # type: ignore


async def send_photo_album(
    client,
    peer,
    photo_paths,
    caption=None,
    reply_to_msg_id=None,
    silent=False,
    background=False,
    clear_draft=False,
    noforwards=False,
    schedule_date=None,
):
    """
    Send an album of photos only

    Args:
        client: Authenticated TelegramClient instance
        peer: Target chat (username, ID, or InputPeer)
        photo_paths: List of paths to photo files
        caption: Optional caption for the album
        reply_to_msg_id: Message ID to reply to
        silent: Send silently (no notifications)
        background: Send in background
        clear_draft: Clear the draft after sending
        noforwards: Disable forwarding
        schedule_date: Unix timestamp for scheduled sending
    """

    # Resolve the peer if not already an InputPeer
    if not isinstance(peer, (InputPeerUser, InputPeerChat, InputPeerChannel)):
        peer = await client.get_input_entity(peer)

    # Prepare the reply_to parameter if needed
    reply_to = None
    if reply_to_msg_id:
        reply_to = InputReplyToMessage(reply_to_msg_id)

    # Upload all photos
    uploaded_photos = []
    for photo_path in photo_paths:
        file = await client.upload_file(photo_path)
        input_media = InputMediaUploadedPhoto(file)
        uploaded_photos.append(input_media)

    # Prepare InputSingleMedia objects
    multi_media = []
    for media in uploaded_photos:
        multi_media.append(
            InputSingleMedia(
                media=media,
                random_id=random.randint(0, 0x7FFFFFFF),
                message=caption if caption else "",
                entities=None,
            )
        )

    # Prepare flags
    flags = 0
    if silent:
        flags |= 1 << 5
    if background:
        flags |= 1 << 6
    if clear_draft:
        flags |= 1 << 7
    if noforwards:
        flags |= 1 << 14
    if reply_to is not None:
        flags |= 1 << 0
    if schedule_date is not None:
        flags |= 1 << 10

    # Construct the request
    request = {
        "_": "messages.sendMultiMedia",
        "flags": flags,
        "peer": peer,
        "multi_media": multi_media,
        "reply_to": reply_to,
        "schedule_date": schedule_date,
    }

    # Remove None values
    request = {k: v for k, v in request.items() if v is not None}

    # Send the request
    result = await client(InvokeWithLayerRequest(layer=195, query=request))

    return result
