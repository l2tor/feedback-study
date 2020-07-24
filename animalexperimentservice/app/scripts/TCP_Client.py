#!/usr/bin/env python
# coding: utf-8

import socket
from threading import Thread
import logging
import time
import log_formatter as lf
import json
import os
from TCP_CallbackClass import CallbackClass
from Queue import Queue, Empty

runningReading = True


class TCPClient:
    LOG_DIR = "../data/logs/"

    def __init__(self, client_name, interaction_manager, ip="127.0.0.1", port=1111):
        # store reference to interaction manager
        self._im = interaction_manager

        # if log dir doesn't exist ...
        if not os.path.exists(TCPClient.LOG_DIR):
            # ... create it
            os.makedirs(TCPClient.LOG_DIR)
        # new log path
        str_log_file = TCPClient.LOG_DIR + "client-interactionmanager.log"

        # create logger
        logging.basicConfig(filename=str_log_file, level=logging.DEBUG,
                            format='%(levelname)s %(relativeCreated)6d %(threadName)s %(message)s (%(module)s.%(lineno)d)',
                            filemode='w')
        self.logFormatter = lf.LogFormatter(str_log_file, level=lf.DEBUG)
        self.logFormatter.start()
        logging.info("Log initialized")

        # create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip, port)
        # try to connect in a loop with 3 sec sleep
        while True:
            try:
                logging.info("Try to  connect to connectionmanager on %s:%s" % server_address)
                self.sock.connect(server_address)
                logging.info("Connection established!")
                break
            except socket.error, exc:
                logging.info("Connection timeout - retry in 3 seconds.")
                time.sleep(3)

        # list of received messages
        self.a_messages = Queue()

        # start thread to receive messages
        logging.info("Starting thread for receiving messages ...")
        self.t = Thread(target=self.read_messages, args=(self.sock, self.a_messages))
        self.t.start()

        # start thread to evaluate the received messages
        logging.info("Starting thread for handling messages ...")
        self.callback_obj = CallbackClass(self, interaction_manager)
        self.te = Thread(target=self.event_binding, args=(self.callback_obj, self.a_messages))
        self.te.start()

        # register interaction manager at connection manager
        logging.info("register " + client_name)
        self.sendMessage("register:" + client_name)

        # initialize some indicator variables for accepting or refusing different kind of messages
        self.acceptVAD = False
        self.acceptSpRel = False
        self.acceptTouchObjs = False

    @staticmethod
    def read_messages(_socket, a_messages):
        """
            This function receives all messages send over the socket connection.

            :param _socket: The TCP Socket.
            :param a_messages: A list where all messages have to be stored.
        """
        tmp_messages = []
        while runningReading:
            try:
                str_receive = _socket.recv(1024)
                if "#" in str_receive:
                    str_receive = str_receive.split("#")
                    if len(str_receive) > 1:
                        tmp_messages += str_receive[0]
                        a_messages.put("".join(tmp_messages)) if len(tmp_messages) > 1 else a_messages.put(tmp_messages[0])

                        for r in str_receive[1:-1]:
                            a_messages.put(r)
                        logging.info("Current message # on stack: %s" % a_messages.qsize())

                    tmp_messages = [str_receive[-1]]
                else:
                    tmp_messages.append(str_receive)

                time.sleep(0.3)
            except socket.error, e:
                logging.debug("error on socket: " + str(e))

    @staticmethod
    def event_binding(callback, a_messages):
        """
            This method evaluates all send messages and calls the corresponding callback function.

            :param callback: The object which contains all callback functions.
            :param a_messages: The send message with function call.
        """
        while runningReading:
            if not a_messages.empty():
                str_message = a_messages.get_nowait()
                if str_message != "":
                    fields = str_message.split("|")
                    sender, method, params = fields[:3]
                    logging.info("received message %s from %s" % (method, str(sender)))
                    try:
                        getattr(callback, method)(sender, params)
                    except AttributeError:
                        logging.error("Function call %s not found!" % method)
                a_messages.task_done()
            time.sleep(0.1)

    def sendMessage(self, str_message):
        """
            This function sends a messages to the connection manager.

            :param str_message: The message to be send.
        """
        logging.info("send message: %s" % str_message)
        self.sock.sendall(str_message + "#")

    def close_connection(self):
        """
            This function provides a clean close and exit for the TCP client.
        """
        global runningReading
        logging.info("Stop the client")
        runningReading = False
        self.sendMessage("exit")
        self.t.join()
        self.te.join()
        self.sock.close()
        self.logFormatter.stopReadingLogs()

    # ============================================
    STR_OUTPUTMANAGER = "tablet.outputmanager"
    STR_TABLETGAME = "tablet.WebSocket"

    # =============== Perception =================
    # def get_emotions(self):
    #     self.sendMessage("call:tablet.perception.getEmotions")
    #     tmp_data = self.callback_obj.perception_data
    #     while not tmp_data:
    #         tmp_data = self.callback_obj.perception_data
    #     return json.loads(tmp_data)
    # ============================================

    def update_reengage_counter(self, counter):
        self.sendMessage('call:tablet.ControlPanel.updateReengageCounter|%s' % counter)

    # ============= CONTROL PANEL ================
    def memory_loaded(self, user_id, user_name):
        self.sendMessage('call:tablet.ControlPanel.memoryLoaded|[%s, %s]' % (user_id, user_name))
    # ============================================

    # ============= TABLET GAME ==================
    def highlight_objects(self, obj_list):
        _data = {"ids": obj_list}
        self.sendMessage('call:%s.hintObject|%s' % (TCPClient.STR_TABLETGAME, json.dumps(_data)))

    def unhighlight_objects(self, obj_list):
        _data = {"ids": obj_list}
        self.sendMessage('call:%s.hintRObject|%s' % (TCPClient.STR_TABLETGAME, json.dumps(_data)))

    def add_arrow(self, obj_type, source_obj, destination_obj):
        self.sendMessage('call:%s.addArrow|{"type":%s, "source":%s, "destination":%s}' % (TCPClient.STR_TABLETGAME, obj_type, source_obj, destination_obj))

    def show_map(self):
        self.sendMessage('call:%s.showMap' % TCPClient.STR_TABLETGAME)

    def add_object(self, obj_list):
        _data = {"ids": obj_list}
        self.sendMessage('call:%s.showObject|%s' % (TCPClient.STR_TABLETGAME, json.dumps(_data)))

    def remove_object(self, obj_list):
        _data = {"ids": obj_list}
        self.sendMessage('call:%s.hideObject|%s' % (TCPClient.STR_TABLETGAME, json.dumps(_data)))

    def lock_objects(self, obj_list):
        _data = {"ids": obj_list}
        self.sendMessage('call:%s.makeStatic|%s' % (TCPClient.STR_TABLETGAME, json.dumps(_data)))

    def unlock_objects(self, obj_list):
        _data = {"ids": obj_list}
        self.sendMessage('call:%s.makeMovable|%s' % (TCPClient.STR_TABLETGAME, json.dumps(_data)))

    def enable_objects(self, obj_id):
        self.sendMessage('call:%s.enableObject|%s' % (TCPClient.STR_TABLETGAME, obj_id))
    # ============================================

    # ============ OUTPUT MANAGER ================
    def init_output_man(self, file_path, child_name):
        self.sendMessage("call:%s.load_session|%s" % (TCPClient.STR_OUTPUTMANAGER, file_path))
        time.sleep(0.5)
        self.sendMessage("call:%s.set_child_name|%s" % (TCPClient.STR_OUTPUTMANAGER, child_name))

    def give_task(self, task_id, sub_task_id, difficulty_lvl):
        self.sendMessage('call:%s.give_task|{"task": %s, "subtask": %s, "difficulty": %s }' % (TCPClient.STR_OUTPUTMANAGER, task_id, sub_task_id, difficulty_lvl))

    def give_feedback(self, task_result):
        self.sendMessage("call:%s.give_feedback|%s" % (TCPClient.STR_OUTPUTMANAGER, json.dumps(task_result)))

    def request_answer(self, data):
        self.sendMessage("call:%s.request_answer|%s" % (TCPClient.STR_OUTPUTMANAGER, json.dumps(data)))

    def interrupt_output(self, explanation):
        self.sendMessage("call:%s.interrupt_output|%s" % (TCPClient.STR_OUTPUTMANAGER, explanation))

    # not used yet
    def give_break(self, break_activity_id):
        self.sendMessage("call:%s.give_break|%s" % (TCPClient.STR_OUTPUTMANAGER, break_activity_id))

    def resume_interaction(self):
        self.sendMessage("call:%s.resume_interaction|" % TCPClient.STR_OUTPUTMANAGER)

    def give_help(self):
        self.sendMessage("call:%s.giveHelp|" % TCPClient.STR_OUTPUTMANAGER)

    def grab_attention(self):
        self.sendMessage("call:%s.grabAttention|" % TCPClient.STR_OUTPUTMANAGER)
    # ============================================
