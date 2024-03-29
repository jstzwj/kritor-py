

from datetime import datetime
from typing import List, Union
from kritor.message import Source
from kritor.message.chain import MessageChain
from kritor.message.element import Plain, At, AtAll
from kritor.models.relationship import Client, Friend, Group, Member, Stranger, MemberPerm
from kritor.protos.common.message_data_pb2 import PushMessageBody
from kritor.protos.common.message_element_pb2 import Element, TextElement, AtElement, FaceElement
from kritor.protos.common.contact_pb2 import Contact, Sender, Scene

def to_contact(target: Union[Friend, Group]) -> Contact:
    if isinstance(target, Group):
        return Contact(scene=Scene.GROUP, peer=str(target.id))
    elif isinstance(target, Friend):
        return Contact(scene=Scene.FRIEND, peer=str(target.id))
    else:
        raise NotImplementedError()

def to_message_chain(elements: List[Element]) -> MessageChain:
    message_chain = MessageChain([])
    for element in elements:
        if element.type == Element.ElementType.TEXT:
            message_chain.content.append(Plain(text=element.text.text))
        elif element.type == Element.ElementType.AT:
            message_chain.content.append(At(target=element.at.uid))
        else:
            raise NotImplementedError()
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

def to_sender(contact: Contact, sender: Sender) -> Union[Friend, Member, Client, Stranger]:
    if contact.scene == Scene.GROUP:
        group = Group(
            id=int(contact.peer),
            name="",
            permission=MemberPerm.Member
        )
        return Member(
            id=sender.uin,
            memberName=sender.nick,
            permission=MemberPerm.Member,
            group=group
        )
    elif contact.scene == Scene.FRIEND:
        return Friend(
            id=sender.uin, 
            nickname=sender.nick, 
            remark=""
        )
    else:
        raise NotImplementedError()

def to_source(message: PushMessageBody) -> Source:
    return Source(
        id=message.message_seq,
        time=datetime.fromtimestamp(message.time),
    )