from tornado import testing, httpserver, gen, websocket, web
import json
import random

class TestChatHandler(testing.AsyncTestCase):

    @testing.gen_test
    def test_addition(self):
        c = yield websocket.websocket_connect('ws://localhost:5000')
        n1 = random.randrange(100)
        n2 = random.randrange(100)
        ans = n1+n2
        command = "bot calc %d+%d" % (n1, n2)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

    @testing.gen_test
    def test_subtraction(self):
        c = yield websocket.websocket_connect('ws://localhost:5000')
        n1 = random.randrange(100)
        n2 = random.randrange(100)
        ans = n1-n2
        command = "bot calc %d-%d" % (n1, n2)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

    @testing.gen_test
    def test_multiplication(self):
        c = yield websocket.websocket_connect('ws://localhost:5000')
        n1 = random.randrange(100)
        n2 = random.randrange(100)
        ans = n1*n2
        command = "bot calc %d*%d" % (n1, n2)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

        ans = (n1 + n2) * n1
        command = "bot calc (%d+%d)*%d" % (n1, n2, n1)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

    @testing.gen_test
    def test_division(self):
        c = yield websocket.websocket_connect('ws://localhost:5000')
        n1 = random.randrange(1, 100)
        n2 = random.randrange(1, 100)
        ans = n1/n2
        command = "bot calc %d/%d" % (n1, n2)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

        ans = (n1 + n2) / n1
        command = "bot calc (%d+%d)/%d" % (n1, n2, n1)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

        #zero check
        command = "bot calc %d/0" % (n1)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual("ERROR: division by zero", json.loads(result)['data'])

    @testing.gen_test
    def test_surplus(self):
        c = yield websocket.websocket_connect('ws://localhost:5000')
        n1 = random.randrange(1, 100)
        n2 = random.randrange(1, 100)
        ans = n1%n2
        command = "bot calc %d%%%d" % (n1, n2)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])

    @testing.gen_test
    def test_power(self):
        c = yield websocket.websocket_connect('ws://localhost:5000')
        n1 = random.randrange(1, 100)
        n2 = random.randrange(1, 100)
        ans = pow(n1,n2)
        command = "bot calc %d^%d" % (n1, n2)
        c.write_message(command)
        formula = yield c.read_message()
        result = yield c.read_message()
        self.assertEqual(command, json.loads(formula)['data'])
        self.assertEqual(ans, json.loads(result)['data'])
