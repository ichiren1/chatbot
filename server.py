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
import re
is_zero = False

client = set()

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
ZERO = ord("0")
NINE = ord("9")
define("port", default = 8080, help = "run on the given port", type = int)

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

class SendWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        client.add(self)
        print("WebSocket opened") 

    def on_message(self, message):
        global is_zero
        receive = ""
        data = {}
        data['data'] = message
        print(data)
        [ws.write_message(json.dumps(data)) for ws in client]
        if message.startswith("bot"):
            commands = message.split()
            if len(commands) == 2:
                if commands[1] == "ping":
                    data['data'] = "pong"
                    [ws.write_message(json.dumps(data)) for ws in client]
            command = {}
            if len(commands) == 3:
                if commands[1] == "todo" and commands[2] == "list":
                    cur.execute("select name, content from todo")
                    result = cur.fetchall()
                    if len(result)==0:
                        receive = "todo empty"
                    else:
                        receive = "\n".join([n+" "+c for n, c in [row for row in result]])
                    data['data'] = receive
                    [ws.write_message(json.dumps(data)) for ws in client]
                elif commands[1] != "calc":
                    command['command'] = commands[1]
                    command['data'] = commands[2]
                    bot = Bot(command)
                    bot.generate_hash()
                    data['data'] = bot.hash
                    [ws.write_message(json.dumps(data)) for ws in client]
            if len(commands) >= 3:
                if commands[1] == "calc":
                    data['data'] = calc("".join(commands[2:]))
                    if is_zero:
                        data['data'] = "ERROR: division by zero"
                    [ws.write_message(json.dumps(data)) for ws in client]
                    is_zero = False
            if len(commands) == 4:
                if commands[1] == "todo" and commands[2] == "delete":
                    cur.execute("delete from todo where name='%s'" % commands[3])
                    connector.commit()
                    status, num = cur.statusmessage.split()
                    if status == "DELETE" and int(num) > 0:
                        data['data'] = "todo deleted"
                        [ws.write_message(json.dumps(data)) for ws in client]
            if len(commands) >= 5:
                if commands[1] == "todo" and commands[2] == "add":
                    cur.execute("insert into todo values('%s','%s')" % (commands[3], " ".join(commands[4:])))
                    connector.commit()
                    status, num1, num2 = cur.statusmessage.split()
                    if status == "INSERT" and int(num2) > 0:
                        data['data'] = "todo added"
                        [ws.write_message(json.dumps(data)) for ws in client]

    def on_close(self):
        client.remove(self)
        print("WebSocket closed")

app = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/", SendWebSocket),
],
template_path=os.path.join(os.getcwd(), "templates"),
static_path=os.path.join(os.getcwd(), "static"),
)

def paren(st):
    if st[0] == "(":
        ans, idx = first(st[1:])
        return ans, idx+2
    elif ZERO <= ord(st[0]) <= NINE:
        i = 1
        while i < len(st) and ZERO <= ord(st[i]) <= NINE:
            i += 1
        return int(st[:i]), i
    return 0, 0

def second(st):
    global is_zero
    ans, idx = paren(st)

    i = idx
    while i < len(st):
        if st[i] == "*":
            tmp, idx = paren(st[i+1:])
            ans *= tmp
            i += idx+1
        elif st[i] == "/":
            tmp, idx = paren(st[i+1:])
            if tmp == 0:
                is_zero = True
            else:
                ans /= tmp
            i += idx+1
        elif st[i] == "%":
            tmp, idx = paren(st[i+1:])
            if tmp == 0:
                is_zero = True
            else:
                ans %= tmp
            i += idx+1
        elif st[i] == "^":
            tmp, idx = paren(st[i+1:])
            ans = pow(ans,tmp)
            i += idx+1
        else:
            return ans, i
    return ans, i

def first(st):
    ans, idx = second(st)

    i = idx
    while i < len(st):
        if st[i] == "+":
            tmp, idx = second(st[i+1:])
            ans += tmp
            i += idx+1
        elif st[i] == "-":
            tmp, idx = second(st[i+1:])
            ans -= tmp
            i += idx+1
        else:
            return ans, i
    return ans, i
    
def calc(s):
    if s.count("(") != s.count(")") or re.search("[^\+\-\*\/()0-9^%]", s):
        return "ERROR"
    else:
        return first(s)[0]


if __name__ == "__main__":
    parse_command_line()
    port = int(os.environ.get("PORT", 5000))
    print("Listen :%d" % port)
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()