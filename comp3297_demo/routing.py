from channels.routing import route
from tutoria.consumers import ws_connect, ws_disconnect, ws_echo


channel_routing = [
    route('websocket.connect', ws_connect, path=r"^/(?P<userID>[a-zA-Z0-9_]+)$"),
    route('websocket.disconnect', ws_disconnect, path=r"^/(?P<userID>[a-zA-Z0-9_]+)$"),
    route('websocket.receive', ws_echo, path=r"^/(?P<userID>[a-zA-Z0-9_]+)$"),
]