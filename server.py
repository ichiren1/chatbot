import json
import time
import tornado.ioloop
import tornado.web
import tornado.websocket
from bot import *
from tornado.ioloop import PeriodicCallback
from tornado.options import define, options, parse_command_line
import urllib.parse
import psycopg2
import os

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
connector = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
cur = connector.cursor()

define("port", default = 8080, help = "run on the given port", type = int)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class SendWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened") 

    def on_message(self, message):
        receive = message
        if message.startswith("bot"):
            commands = message.split()
            if len(commands) == 2:
                if commands[1] == "ping":
                    data = {}
                    data['data'] = receive
                    print(data)
                    self.write_message(json.dumps(data))
                    receive = "pong"
            command = {}
            if len(commands) == 3:
                if commands[1] == "todo" and commands[2] == "list":
                    cur.execute("select name, content from todo")
                    result = cur.fetchall()
                    if len(result)==0:
                        receive = "todo empty"
                    else:
                        receive = "\n".join([n+" "+c for n, c in [row for row in result]])
                else:
                    command['command'] = commands[1]
                    command['data'] = commands[2]
                    bot = Bot(command)
                    bot.generate_hash()
                    receive = bot.hash
            elif len(commands) == 4:
                if commands[1] == "todo" and commands[2] == "delete":
                    cur.execute("delete from todo where name='%s'" % commands[3])
                    connector.commit()
                    status, num = cur.statusmessage.split()
                    if status == "DELETE" and int(num) > 0:
                        receive = "todo deleted"
            elif len(commands) >= 5:
                if commands[1] == "todo" and commands[2] == "add":
                    cur.execute("insert into todo values('%s','%s')" % (commands[3], " ".join(commands[4:])))
                    connector.commit()
                    status, num1, num2 = cur.statusmessage.split()
                    if status == "INSERT" and int(num2) > 0:
                        receive = "todo added"
        data = {}
        data['data'] = receive
        print(data)
        self.write_message(json.dumps(data))

    def on_close(self):
        print("WebSocket closed")

app = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/", SendWebSocket),
],
template_path=os.path.join(os.getcwd(), "templates"),
static_path=os.path.join(os.getcwd(), "static"),
)

if __name__ == "__main__":
    parse_command_line()
    port = int(os.environ.get("PORT", 5000))
    print("Listen :%d" % port)
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()