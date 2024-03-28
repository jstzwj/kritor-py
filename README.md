# Kritor-py

**Kritor** （OneBotX）是一个聊天机器人应用接口标准，
旨在统一腾讯QQ IM平台上的机器人应用开发接口 ，
使开发者只需编写一次业务逻辑代码即可应用到多种机器人平台。

**Kritor-py** 是一个**Kritor**在Python3上的实现。

## 客户端代码示例

建立一个管道，实例化Grpc的服务，发送一个鉴权请求。

```python
import grpc
from kritor.protos.auth.authentication_pb2_grpc import AuthenticationServiceStub

with grpc.insecure_channel(self.target) as channel:
    stub = AuthenticationServiceStub(channel)
    out = stub.Authenticate(AuthenticateRequest(account = "1145141919810", ticket = "A123456"))
    print(out.msg)
```

## 使用项目

- [Shamrock](https://github.com/whitechi73/OpenShamrock)