import cmd
import sys
import threading
import readline
import uuid
import socket


class NetworkMessageSender:

    def __init__(self, socket):
        self.socket = socket
        self.subscribed = []

    def SendRequest(self, message):
        self.socket.sendall((message + '\n').encode())


class NetworkMessageReceiver:

    def __init__(self, socket):
        self.socket = socket
        self.subscribed = []

    def MakeReceiverThread(self):
        self.stopping_event = threading.Event()
        self.receiver = threading.Thread(target=self.ReceiveMessage,
                                         args=[self.stopping_event])
        self.receiver.start()

    def StopReceiverThread(self):
        self.stopping_event.set()

    def ReceiveMessage(self, event):
        while ((not event.is_set()) and
               (msg := self.socket.recv(1024).decode())):
            # print(msg.strip())
            for subscribed_obj in self.subscribed:
                subscribed_obj.GetMessage(msg)

    def Subscribe(self, obj):
        self.subscribed.append(obj)

    def Unsubscribe(self, obj):
        if obj in self.subscribed:
            self.subscribed.remove(obj)


class Subscriber:

    def GetMessage(self, message):
        pass

    def SubscribeToReceiver(self, receiver):
        self.receiver = receiver
        receiver.Subscribe(self)

    def UnsubscribeFromReceiver(self):
        self.receiver.Unsubscribe(self)


class UnrequestedMessageSubscriber(Subscriber):

    def __init__(self, cmd):
        self.cmd = cmd

    def GetMessage(self, message):
        if message[0] == ' ':
            print(f"\n{message.strip()}\n{self.cmd.prompt}"
                  f"{readline.get_line_buffer()}",
                  end="", flush=True)
            self.UnsubscribeFromReceiver()


class RequestedMessageSubscriber(Subscriber):

    def __init__(self, event, res_id):
        self.event = event
        self.res_id = res_id
        self.message_got = ''

    def GetMessage(self, message):
        if message[0] != ' ' and message.split()[0] == self.res_id:
            if len(message.split()) == 1:
                message = ''
            else:
                _, message = message.split(maxsplit=1)
            self.message_got = message.strip()
            self.event.set()
            self.UnsubscribeFromReceiver()


class CowsayClientCmd(cmd.Cmd):

    def SetNetworkSender(self, sender):
        self.sender = sender

    def SetNetworkReceiver(self, receiver):
        self.receiver = receiver

    def GetRequestUUID(self):
        return str(uuid.uuid4())

    def SendRequestWithResponse(self, message):
        res_id = self.GetRequestUUID()
        event = threading.Event()
        res_getter = RequestedMessageSubscriber(event, res_id)
        res_getter.SubscribeToReceiver(self.receiver)
        self.sender.SendRequest(res_id + ' ' + message)
        event.wait(timeout=5)
        if event.is_set():
            return res_getter.message_got
        else:
            return None

    def SendRequestWithoutResponse(self, message):
        self.sender.SendRequest(' ' + message)

    def do_who(self, arg):
        res = self.SendRequestWithResponse('who')
        if res == None:
            print('Timeout')
        else:
            print(', '.join(res.split()))

    def complete_login(self, text, line, startidx, endidx):
        available_cows = self.SendRequestWithResponse('cows')
        if available_cows is None:
            return []
        available_cows = available_cows.split()
        return [cow for cow in available_cows if cow.startswith(text)]

    def do_login(self, args):
        res = self.SendRequestWithResponse('login ' + args.split()[0])
        if res == None:
            print('Timeout')
        else:
            print(res)

    def do_cows(self, args):
        res = self.SendRequestWithResponse('cows')
        if res == None:
            print('Timeout')
        else:
            print(', '.join(res.split()))

    def complete_say(self, text, line, startidx, endidx):
        if line[:startidx].split() == ['say']:
            res = self.SendRequestWithResponse('who')
            if res is None:
                return []
            else:
                return [cow for cow in res.split()
                        if cow.startswith(text)]

    def do_say(self, args):
        send_to, message = args.split(maxsplit=1)
        logined_cows = self.SendRequestWithResponse('who')
        if logined_cows != None:
            if send_to not in logined_cows.split():
                print('No such cow')
                return
        self.SendRequestWithoutResponse('say ' + send_to + ' ' + message)

    def do_yield(self, args):
        self.SendRequestWithoutResponse('yield ' + args)

    def do_quit(self, args):
        res = self.SendRequestWithResponse('quit')
        if res == None:
            print('Timeout')
        else:
            print(res)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('server hostname not specified')
        exit()
    cmdline = CowsayClientCmd()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((sys.argv[1],
                           sys.argv[2] if len(sys.argv) > 2 else 1337))
    message_receiver = NetworkMessageReceiver(server_socket)
    message_sender = NetworkMessageSender(server_socket)
    cmdline.SetNetworkSender(message_sender)
    cmdline.SetNetworkReceiver(message_receiver)
    unrequested_message_subscriber = UnrequestedMessageSubscriber(cmdline)
    unrequested_message_subscriber.SubscribeToReceiver(message_receiver)
    message_receiver.MakeReceiverThread()
    try:
        cmdline.cmdloop()
    except KeyboardInterrupt:
        message_receiver.StopReceiverThread()
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()
        print('Client off')
