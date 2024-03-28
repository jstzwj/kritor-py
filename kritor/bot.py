import asyncio
import inspect
import logging
from typing import Any, Callable, Dict, List
import uuid
import grpc
import time
from concurrent import futures

from kritor.handler import KritorHandler
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

class KritorBot(object):
    def __init__(self, host: str, port: int, passive:bool = False, max_workers: int = 10) -> None:
        self.host = host
        self.port = port
        self.passive = passive
        self.debug = True
        self.max_workers = max_workers
        self.target = f"{host}:{port}"

        self.event_handlers: Dict[str, List[KritorHandler]] = {}
        # Coroutines to be invoked when the event loop is shutting down.
        self._cleanup_coroutines = []
    
    def register_handler(self, event_name: str, handler: Callable[[Any], Any]) -> str:
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        h = KritorHandler(handler)
        self.event_handlers[event_name].append(h)
        return h.get_handler_id()
    
    def remove_handler(self, handler_id: str):
        for event_name, handlers in self.event_handlers.items():
            i = 0
            while i < len(handlers):
                if handlers[i].get_handler_id() == handler_id:
                    del handlers[i]
                    break
                i += 1
    
    def clear_handlers(self, event_name: str) -> None:
        if event_name in self.event_handlers:
            self.event_handlers[event_name].clear()
    
    def on_core(self, fn: Callable[[Any], Any]) -> str:
        return self.register_handler("core", fn)

    def on_message(self, fn: Callable[[Any], Any]) -> str:
        return self.register_handler("message", fn)

    def on_notice(self, fn: Callable[[Any], Any]) -> str:
        return self.register_handler("notice", fn)
    
    def on_request(self, fn: Callable[[Any], Any]) -> str:
        return self.register_handler("request", fn)
    
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
    
    def _serve_passive(self) -> None:
        with grpc.insecure_channel(self.target) as channel:
            stub = EventServiceStub(channel)
            
            core_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_CORE_EVENT))
            message_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_MESSAGE))
            notice_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_NOTICE))
            request_event_list = stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_REQUEST))

            core_event_iter = iter(core_event_list)
            message_event_iter = iter(message_event_list)
            notice_event_iter = iter(notice_event_list)
            request_event_iter = iter(request_event_list)
            while True:
                try:
                    event = next(core_event_iter)
                    self._call_event("core", args=[], kargs={})
                except StopIteration:
                    continue
                
                try:
                    event = next(message_event_iter)
                    self._call_event("message", args=[], kargs={"message": event.message})
                except StopIteration:
                    continue
                
                try:
                    event = next(notice_event_iter)
                    self._call_event("notice", args=[], kargs={"notice": event.notice})
                except StopIteration:
                    continue
                
                try:
                    event = next(request_event_iter)
                    self._call_event("request", args=[], kargs={"request": event.request})
                except StopIteration:
                    continue

                time.sleep(0.1)

    async def _aserve_passive(self) -> None:
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = EventServiceStub(channel)
            while True:
                event_list = await stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_CORE_EVENT))
                for event in event_list:
                    await self._acall_event("core", args=[], kargs={})
                
                event_list = await stub.RegisterActiveListener(RequestPushEvent(type=EventType.EVENT_TYPE_MESSAGE))
                for event in event_list:
                    await self._acall_event("message", args=[], kargs={"message": event.message})
                
                await asyncio.sleep(0.1)

    def run(self, host: str, port: int) -> None:
        self._run_info(host=host, port=port)
        if self.passive:
            self._serve_passive()
        else:
            self._serve_active(host=host, port=port)

    async def arun(self, host: str, port: int) -> None:
        self._run_info(host=host, port=port)
        if self.passive:
            await self._serve_passive()
        else:
            await self._aserve_active(host=host, port=port)
    
    # Auth
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
    def send_message(self) -> SendMessageResponse:
        with grpc.insecure_channel(self.target) as channel:
            stub = MessageServiceStub(channel)
            contact = Contact(scene=0, peer="")
            out = stub.SendMessage(SendMessageRequest(contact = contact, elements = [Element(type=0, text=TextElement(text="你好，世界"))], retry_count=3))
            return out
