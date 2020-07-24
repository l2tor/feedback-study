# -*- coding: utf-8 -*-
from copy import deepcopy
from random import shuffle, randint, seed
import json
import logging


class ChildRandomModel:
    # meaning of each of the 6 probabilities above
    BIN_MEANING = [0., 0.2, 0.4, 0.6, 0.8, 1.]
    # count of bins for each skill-distribution
    BIN_COUNT = len(BIN_MEANING)
    # log-level
    LOG_LEVEL = 21

    def __init__(self, keys):
        # seed(1337) # If you put a seed here, it should work for the random condition!

        """
            Constructor to init the child model

            :param keys: list of all skills to be trained
        """
        self._last_action = None
        # self._actions = {"task_h": "H", "task_m": "M", "probe_skill": "L", "explanation": "E"}
        self._actions = {"task_4": "4", "task_3": "3", "task_2": "2", "task_1": "1"}#, "probe_skill": "L", "explanation": "E"}
        self.round_nr = 0

        # list of skills to be shown on the screen - could be reduced to compare the impact of the displayed words
        self._show_skill_text = deepcopy(keys)

        # list with all skills to be taught
        self._skill_list = keys
        # list with all skills to be taught in random order -
        # here every time some skill will be taught it will be removed
        self._tmp_skill_list = deepcopy(self._skill_list)
        shuffle(self._tmp_skill_list)

        # variable which indicates, if the next run will be a test run or a real task
        self._test_mode = False
        self.finished = (False, False)
        self.recap = False
        self.chunk_changed = False

    def update_round_number(self, number):
        """
            This function updates the internal counter which round is currently played. This number is used
            to make sure every skill will be taught at least once.

            :param number: The new round number.
        """
        self.round_nr = number
        logging.log(self.LOG_LEVEL, "[round_nr]" + str(self.round_nr))

    def get_belief(self, skill):
        """
            During the use of the random model, this function only provides a rudimentary return-value to keep the
            interaction flow running. It's only a dummy function.
        """
        return [1.0, ]

    def get_action_difficulty(self, action):
        """
            Returns the difficult for a specific action.

            :param action: The action for which the difficult should be returned.
            :return: the difficult in one letter
        """
        return self._actions[action]

    def set_test_mode(self, value):
        """
            Switch the mode of the system between test- and real task-mode.

            :param value: True  for test-mode
                          False else
        """
        self._test_mode = value

    def get_last_action(self):
        """
            Getter for the object which stores the last action of the system

            :return: Tuple(skill, action)
        """
        return self._last_action

    def set_last_action(self, action):
        """
            Setter to set the last action of the system

            :param action: Tuple(skill, action)
        """
        self._last_action = action

    def update_belief(self, obs):
        """
            Dummy function to provide the same interface as for the adaptive model to the interaction manager.s
        """
        pass

    def show_skilltext(self, skill):
        """
            Function which proves if for the given skill a skill-text should be shown on the tablet.

            /* from first try .. only display a few skills on the tablet to prove if there is a difference */

            :param skill: The skill to prove...

            :return: True   if should be shown
                     False  else
        """
        return skill in self._show_skill_text

    def update_skill_freq_reduction(self, skill):
        """
            Dummy function to provide the same interface as for the adaptive model to the interaction manager.s
        """
        pass

    def get_next_action(self, logger=True, sim=False):
        """
            This function determine the next skill to taught and with which action it should be done.

            :param logger: True     if the system should log the decision of the function
                           False    else
            :return: The next skill to be taught and the action to do it as a list.
        """
        # if all skills taught, just begin from the scratch again
        if len(self._tmp_skill_list) == 0:
            self._tmp_skill_list = deepcopy(self._skill_list)
            shuffle(self._tmp_skill_list)

        # for the test if the user understood the task, just choose a random skill form the list
        if self._test_mode:
            next_skill = self._skill_list[4] # We use chicken in the introduction  #self._tmp_skill_list[randint(0, len(self._tmp_skill_list)-1)]
        elif not logger:
            next_skill = self._tmp_skill_list[-1]
        else:
            next_skill = self._tmp_skill_list.pop()

        # during random mode always use a medium task
        self._last_action = [next_skill, "task_2", 1.0]

        # log everything to a file
        if logger:
            logging.log(self.LOG_LEVEL, "[action]" + json.dumps(self._last_action))

        return self._last_action


def main():
    keys = ["sk1", "sk2", "sk3"]
    cm = ChildRandomModel(keys)

    # for i in xrange(0, 10):
    #     next_action = cm.get_next_action()
    #     print str(next_action[1]) + " for skill " + next_action[0]
    #     cm.update_belief("+O")
    #     sleep(1)

    # import numpy as np
    # import matplotlib.pyplot as plt
    #
    # x = np.arange(0, 11, 1.0)
    # y = cm.liste
    # plt.ylim((0.0, 1.0))
    # plt.plot(x, y)
    # plt.show()

    # from scipy.stats import norm
    # fig, ax = plt.subplots(1, 1)
    # x = np.linspace(norm.ppf(0.01, loc=.14, scale=.10), norm.ppf(0.99, loc=.14, scale=.10), 100)
    # ax.plot(x, norm.pdf(x, loc=.14, scale=.10), 'r-', lw=5, alpha=0.6, label='norm pdf')
    # x = np.linspace(norm.ppf(0.01, loc=.495, scale=.10), norm.ppf(0.99, loc=.495, scale=.10), 100)
    # ax.plot(x, norm.pdf(x, loc=.495, scale=.10), 'g-', lw=5, alpha=0.6, label='norm pdf')
    # x = np.linspace(norm.ppf(0.01, loc=.85, scale=.10), norm.ppf(0.99, loc=.85, scale=.10), 100)
    # ax.plot(x, norm.pdf(x, loc=.85, scale=.10), 'b-', lw=5, alpha=0.6, label='norm pdf')
    # plt.show()

    while True:
        next_action = cm.get_next_action()
        print str(next_action[1]) + " for skill " + next_action[0]
        obs = raw_input("Please enter observation (+O/-O/q for quit): ")
        print "you entered", obs
        if obs == 'q':
            break
        cm.update_belief(obs)

if __name__ == "__main__":
    main()
