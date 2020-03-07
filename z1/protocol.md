# Protocol

## Generic message format
```
0    2    3               3 + CL
+----+----+----------~  ~-+
| CL | MT | Content       |
+----+----+----------~  ~-+
```
* CL - payload length - length of content in bytes (network byte order), might be 0 if it is required or permitted by MT
* MT - message type - type of message, one of described below
* Content - as defined in MT, length = CL

## Message types

### `MT=0` Hello server
First packet sent from client to server. Content = UTF8-encoded nickname. 

### `MT=1` General Client
Sent by server to client. No content. 
Client can send/receive messages after receiving this message

### `MT=2` Message client -> server
Sent by client, contains message that will be sent to all clients.

### `MT=3` Message server -> client
Sent by server, contains message that is sent to client.