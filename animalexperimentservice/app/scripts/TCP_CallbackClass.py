import json
import time


class CallbackClass:

    def __init__(self, sock, interaction_manager):
        self._sock = sock
        self._perception_data = None
        self._im = interaction_manager

    def vadStop(self, sender, data):
        if self._sock.acceptVAD:
            self._sock.acceptVAD = False
            self._im._vad_detected = True

    def vadStart(self, sender, data):
        pass

    def logPing(self, sender, data):
        self._im.s.ALMemory.raiseEvent("log_ping", "")

    def vadFake(self, sender, data):
        """Correct word has been spoken by the child"""
        print "vadFake"
        if self._sock.acceptVAD:
            print "vadFake"
            self._sock.acceptVAD = False
            self._im._vad_detected = True
            self._im._vad_correct = True
            self._im.s.ALMemory.raiseEvent("log_vad_answer", "True")

    def vadFakeFalse(self, sender, data):
        """Wrong word has been spoken by the child"""
        if self._sock.acceptVAD:
            print "vadFakeFalse"
            self._im._vad_detected = True
            self._im._vad_correct = False
            self._im.s.ALMemory.raiseEvent("log_vad_answer", "False")

    def start(self, sender, data):
        self._im.tts_set_language("Dutch")

        # self._im.s.ALRobotPosture.goToPosture("Stand", 0.5)
        # self._im.s.ALAnimatedSpeech.setBodyLanguageMode(0)
        #
        # self._im.s.ALMotion.setBreathEnabled("Head", True)
        # time.sleep(1)
        # self._im.s.ALMotion.setBreathEnabled("Body", True)
        self._im.goto_crouch_with_breath()

        self._im._child_name = data

        self._im.running = True

    def exit(self, sender, data):
        self._im._exit_interaction = True
        if self._im.paused:
            self._im.stop()

    def pause(self, sender, data):
        self._im.paused = True

    def stopAllBehaviors(self, sender, data):
        self._im.s.ALBehaviorManager.stopAllBehaviors()
        self._im.s.ALMotion.setBreathEnabled("Head", False)
        self._im.s.ALMotion.setBreathEnabled("Body", False)
        self._im.s.ALRobotPosture.goToPosture("Crouch", 0.5)
        time.sleep(2)
        self._im.s.ALMotion.stiffnessInterpolation("Body", 0.0, 0.1)

    def resume(self, sender, data):
        print "=== interaction resumed ==="
        self._im.paused = False
        # TODO INTRO EINBEZIEHEN
        if self._im._intro:
            pass
        elif self._im.isLastAnswerWrong:
            self._im.s.ALMemory.raiseEvent("explain_skill", "")
        else:
            self._im.s.ALMemory.raiseEvent("describe_object", "")

    def reengage(self, sender, data):
        print "reengage child because: %s" % data
        self._im._reengage_strategy = data
        self._im.s.ALMemory.raiseEvent("log_reengage_button", data)
