import os
import json
import time
import tornado.ioloop
import tornado.web
import tornado.websocket
from bot import *
from tornado.ioloop import PeriodicCallback

from tornado.options import define, options, parse_command_line

define("port", default = 8080, help = "run on the given port", type = int)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class SendWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened") 

    def on_message(self, message):
        if message.startswith("bot"):
            commands = message.split()
            command = {}
            if len(commands) == 3:
                command['command'] = commands[1]
                command['data'] = commands[2]
                bot = Bot(command)
                bot.generate_hash()
                message = bot.hash
        data = {}
        data['data'] = message
        print(data)
        self.write_message(json.dumps(data))

    def on_close(self):
        print("WebSocket closed")

app = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/ws", SendWebSocket),
],
template_path=os.path.join(os.getcwd(), "templates"),
static_path=os.path.join(os.getcwd(), "static"),
)

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()