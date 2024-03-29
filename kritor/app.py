import asyncio
import inspect
import logging
from typing import Any, Callable, ClassVar, Dict, List, Optional, Union
import uuid
import grpc
import time
from threading import Thread
from concurrent import futures

from kritor.bridge.message import to_message_chain, to_sender, to_source, to_contact, to_message

from .broadcast import Broadcast
from .broadcast.interfaces.dispatcher import DispatcherInterface

import kritor
from kritor.event.message import MessageEvent, FriendMessage, GroupMessage, StrangerMessage, TempMessage, OtherClientMessage
from kritor.handler import KritorHandler
from kritor.message.chain import MessageChain
from kritor.models.options import KritorOptions
from kritor.models.relationship import Friend, Member, Stranger, Group
from kritor.protos.common.contact_pb2 import Contact
from kritor.protos.common.message_element_pb2 import Element, TextElement, AtElement

from kritor.protos.auth.authentication_pb2_grpc import AuthenticationServiceStub
from kritor.protos.auth.authentication_pb2 import GetAuthenticationStateResponse
from kritor.protos.auth.authentication_pb2 import GetAuthenticationStateRequest
from kritor.protos.auth.authentication_pb2 import AuthenticateRequest, AuthenticateResponse
from kritor.protos.auth.authentication_pb2 import GetTicketRequest, GetTicketResponse
from kritor.protos.auth.authentication_pb2 import DeleteTicketRequest, DeleteTicketResponse
from kritor.protos.auth.authentication_pb2 import AddTicketRequest, AddTicketResponse

from kritor.protos.message.message_pb2_grpc import MessageServiceStub
from kritor.protos.message.message_pb2 import SendMessageRequest, SendMessageResponse


from kritor.protos.event.event_pb2_grpc import EventServiceStub, EventServiceServicer, add_EventServiceServicer_to_server
from kritor.protos.event.event_pb2 import RequestPushEvent, EventStructure, EventType
from kritor.typing import class_property

class KritorAsyncEventServiceServicer(EventServiceServicer):
    async def RegisterPassiveListener(self, request_iterator, context: grpc.aio.ServicerContext):
        for request in request_iterator:
            print(request.type)
        return RequestPushEvent(type=1)

class KritorEventServiceServicer(EventServiceServicer):
    def RegisterPassiveListener(self, request_iterator, context: grpc.aio.ServicerContext):
        for request in request_iterator:
            print(request.type)
        return RequestPushEvent(type=1)
        # raise NotImplementedError('Method not implemented!')

class KritorApp(object):
    def __init__(self,
                 account: str,
                 ticket: str,
                 host: str,
                 port: int,
                 server_host: Union[str]=None,
                 server_port: Union[int]=None,
                 passive:bool = False,
                 max_workers: int = 10
            ) -> None:
        self.account = account
        self.ticket = ticket

        self.host = host
        self.port = port

        self.server_host = server_host
        self.server_port = server_port

        self.passive = passive
        self.debug = True
        self.max_workers = max_workers
        self.target = f"{host}:{port}"

        self.event_system = Broadcast()
        self.running = True
        # Coroutines to be invoked when the event loop is shutting down.
        self._cleanup_coroutines = []
    
    @property
    def broadcast(self) -> Broadcast:
        """获取事件系统.

        Returns:
            Broadcast: 事件系统
        """
        return self.event_system
    
    def _call_event(self, event: str, args: List[Any], kargs: Dict[str, Any]):
        if event not in self.event_handlers:
            return
        for handler in self.event_handlers[event]:
            if handler.is_sync:
                handler.call(*args, **kargs)
    
    async def _acall_event(self, event: str, args: List[Any], kargs: Dict[str, Any]):
        if event not in self.event_handlers:
            return
        for handler in self.event_handlers[event]:
            if handler.is_sync:
                handler.call(*args, **kargs)
            else:
                await handler.acall(*args, **kargs)
    
    def _run_info(self, host: str, port: int, debug=False):
        lines = []
        lines.append("* Serving Kritor app")
        lines.append(f"* Passive mode: {self.passive}")
        lines.append(f"* Debug mode: {self.debug}")
        lines.append(f"* Running on {host}:{port} (CTRL + C to quit)")
        print("\n".join(lines))

    def _serve_active(self, host: str, port: int) -> None:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.max_workers))
        add_EventServiceServicer_to_server(KritorEventServiceServicer(), server)
        server.add_insecure_port(f"{host}:{port}")
        server.start()
        server.wait_for_termination()

    async def _aserve_active(self, host: str, port: int) -> None:
        server = grpc.aio.server()
        add_EventServiceServicer_to_server(KritorAsyncEventServiceServicer(), server)
        server.add_insecure_port(f"{host}:{port}")
        await server.start()

        async def server_graceful_shutdown():
            print("Starting graceful shutdown...")
            # Shuts down the server with 5 seconds of grace period. During the
            # grace period, the server won't accept new connections and allow
            # existing RPCs to continue within the grace period.
            await server.stop(5)

        self._cleanup_coroutines.append(server_graceful_shutdown())
        await server.wait_for_termination()
    
    async def _broadcast_message(self, event: EventStructure):
        message_chain = to_message_chain(event.message.elements)
        sender = to_sender(event.message.contact, event.message.sender)
        source = to_source(event.message)
        if isinstance(sender, Friend):
            await self.broadcast.postEvent(
                FriendMessage(
                    messageChain=message_chain,
                    sender=sender,
                    source=source,
                    quote=None
                )
            )
        elif isinstance(sender, Member):
            await self.broadcast.postEvent(
                GroupMessage(
                    messageChain=message_chain,
                    sender=sender,
                    source=source,
                    quote=None
                )
            )
        elif isinstance(sender, Stranger):
            await self.broadcast.postEvent(
                StrangerMessage(
                    messageChain=message_chain,
                    sender=sender,
                    source=source,
                    quote=None
                )
            )
    
    def _thread_core_event(self):
        with grpc.insecure_channel(self.target) as channel:
            stub = EventServiceStub(channel)
            core_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_CORE_EVENT))
            core_event_iter = iter(core_event_list)
            try:
                while self.running:
                    try:
                        event: EventStructure = next(core_event_iter)
                    except StopIteration:
                        pass
                    time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                return
    
    def _thread_message_event(self):
        loop = asyncio.new_event_loop()
        with grpc.insecure_channel(self.target) as channel:
            stub = EventServiceStub(channel)
            message_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_MESSAGE))
            message_event_iter = iter(message_event_list)
            try:
                while self.running:
                    try:
                        event: EventStructure = next(message_event_iter)
                        loop.run_until_complete(self._broadcast_message(event=event))
                    except StopIteration:
                        pass
            except (KeyboardInterrupt, SystemExit):
                return
    
    def _thread_notice_event(self):
        with grpc.insecure_channel(self.target) as channel:
            stub = EventServiceStub(channel)
            notice_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_NOTICE))
            notice_event_iter = iter(notice_event_list)
            try:
                while self.running:
                    try:
                        event: EventStructure = next(notice_event_iter)
                    except StopIteration:
                        pass
                    time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                return
    
    def _thread_request_event(self):
        with grpc.insecure_channel(self.target) as channel:
            stub = EventServiceStub(channel)
            request_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_NOTICE))
            request_event_iter = iter(request_event_list)
            try:
                while self.running:
                    try:
                        event: EventStructure = next(request_event_iter)
                    except StopIteration:
                        pass
                    time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                return
    
    def _serve_passive(self) -> None:
        core_t = Thread(target=self._thread_core_event, args=[], daemon=True)
        message_t = Thread(target=self._thread_message_event, args=[], daemon=True)
        notice_t = Thread(target=self._thread_notice_event, args=[], daemon=True)
        request_t = Thread(target=self._thread_request_event, args=[], daemon=True)

        threads = [core_t, message_t, notice_t, request_t]

        # Start all threads.
        for t in threads:
            t.start()

        try:
            while True:
                time.sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
            self.running = False
            # Wait for all threads to finish.
            for t in threads:
                t.join(timeout=3)
                if t.is_alive():
                    print("Threading join timeout.")

    async def _aserve_passive(self) -> None:
        core_t = Thread(target=self._thread_core_event, args=[], daemon=True)
        message_t = Thread(target=self._thread_message_event, args=[], daemon=True)
        notice_t = Thread(target=self._thread_notice_event, args=[], daemon=True)
        request_t = Thread(target=self._thread_request_event, args=[], daemon=True)

        threads = [core_t, message_t, notice_t, request_t]

        # Start all threads.
        for t in threads:
            t.start()

        try:
            while True:
                await asyncio.sleep(0.1)
        except (KeyboardInterrupt, SystemExit):
            self.running = False
            # Wait for all threads to finish.
            for t in threads:
                t.join(timeout=3)
                if t.is_alive():
                    print("Threading join timeout.")

    def run(self, host: str, port: int) -> None:
        self._run_info(host=host, port=port)
        if self.passive:
            self._serve_passive()
        else:
            self._serve_active(host=host, port=port)

    async def arun(self, host: str, port: int) -> None:
        self._run_info(host=host, port=port)
        if self.passive:
            await self._aserve_passive()
        else:
            await self._aserve_active(host=host, port=port)
    
    def launch_blocking(self, sync=True):
        if sync:
            self.run(self.server_host, self.server_port)
        else:
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(self.arun(self.server_host, self.server_port))
            finally:
                loop.run_until_complete(*self._cleanup_coroutines)
                loop.close()
    
    # Auth
    def authenticate(self, account: str, ticket: str) -> bool:
        with grpc.insecure_channel(self.target) as channel:
            stub = AuthenticationServiceStub(channel)
            out: GetAuthenticationStateResponse = stub.GetAuthenticationState(GetAuthenticationStateRequest(account = account))
            if out.is_required:
                out = stub.Authenticate(AuthenticateRequest(account = account, ticket = ticket))
                return False
            return out.is_required

    def auth(self, account: str, ticket: str) -> AuthenticateResponse:
        with grpc.insecure_channel(self.target) as channel:
            stub = AuthenticationServiceStub(channel)
            out = stub.Authenticate(AuthenticateRequest(account = account, ticket = ticket))
            return out

    def get_auth_state(self, account: str) -> GetAuthenticationStateResponse:
        with grpc.insecure_channel(self.target) as channel:
            stub = AuthenticationServiceStub(channel)
            out = stub.GetAuthenticationState(GetAuthenticationStateRequest(account = account))
            return out

    def get_ticket(self, account: str, ticket: str) -> GetTicketResponse:
        with grpc.insecure_channel(self.target) as channel:
            stub = AuthenticationServiceStub(channel)
            out = stub.GetTicket(GetTicketRequest(account = account, ticket = ticket))
            return out
    
    # Message
    def send_message_sync(self, target: Union[Friend, Group], message: Union[MessageChain, str], retry_count:int = 3) -> SendMessageResponse:
        with grpc.insecure_channel(self.target) as channel:
            stub = MessageServiceStub(channel)
            contact = to_contact(target)
            if isinstance(message, str):
                elements = [Element(type=Element.ElementType.TEXT, text=TextElement(text=message))]
            else:
                elements = to_message(message)
            out = stub.SendMessage(
                SendMessageRequest(
                    contact = contact,
                    elements = elements,
                    retry_count=retry_count
                )
            )
            return out

    async def send_message(self, target: Union[Friend, Group], message: Union[MessageChain, str], retry_count:int = 3) -> SendMessageResponse:
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = MessageServiceStub(channel)
            contact = to_contact(target)
            if isinstance(message, str):
                elements = [Element(type=Element.ElementType.TEXT, text=TextElement(text=message))]
            else:
                elements = to_message(message)
            out = await stub.SendMessage(
                SendMessageRequest(
                    contact = contact,
                    elements = elements,
                    retry_count=retry_count
                )
            )
            return out
