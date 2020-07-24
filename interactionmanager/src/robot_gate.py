from robot import Robot
from naoqi import ALModule
from time import sleep

# TODO: Eyeblinking, Facedetection


class NaoRobotGate(ALModule):
    # static look_at positions for the study setting
    _look_pos = {"tablet": (1.0, 0.1, -1.0), "user": (1.0, 0.5, 0.0)}

    def __init__(self, name, interaction_manager):
        ALModule.__init__(self, name)
        self._interaction_manager = interaction_manager
        self._name = name
        self._speech_count = 0

        # register all necessary event handlers
        self._register_event_handler()

    def _register_event_handler(self):
        """
            Register all event-handlers
        """
        Robot.memoryProxy.subscribeToEvent("animated_tts", self._name, "animated_tts_event")
        Robot.memoryProxy.subscribeToEvent("test", self._name, "test_event")
        Robot.memoryProxy.subscribeToEvent("test", self._name, "test_event")
        Robot.memoryProxy.subscribeToEvent("describe_object", self._name, "describe_object_event")
        Robot.memoryProxy.subscribeToEvent("skip_object", self._name, "skip_object_event")
        Robot.memoryProxy.subscribeToEvent("explain_skill2", self._name, "explain_skill_event2")
        Robot.memoryProxy.subscribeToEvent("explain_skill", self._name, "explain_skill_event")
        Robot.memoryProxy.subscribeToEvent("dialog_stop", self._name, "stop_tts_event")
        Robot.memoryProxy.subscribeToEvent("motivate_request", self._name, "motivate_request_event")
        Robot.memoryProxy.subscribeToEvent("sing_a_song", self._name, "sing_a_song_event")
        Robot.memoryProxy.subscribeToEvent("test_run", self._name, "test_run_event")
        Robot.memoryProxy.subscribeToEvent("repeat_answer", self._name, "repeat_answer_event")
        Robot.memoryProxy.subscribeToEvent("look_at", self._name, "look_at_event")
        Robot.memoryProxy.subscribeToEvent("round_nr", self._name, "round_number_update_event")
        Robot.memoryProxy.subscribeToEvent("experiment_done", self._name, "experiment_done_event")
        Robot.memoryProxy.subscribeToEvent("log", self._name, "log_event")
        Robot.memoryProxy.subscribeToEvent("start_post_test", self._name, "start_post_test_event")
        Robot.memoryProxy.subscribeToEvent("end_post_test", self._name, "end_post_test_event")
        Robot.memoryProxy.subscribeToEvent("start_pre_test", self._name, "start_pre_test_event")
        Robot.memoryProxy.subscribeToEvent("end_pre_test", self._name, "end_pre_test_event")
        Robot.memoryProxy.subscribeToEvent("log_ping", self._name, "log_ping_event")
        Robot.memoryProxy.subscribeToEvent("log_reengage_button", self._name, "log_reengage_button_event")
        Robot.memoryProxy.subscribeToEvent("post_test_target_word", self._name, "post_test_target_word_event")
        Robot.memoryProxy.subscribeToEvent("log_vad_answer", self._name, "log_vad_answer_event")

    ###################################################
    # Start of event-handlers
    ###################################################
    def post_test_target_word_event(self, key, value):
        self._interaction_manager._post_test_target_word = value

    def log_ping_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("===VideoSync===")
        self._interaction_manager.log("=====================================================================")


    def test_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("===TESTESTESTESTS===")
        self._interaction_manager.log("=====================================================================")        

    def log_vad_answer_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("[vad_button_press]"+value)
        self._interaction_manager.log("=====================================================================")

    def log_reengage_button_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("[reengage_button_press]"+value)
        self._interaction_manager.log("=====================================================================")

    def end_post_test_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("===End-Post-Test===")
        self._interaction_manager.log("=====================================================================")

    def start_post_test_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("===Post-Test===")
        self._interaction_manager.log("=====================================================================")

    def end_pre_test_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("===End-Pre-Test===")
        self._interaction_manager.log("=====================================================================")

    def start_pre_test_event(self, key, value):
        self._interaction_manager.log("=====================================================================")
        self._interaction_manager.log("===Pre-Test===")
        self._interaction_manager.log("=====================================================================")

    def log_event(self, key, value):
        print()
        print "dit is gelogt: " + value
        self._interaction_manager.log(value)

    def experiment_done_event(self, key):
        self._interaction_manager.stop()

    def round_number_update_event(self, key, value):
        self._interaction_manager.update_round_number(int(value))

    def look_at_event(self, key, value):
        """
            Look to the specified point.

            :param value: could be 'user' or 'tablet'
        """
        Robot.trackerProxy.lookAt(NaoRobotGate._look_pos[value], 0, 0.1, False)

    def repeat_answer_event(self, key, value):
        """
            Repeat the answer and say "fesuti means red"
        """
        self._interaction_manager.repeat_answer()

    def test_run_event(self, key, value):
        """
            Switch to test-mode of the system to make sure the user understood the task.
        """
        self._interaction_manager.switch_test_run_activation(value)

    def sing_a_song_event(self, key, value):
        """
            Not implemented yet. Only a placeholder.
        """
        sleep(1)
        self.action_finished()

    def motivate_request_event(self, key, value):
        """
            Ask if the child have to be motivated? If yes --> do something
        """
        self._interaction_manager.motivate_request()

    def stop_tts_event(self, key, value):
        """
            Stops the current tts of the robot.
        """
        Robot.TTSProxy.stopAll()

    def skip_object_event(self, key, value):
        """
            If the user decides to try another task, skip the current one.
        """
        self._interaction_manager.skip_explanation()

    def animated_tts_event(self, key, value):
        """
            Send the given event-value to the animated tts proxy.

            :param value:
        """
        self._speech_count += 1
        self.animated_tts(value)

    def explain_skill_event(self, key, value):
        """
            Make an explanation task including a new tablet content.
        """
        self._interaction_manager.give_explanation()

    def explain_skill_event2(self, key, value):
        """
            Make an explanation task including a new tablet content.
        """
        self._interaction_manager.test_logger("hoi")        

    def describe_object_event(self, key, value):
        """
            Give a new task.
        """
        self._interaction_manager.give_task()

    ###################################################
    # End of event-handlers
    ###################################################

    def stand_up(self, breath=True):
        """
            Let the Nao stand up and maybe breath. For the breath the head is excluded to not interrupt possible
            look_at behavior.

            :param breath: True     robot breath
                           False    else
        """
        Robot.robotPostureProxy.goToPosture("StandInit", 1.0)
        Robot.motionProxy.setBreathEnabled('Body', breath)
        Robot.motionProxy.setBreathEnabled('Head', False)

    def crouch(self):
        """
            Let the robot crouch.
        """
        Robot.robotPostureProxy.goToPosture("Crouch", 1.0)

    def sit(self):
        """
            Let the robot sit down.
        """
        Robot.robotPostureProxy.goToPosture("Sit", 1.0)

    def animated_tts(self, text, body_language_mode="contextual"):
        """
            Let the nao say a text including some "body-language".

            :param text: The text to say.
            :param body_language_mode: Optional body-language option. Default is "contextual".
                                       Possible values could be found at
                                       http://doc.aldebaran.com/2-1/naoqi/audio/alanimatedspeech.html#body-language

        """
        print "tts", text
        config = {"bodyLanguageMode": body_language_mode}
        Robot.animatedTTSProxy.say(text, config)

    def change_language(self, lang):
        """
            Function for changing the language of the robot.

            :param lang: The new language of the robot-tts.
        """
        #Robot.TTSProxy.setLanguage(lang)
        # Jan: language should not be changed from interaction manager anymore.
        pass

    def raise_event(self, event, value):
        Robot.memoryProxy.raiseEvent(event, value)

    def action_finished(self):
        """
            Send an event, that the last action to be done is finished so the dialog
            flow could go on. This is used for example after doing some non-verbal behavior etc.
        """
        Robot.memoryProxy.raiseEvent("action/finished", 1)

    def setGestureCondition(self, value):
        """
            Send an event, that the last action to be done is finished so the dialog
            flow could go on. This is used for example after doing some non-verbal behavior etc.
        """
        Robot.memoryProxy.raiseEvent("gesture_condition", value)
