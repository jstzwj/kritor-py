import grpc
from concurrent import futures

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

class KritorBot(object):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.target = f"{host}:{port}"
    
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
    