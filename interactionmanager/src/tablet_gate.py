from naoqi import ALModule
from robot import Robot
import logging


class TabletGate(ALModule):
    def __init__(self, name, interaction_manager):
        ALModule.__init__(self, name)
        self._name = name
        self._interaction_manager = interaction_manager

        self._register_event_handler()

    def _register_event_handler(self):
        """
            Register all callback-function for events send from the tablet.
        """
        Robot.memoryProxy.subscribeToEvent("answer", self._name, "answer_event")
        Robot.memoryProxy.subscribeToEvent("answer_time", self._name, "answer_time_event")
        Robot.memoryProxy.subscribeToEvent("berry_dropped", self._name, "berry_dropped_event")

    def berry_dropped_event(self, key, value):
        self._interaction_manager.log_post_test_answer(value)

    def answer_time_event(self, key, value):
        self._interaction_manager.log_answer_time(value)

    def answer_event(self, key, value):
        """
            Callback function for the answer given by the user.

            :param value: The touched object on the screen.
        """
        self._interaction_manager.validate_answer(value)

    def set_task(self, objects):
        """
            This function sends the given list of objects to the tablet so that they could be displayed there.

            :param objects: List of objects. The whole object with all attributes has to be send, so the tablet can
                            determine how to display it.
        """
        self._interaction_manager.log_screen_layout(objects)
        Robot.memoryProxy.raiseEvent("set_images", objects)

    def hide_images(self):
        """
            Send an event to the tablet to hide all shown images.
        """
        Robot.memoryProxy.raiseEvent("show_images", "")

    def show_validation(self, result):
        print("tablet_gate: show_validation: ",result)
        """
            Send the result of the answer-validation to the tablet,
            so it can display some positive or negative feedback.

            :param result: True     if the users answer was correct
                           False    else
        """
        Robot.memoryProxy.raiseEvent("validation", result)

    def show_skilltext(self, skilltext):
        """
            Send the text of the current skill to be taught to the tablet, so it could be displayed on the screen.#

            :param skilltext: The skill-text to be displayed.
        """
        Robot.memoryProxy.raiseEvent("show_skilltext", skilltext)
