from datetime import datetime
from typing import List, Union
from kritor.message import Source
from kritor.message.chain import MessageChain
from kritor.message.element import (
    Plain,
    At,
    AtAll,
    Face,
    Quote,
    Image,
    Forward,
    File,
    MultimediaElement,
    FlashImage,
    Voice,
    Video,
)
from kritor.models.relationship import (
    Client,
    Friend,
    Group,
    Member,
    Stranger,
    MemberPerm,
)
from kritor.protos.common.message_data_pb2 import PushMessageBody
from kritor.protos.common.message_element_pb2 import (
    Element,
    TextElement,
    AtElement,
    FaceElement,
    BubbleFaceElement,
    ReplyElement,
    ImageElement,
    VoiceElement,
    VideoElement,
    BasketballElement,
    DiceElement,
    RpsElement,
    PokeElement,
    MusicElement,
    WeatherElement,
    LocationElement,
    ShareElement,
    GiftElement,
    MarketFaceElement,
    ForwardElement,
    ContactElement,
    JsonElement,
    XmlElement,
    FileElement,
    MarkdownElement,
    ButtonElement,
)
from kritor.protos.common.contact_pb2 import Contact, Sender, Scene


def to_contact(target: Union[Friend, Group]) -> Contact:
    if isinstance(target, Group):
        return Contact(scene=Scene.GROUP, peer=str(target.id))
    elif isinstance(target, Friend):
        return Contact(scene=Scene.FRIEND, peer=str(target.id))
    else:
        raise NotImplementedError()


def to_message_chain(elements: List[Element]) -> MessageChain:
    """这里有bug，kritor的element.type永远为0，这里workaround想办法

    Args:
        elements (List[Element]): _description_

    Raises:
        NotImplementedError: _description_

    Returns:
        MessageChain: _description_
    """
    message_chain = MessageChain([])
    for element in elements:
        data_field = element.WhichOneof("data")
        if data_field == "text":  # element.type == Element.ElementType.TEXT
            message_chain.content.append(Plain(text=element.text.text))
        elif data_field == "at":  # element.type == Element.ElementType.AT
            message_chain.content.append(At(target=element.at.uin))
        elif data_field == "face":  # element.type == Element.ElementType.FACE
            message_chain.content.append(
                Face(
                    id=element.face.id,
                    face_id=element.face.result,
                    name=None,
                    is_big=element.face.is_big,
                )
            )
        elif (
            data_field == "bubble_face"
        ):  # element.type == Element.ElementType.BUBBLE_FACE
            message_chain.content.append(
                BubbleFaceElement(
                    target=element.bubble_face.id,
                    count=element.bubble_face.count,
                )
            )
        elif data_field == "reply":  # element.type == Element.ElementType.REPLY
            message_chain.content.append(
                Quote(
                    id=int(element.reply.message_id),
                )
            )
        elif data_field == "image":  # element.type == Element.ElementType.IMAGE
            image_data_field = element.image.WhichOneof("data")
            if image_data_field == "file":
                message_chain.content.append(
                    Image(
                        id=element.image.file_md5,
                        data_bytes=element.image.file,
                    )
                )
            elif image_data_field == "file_name":
                message_chain.content.append(
                    Image(
                        id=element.image.file_md5,
                        path=element.image.file_path,
                    )
                )
            elif image_data_field == "file_path":
                message_chain.content.append(
                    Image(
                        id=element.image.file_md5,
                        path=element.image.file_path,
                    )
                )
            elif image_data_field == "file_url":
                message_chain.content.append(
                    Image(
                        id=element.image.file_md5,
                        url=element.image.file_url,
                    )
                )
            else:
                raise Exception("Unsupported image type.")
        elif data_field == "voice":
            voice_data_field = element.voice.WhichOneof("data")
            if voice_data_field == "file":
                message_chain.content.append(
                    Voice(
                        id=element.voice.file_md5,
                        data_bytes=element.voice.file,
                    )
                )
            elif voice_data_field == "file_name":
                message_chain.content.append(
                    Voice(
                        id=element.voice.file_md5,
                        path=element.voice.file_path,
                    )
                )
            elif voice_data_field == "file_path":
                message_chain.content.append(
                    Voice(
                        id=element.voice.file_md5,
                        path=element.voice.file_path,
                    )
                )
            elif voice_data_field == "file_url":
                message_chain.content.append(
                    Voice(
                        id=element.voice.file_md5,
                        url=element.voice.file_url,
                    )
                )
            else:
                raise Exception("Unsupported voice type.")
        elif data_field == "video":
            video_data_field = element.video.WhichOneof("data")
            if video_data_field == "file":
                message_chain.content.append(
                    Video(
                        id=element.video.file_md5,
                        data_bytes=element.video.file,
                    )
                )
            elif video_data_field == "file_name":
                message_chain.content.append(
                    Video(
                        id=element.video.file_md5,
                        path=element.video.file_path,
                    )
                )
            elif video_data_field == "file_path":
                message_chain.content.append(
                    Video(
                        id=element.video.file_md5,
                        path=element.video.file_path,
                    )
                )
            elif video_data_field == "file_url":
                message_chain.content.append(
                    Video(
                        id=element.video.file_md5,
                        url=element.video.file_url,
                    )
                )
            else:
                raise Exception("Unsupported video type.")
        elif data_field == "basketball":
            pass
        elif data_field == "dice":
            pass
        elif data_field == "rps":
            pass
        elif data_field == "poke":
            pass
        elif data_field == "music":
            pass
        elif data_field == "weather":
            pass
        elif data_field == "location":
            pass
        elif data_field == "share":
            pass
        elif data_field == "gift":
            pass
        elif data_field == "market_face":
            pass
        elif data_field == "forward":
            pass
        elif data_field == "contact":
            pass
        elif data_field == "json":
            pass
        elif data_field == "xml":
            pass
        elif data_field == "file":
            pass
        elif data_field == "markdown":
            pass
        elif data_field == "button":
            pass
        else:
            pass
            # raise NotImplementedError()
    return message_chain


def to_message(chain: MessageChain) -> List[Element]:
    message = MessageChain([])
    for element in chain.content:
        if element.type == "Plain":
            message.append(TextElement(text=element.text))
        elif element.type == "At":
            message.append(AtElement(target=element.at.uid))
        elif element.type == "AtAll":
            pass
        elif element.type == "Face":
            message.append(
                FaceElement(id=element.face_id, is_big=False, result=element.name)
            )
        elif element.type == "Xml":
            pass
        elif element.type == "Json":
            pass
        elif element.type == "App":
            pass
        elif element.type == "Poke":
            pass
        elif element.type == "Dice":
            pass
        elif element.type == "MusicShare":
            pass
        elif element.type == "Forward":
            pass
        else:
            raise NotImplementedError()
    return message


def to_sender(
    contact: Contact, sender: Sender
) -> Union[Friend, Member, Client, Stranger]:
    """这里有bug，kritor的element.scene永远为0，这里workaround想办法

    Args:
        contact (Contact): _description_
        sender (Sender): _description_

    Raises:
        NotImplementedError: _description_

    Returns:
        Union[Friend, Member, Client, Stranger]: _description_
    """
    if contact.scene == Scene.GROUP:
        group = Group(id=int(contact.peer), name="", permission=MemberPerm.Member)
        return Member(
            id=sender.uin,
            memberName=sender.nick,
            permission=MemberPerm.Member,
            group=group,
        )
    elif contact.scene == Scene.FRIEND:
        return Friend(id=sender.uin, nickname=sender.nick, remark="")
    else:
        raise NotImplementedError()


def to_source(message: PushMessageBody) -> Source:
    return Source(
        id=message.message_seq,
        time=datetime.fromtimestamp(message.time),
    )
