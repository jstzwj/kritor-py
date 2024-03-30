from datetime import datetime
from typing import List, Union
from kritor.message import Source
from kritor.message.chain import MessageChain
from kritor.message.element import Plain, At, AtAll, Face, Quote, Image
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
                FaceElement(
                    id=element.face.id,
                    is_big=element.face.is_big,
                    result=element.face.result,
                )
            )
        elif data_field == "bubble_face":  # element.type == Element.ElementType.BUBBLE_FACE
            message_chain.content.append(
                BubbleFaceElement(
                    target=element.bubble_face.id,
                    count=element.bubble_face.count,
                )
            )
        elif data_field == "reply":  # element.type == Element.ElementType.REPLY
            message_chain.content.append(
                ReplyElement(
                    message_id=element.reply.message_id,
                )
            )
        elif data_field == "image":  # element.type == Element.ElementType.IMAGE
            image_data_field = element.image.WhichOneof("data")
            message_chain.content.append(
                ImageElement(
                    file=element.image.file if image_data_field == "file" else None,
                    file_name=element.image.file_name if image_data_field == "file_name" else None,
                    file_path=element.image.file_path if image_data_field == "file_path" else None,
                    file_url=element.image.file_url if image_data_field == "file_url" else None,
                    file_md5=element.image.file_md5,
                    sub_type=element.image.sub_type,
                    type=element.image.type,
                )
            )
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
