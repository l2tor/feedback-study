# -*- coding: utf-8 -*-
from copy import deepcopy
from sys import maxint
from time import sleep
from scipy.stats import norm, entropy
import json
import logging
import utils
import random
from Queue import Queue


class ChildModel:
    # meaning of each of the 6 probabilities above
    BIN_MEANING = [0., 0.2, 0.4, 0.6, 0.8, 1.]
    # count of bins for each skill-distribution
    BIN_COUNT = len(BIN_MEANING)
    # log-level
    LOG_LEVEL = 21

    def __init__(self, keys, overall_rounds, chunk_size):
        """
            Constructor to init the child model

            :param keys: list of all skills to be trained
            :param overall_rounds: The count of round to be thought.
        """
        self._last_action = None
        # self._action_norm = {'L': {'loc': .14, 'scale': .10},
        #                      'M': {'loc': .495, 'scale': .10},
        #                      'H': {'loc': .85, 'scale': .10}}

        self._action_norm = {'1': {'loc': .15, 'scale': .05},
                             '2': {'loc': .40, 'scale': .05},
                             '3': {'loc': .625, 'scale': .05},
                             '4': {'loc': .85, 'scale': .05}}

        self._actions = {"task_4": "4", "task_3": "3", "task_2": "2", "task_1": "1"}#, "probe_skill": "L", "explanation": "E"}

        self._u_bin = [0.05, 0.075, 0.125, 0.175, 0.225, 0.35]

        # the both following variables are used to make sure, every skill will be shown at least once.
        self._skills_not_used = deepcopy(keys)
        self._round_nr = 0
        self._overall_round_nr = overall_rounds
        self._chunk_size = chunk_size

        # CPT for P(O|S,A)
        # self._observation = {'+O': {'L': {0: 0.50, 1: 0.55, 2: 0.65, 3: 0.75, 4: 0.85, 5: 0.95},
        #                             "M": {0: 0.33, 1: 0.40, 2: 0.55, 3: 0.65, 4: 0.75, 5: 0.85},
        #                             "H": {0: 0.25, 1: 0.30, 2: 0.40, 3: 0.50, 4: 0.60, 5: 0.70},
        #                             "E": {0: 0.75, 1: 0.80, 2: 0.85, 3: 0.90, 4: 0.95, 5: 0.99}
        #                             },
        #                      '-O': {'L': {0: 0.50, 1: 0.45, 2: 0.35, 3: 0.25, 4: 0.15, 5: 0.05},
        #                             "M": {0: 0.67, 1: 0.60, 2: 0.45, 3: 0.35, 4: 0.25, 5: 0.15},
        #                             "H": {0: 0.75, 1: 0.70, 2: 0.60, 3: 0.50, 4: 0.40, 5: 0.30},
        #                             "E": {0: 0.25, 1: 0.20, 2: 0.15, 3: 0.10, 4: 0.05, 5: 0.01}
        #                             }
        #                      }
        self._observation = {'+O': {'1': {0: 0.50, 1: 0.55, 2: 0.65, 3: 0.75, 4: 0.85, 5: 0.95},
                                    "2": {0: 0.33, 1: 0.40, 2: 0.55, 3: 0.65, 4: 0.75, 5: 0.85},
                                    "3": {0: 0.25, 1: 0.30, 2: 0.40, 3: 0.50, 4: 0.60, 5: 0.70},
                                    "4": {0: 0.15, 1: 0.20, 2: 0.30, 3: 0.40, 4: 0.50, 5: 0.60}
                                    },
                             '-O': {'1': {0: 0.50, 1: 0.45, 2: 0.35, 3: 0.25, 4: 0.15, 5: 0.05},
                                    "2": {0: 0.67, 1: 0.60, 2: 0.45, 3: 0.35, 4: 0.25, 5: 0.15},
                                    "3": {0: 0.75, 1: 0.70, 2: 0.60, 3: 0.50, 4: 0.40, 5: 0.30},
                                    "4": {0: 0.85, 1: 0.80, 2: 0.70, 3: 0.60, 4: 0.50, 5: 0.40}
                                    }
                             }

        # CPT for P(A|S)
        # self._a_s = {'L': {0: 0.40, 1: 0.35, 2: 0.30, 3: 0.30, 4: 0.30, 5: 0.30},
        #              'M': {0: 0.30, 1: 0.35, 2: 0.40, 3: 0.40, 4: 0.35, 5: 0.30},
        #              'H': {0: 0.30, 1: 0.30, 2: 0.30, 3: 0.30, 4: 0.35, 5: 0.40},
        #              'E': {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00}
        #              }
        self._a_s = {'1': {0: 0.40, 1: 0.30, 2: 0.20, 3: 0.15, 4: 0.10, 5: 0.05},
                     '2': {0: 0.30, 1: 0.35, 2: 0.40, 3: 0.25, 4: 0.25, 5: 0.25},
                     '3': {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.40, 4: 0.35, 5: 0.30},
                     '4': {0: 0.05, 1: 0.10, 2: 0.15, 3: 0.20, 4: 0.30, 5: 0.40}
                     }

        # CPT for P(t) or P(S_t+1|S_t)
        # self._t_s = {'+O': {"L": {0: {0: 0.60, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.25, 1: 0.70, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.15, 1: 0.20, 2: 0.80, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.10, 2: 0.15, 3: 0.85, 4: 0.00, 5: 0.00},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.05, 3: 0.10, 4: 0.90, 5: 0.00},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.05, 4: 0.10, 5: 1.00}
        #                           },
        #                     "M": {0: {0: 0.55, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.35, 1: 0.60, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.10, 1: 0.30, 2: 0.70, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.10, 2: 0.20, 3: 0.70, 4: 0.00, 5: 0.00},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.10, 3: 0.25, 4: 0.75, 5: 0.00},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.05, 4: 0.25, 5: 1.00}
        #                           },
        #                     "H": {0: {0: 0.40, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.40, 1: 0.40, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.20, 1: 0.40, 2: 0.40, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.20, 2: 0.40, 3: 0.50, 4: 0.00, 5: 0.00},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.20, 3: 0.40, 4: 0.60, 5: 0.00},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.10, 4: 0.40, 5: 1.00}
        #                           },
        #                     "E": {0: {0: 0.95, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.05, 1: 0.95, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.00, 1: 0.05, 2: 0.95, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.00, 2: 0.05, 3: 0.95, 4: 0.00, 5: 0.00},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.05, 4: 0.95, 5: 0.00},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.05, 5: 1.00}
        #                           }
        #                     },
        #              '-O': {"L": {0: {0: 1.00, 1: 0.10, 2: 0.05, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.00, 1: 0.90, 2: 0.10, 3: 0.15, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.00, 1: 0.00, 2: 0.85, 3: 0.25, 4: 0.20, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.60, 4: 0.30, 5: 0.25},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.50, 5: 0.35},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.40}
        #                           },
        #                     "M": {0: {0: 1.00, 1: 0.25, 2: 0.05, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.00, 1: 0.75, 2: 0.25, 3: 0.10, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.00, 1: 0.00, 2: 0.70, 3: 0.25, 4: 0.10, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.65, 4: 0.30, 5: 0.10},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.60, 5: 0.35},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.55}
        #                           },
        #                     "H": {0: {0: 1.00, 1: 0.20, 2: 0.20, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.00, 1: 0.80, 2: 0.40, 3: 0.20, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.00, 1: 0.00, 2: 0.40, 3: 0.40, 4: 0.20, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.40, 4: 0.40, 5: 0.20},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.40, 5: 0.40},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.40}
        #                           },
        #                     "E": {0: {0: 1.00, 1: 0.05, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           1: {0: 0.00, 1: 0.95, 2: 0.05, 3: 0.00, 4: 0.00, 5: 0.00},
        #                           2: {0: 0.00, 1: 0.00, 2: 0.95, 3: 0.05, 4: 0.00, 5: 0.00},
        #                           3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.95, 4: 0.05, 5: 0.00},
        #                           4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.95, 5: 0.05},
        #                           5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.95}
        #                           }
        #                     }
        #              }

        # only to display on the screen .. first try was only to display half of the list,
        # so it's a separate variable

        self._t_s = {'+O': {"1": {0: {0: 0.60, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.25, 1: 0.70, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  2: {0: 0.15, 1: 0.20, 2: 0.80, 3: 0.00, 4: 0.00, 5: 0.00},
                                  3: {0: 0.00, 1: 0.10, 2: 0.15, 3: 0.85, 4: 0.00, 5: 0.00},
                                  4: {0: 0.00, 1: 0.00, 2: 0.05, 3: 0.10, 4: 0.90, 5: 0.00},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.05, 4: 0.10, 5: 1.00}
                                  },
                            "2": {0: {0: 0.55, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.35, 1: 0.60, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  2: {0: 0.10, 1: 0.30, 2: 0.70, 3: 0.00, 4: 0.00, 5: 0.00},
                                  3: {0: 0.00, 1: 0.10, 2: 0.20, 3: 0.70, 4: 0.00, 5: 0.00},
                                  4: {0: 0.00, 1: 0.00, 2: 0.10, 3: 0.25, 4: 0.75, 5: 0.00},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.05, 4: 0.25, 5: 1.00}
                                  },
                            "3": {0: {0: 0.40, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.40, 1: 0.40, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  2: {0: 0.20, 1: 0.40, 2: 0.40, 3: 0.00, 4: 0.00, 5: 0.00},
                                  3: {0: 0.00, 1: 0.20, 2: 0.40, 3: 0.50, 4: 0.00, 5: 0.00},
                                  4: {0: 0.00, 1: 0.00, 2: 0.20, 3: 0.40, 4: 0.60, 5: 0.00},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.10, 4: 0.40, 5: 1.00}
                                  },
                            "4": {0: {0: 0.30, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.45, 1: 0.30, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00},
                                  2: {0: 0.20, 1: 0.45, 2: 0.30, 3: 0.00, 4: 0.00, 5: 0.00},
                                  3: {0: 0.05, 1: 0.20, 2: 0.45, 3: 0.30, 4: 0.00, 5: 0.00},
                                  4: {0: 0.00, 1: 0.05, 2: 0.20, 3: 0.45, 4: 0.40, 5: 0.00},
                                  5: {0: 0.00, 1: 0.00, 2: 0.05, 3: 0.25, 4: 0.60, 5: 1.00}
                                  }
                            },
                     '-O': {"1": {0: {0: 1.00, 1: 0.10, 2: 0.05, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.00, 1: 0.90, 2: 0.10, 3: 0.15, 4: 0.00, 5: 0.00},
                                  2: {0: 0.00, 1: 0.00, 2: 0.85, 3: 0.25, 4: 0.20, 5: 0.00},
                                  3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.60, 4: 0.30, 5: 0.25},
                                  4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.50, 5: 0.35},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.40}
                                  },
                            "2": {0: {0: 1.00, 1: 0.25, 2: 0.05, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.00, 1: 0.75, 2: 0.25, 3: 0.10, 4: 0.00, 5: 0.00},
                                  2: {0: 0.00, 1: 0.00, 2: 0.70, 3: 0.25, 4: 0.10, 5: 0.00},
                                  3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.65, 4: 0.30, 5: 0.10},
                                  4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.60, 5: 0.35},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.55}
                                  },
                            "3": {0: {0: 1.00, 1: 0.20, 2: 0.20, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.00, 1: 0.80, 2: 0.40, 3: 0.20, 4: 0.00, 5: 0.00},
                                  2: {0: 0.00, 1: 0.00, 2: 0.40, 3: 0.40, 4: 0.20, 5: 0.00},
                                  3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.40, 4: 0.40, 5: 0.20},
                                  4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.40, 5: 0.40},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.40}
                                  },
                            "4": {0: {0: 1.00, 1: 0.40, 2: 0.15, 3: 0.00, 4: 0.00, 5: 0.00},
                                  1: {0: 0.00, 1: 0.60, 2: 0.35, 3: 0.15, 4: 0.00, 5: 0.00},
                                  2: {0: 0.00, 1: 0.00, 2: 0.50, 3: 0.35, 4: 0.15, 5: 0.00},
                                  3: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.50, 4: 0.35, 5: 0.15},
                                  4: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.50, 5: 0.35},
                                  5: {0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.50}
                                  }
                            }
                     }

        self._show_skill_text = keys

        # dictionary which stores a bayesian network for each skill to learn
        _bs = {}
        # alpha value to control the frequency of occurrence
        self._skill_freq_reduction = {}
        # TODO Clean up
        # self._skill_occurence = {}
        # self._last_skills = []
        # self.max_skill_memory = 2

        self.error_statistics = {}
        for key in keys:
            _bs.update({key: [1./6, 1./6, 1./6, 1./6, 1./6, 1./6]})
            self._skill_freq_reduction.update({key: 1.0})
            # self._skill_occurence.update({key: 0.0})
            self.error_statistics.update({key: [0.0, 0.0]})

        # list to store the different time-slides
        self._t = [_bs, ]

        self._skill_chunks = self._create_chunks(keys)
        print "all chunks: ", self._skill_chunks
        self._current_chunk = self._skill_chunks.pop(0)
        print "current chunk: ", self._current_chunk
        self.finished = (False, False)
        self.recap = False
        self.chunk_changed = False

    def _create_chunks(self, keys):
        current_items = [(k, utils.sum_to_percentage(self._t[-1][k], self.BIN_MEANING)) for k in keys]
        item_count = len(current_items)
        if self._chunk_size > item_count:
            self._chunk_size = item_count

        tmp = sorted(current_items, key=lambda x: x[1])
        return [tmp[i:i + self._chunk_size] for i in xrange(0, item_count, self._chunk_size)]

    def _prepare_recap(self):
        result = []
        for key, value in self.error_statistics.items():
            if value[0] > 0 and value[1]/value[0] > 0.0 and key not in result:
                result.append((key, utils.sum_to_percentage(self._t[-1][key], self.BIN_MEANING)))

        while len(result) < 3:
            rand_key, _ = random.choice(list(self.error_statistics.items()))
            if rand_key not in result:
                result.append((rand_key, utils.sum_to_percentage(self._t[-1][rand_key], self.BIN_MEANING)))

        self._skill_chunks.append(sorted(result, reverse=True, key=lambda x: self.error_statistics[x[0]][1])[:3])

    def update_round_number(self, number):
        """
            This function updates the internal counter which round is currently played. This number is used
            to make sure every skill will be taught at least once.

            :param number: The new round number.
        """
        print "=== Updating round number.. " + str(number)
        self._round_nr = number
        logging.log(self.LOG_LEVEL, "[round_nr]" + str(self._round_nr))

    def get_belief(self, skill):
        """
            Return the current belief-state for the given skill.

            :param skill: The skill the blief-state is requested for.

            :return: The belief-state in 6 bins.
        """
        return self._t[-1][skill]

    def get_action_difficulty(self, action):
        """
            Returns the difficult for a specific action.

            :param action: The action for which the difficult should be returned.
            :return: the difficult in one letter
        """
        return self._actions[action]

    def set_test_mode(self, value):
        """
            Only a dummy function for the adaptive model. During test-mode everything will be done normally instead of
            the belief-update. This step is coordinated by the interaction manager, so this part isn't need here.
        """
        pass

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

    def show_skilltext(self, skill):
        """
            Function which proves if for the given skill a skill-text should be shown on the tablet.

            /* from first try .. only display a few skills on the tablet to prove if there is a difference */

            :param skill: The skill to prove...

            :return: True   if should be shown
                     False  else
        """
        return skill in self._show_skill_text

    def update_skill_freq_reduction(self, skill, answer):
        """
            Updates (decreases) the alpha-value for a specific skill and raises the values for all others.

            :param skill: The last skill which had been taught.
            :param answer: The given answer of the user.
        """
        upd_coff = 0.3
        if answer == "-O":
            upd_coff = 0.45
        for s in self._skill_freq_reduction.keys():
            if s == skill and self._skill_freq_reduction[s] > 0.0:
                self._skill_freq_reduction[s] -= upd_coff # 0.3 # 0.1
            elif self._skill_freq_reduction[s] < 1.0:
                self._skill_freq_reduction[s] += 0.15 # 0.1
        # self._skill_occurence[skill] += 1.0
        # self._last_skills.append(skill)
        # if len(self._last_skills) > self.max_skill_memory:
        #     self._last_skills = self._last_skills[1:]

    # def get_skill_occurence(self, skill):
    #     # if self._round_nr == 0:
    #     #     return 1.0
    #     # return 1.0 - (self._skill_occurence[skill]/float(self._round_nr))
    #     if skill not in self._last_skills:
    #         return self._skill_freq_reduction[skill]
    #     else:
    #         return 0

    def reset_skill_freq_reduction(self):
        """
            Resets the alpha values for the occurrence frequency of all skills.
        """
        for s in self._skill_freq_reduction.keys():
            self._skill_freq_reduction[s] = 1.0

    def _sim_action(self, skill, action):
        """
            Simulates the effect of an action on a skill

            :param skill: The skill the action should be used on.
            :param action: The action which should be done.
            :return: Returns both probability-distributions - one for answering right and one for a wrong answer
        """
        s_i = [0.0]*self.BIN_COUNT
        a = self._actions[action]
        p_s_o_a = {}
        for o in ["+O", "-O"]:
            p_s_o_a.update({o: self._get_updated_belief(skill, action, o, sim=True)})

        for i in xrange(0, self.BIN_COUNT):
            x = 0.0
            for o in ["+O", "-O"]:
                tmp_si = 0.0
                for s in xrange(0, self.BIN_COUNT):
                    tmp_si += self._observation[o][a][s] * self._t[-1][skill][s] * self._a_s[a][s]
                x += tmp_si
                s_i[i] += tmp_si * p_s_o_a[o][i]
            s_i[i] /= x

        tmp_result = [0.0] * len(s_i)
        for i in xrange(0, len(s_i)):
            for j in xrange(0, len(s_i)):
                for obs in ["+O", "-O"]:
                    tmp_result[i] += s_i[j] * self._t_s[obs][a][i][j]/2
        return tmp_result

    def update_belief(self, obs):
        """
            This function creates a new time-slice and stores the updated bayes-net,with respect to the observation.

            :param obs: The observation (answer from the child).
        """
        if len(self._t) < 3:
            self._t.append(deepcopy(self._t[-1]))
        else:
            for i in xrange(0, len(self._t)-1):
                self._t[i] = self._t[i+1]
            self._t[-1] = deepcopy(self._t[-2])

        if self._last_action[1] != "explanation" or (self._last_action[1] == "explanation" and obs == "-O"):
            self.error_statistics[self._last_action[0]][0] += 1.0
            if obs == "-O":
                self.error_statistics[self._last_action[0]][1] += 1.0

        new_b = self._get_updated_belief(self._last_action[0], self._last_action[1], obs)
        self._t[-1][self._last_action[0]] = [0.0]*len(new_b)
        a = self._actions[self._last_action[1]]
        for i in xrange(0, len(new_b)):
            for j in xrange(0, len(new_b)):
                self._t[-1][self._last_action[0]][i] += new_b[j] * self._t_s[obs][a][i][j]

        # print self._t[-1]
        logging.log(self.LOG_LEVEL, "[nb]" + json.dumps(self._t[-1]))
        self.update_skill_freq_reduction(self._last_action[0], obs)

        # only for logging
        test = {}
        for x in self._t[-1].keys():
            test.update({x: utils.sum_to_percentage(self._t[-1][x], self.BIN_MEANING)})
        print test

        logging.log(self.LOG_LEVEL, "[nbp]" + json.dumps(test))

        go_on = self.evaluate_error_statistics()
        # if not go_on:
        #     self.finished = (True, True)
        #     return
        avg_sk_belief = sum([utils.sum_to_percentage(self._t[-1][skill], self.BIN_MEANING) for skill, _ in self._current_chunk]) / float(len(self._current_chunk))
        self.chunk_changed = False
        if self.recap and obs != "-O":
            del self._current_chunk[[i for i in xrange(len(self._current_chunk)) if self._current_chunk[i][0] == self._last_action[0]][0]]
            if len(self._current_chunk) == 0:
                self.finished = (True, False)
                return
        elif avg_sk_belief > 0.75:
            if len(self._skill_chunks) == 0:
                self.recap = True
                self._prepare_recap()
            self._current_chunk = self._skill_chunks.pop(0)
            self.chunk_changed = True

    def evaluate_error_statistics(self):
        result = True
        rounds = 0.0
        errors = 0.0

        for _, value in self.error_statistics.items():
            rounds += value[0]
            errors += value[1]

        if rounds >= 4:
            ratio = errors/rounds
            if ratio >= .75:
                result = False

        return result

    def _get_updated_belief(self, skill, action, observation, sim=False):
        result = [0.0]*self.BIN_COUNT
        a = self._actions[action]
        p_o = 0.0

        for c_bin in xrange(0, self.BIN_COUNT):
            result[c_bin] = self._observation[observation][a][c_bin] * self._t[-1][skill][c_bin]
            if sim:
                result[c_bin] *= self._a_s[a][c_bin]
            p_o += result[c_bin]

        return [x/p_o for x in result]

    def get_next_action(self, logger=True, sim=False):
        """
            This function determine the next skill to taught and with which action it should be done.

            :param logger: True     if the system should log the decision of the function
                           False    else
            :param sim: True    if the system simply should try to find out which action would be next
                        False   else
            :return: The next skill to be taught and the action to do it as a list.
        """
        result = ("", -maxint)
        super_skill = [1.99840144433e-15, 1.99840144433e-15, 1.99840144433e-15,
                       1.99840144433e-15, 1.99840144433e-15, 0.99999999999999]
        log_list = []
        random.shuffle(self._current_chunk)
        for skill, _ in self._current_chunk: # self._t[-1].keys():
            kld = entropy(self._t[-1][skill], qk=super_skill, base=6)
            kld_freq = kld * self._skill_freq_reduction[skill]#*kld
            log_list.append((skill, kld_freq))
            if kld_freq > result[1]:
                result = (skill, kld_freq)
        if logger:
            logging.log(self.LOG_LEVEL, "[kld_freq_list]" + json.dumps(log_list))
            logging.log(self.LOG_LEVEL, "[kld_freq]" + json.dumps(result))

        # print "[freq_reduction]", self._skill_freq_reduction
        # print "[kld_freq_list]", json.dumps(log_list)
        # print "[kld_freq]", json.dumps(result)

        #####################################################
        # make sure every skill will be taught at least once
        #####################################################
        if not sim:
            print self._skills_not_used, self._round_nr
            if len(self._skills_not_used) != 0 and len(self._skills_not_used) == (self._overall_round_nr-self._round_nr):
                print "system choice to taught each skill at least once"
                if logger:
                    logging.log(self.LOG_LEVEL, "[interrupt_1]System will try to teach every skill at least once.")
                result = (self._skills_not_used.pop(), 0.0)
            if result[0] in self._skills_not_used:
                self._skills_not_used.remove(result[0])
        #####################################################

        results = {result[0]: {}}
        for a in self._actions.keys():
            if a == "explanation":
                continue
            res = self._sim_action(result[0], a)
            results[result[0]].update({a: res})

        results_2 = deepcopy(results)
        for skill_i in results.keys():
            for action in results[skill_i].keys():
                a = self._actions[action]
                percentage = utils.sum_to_percentage(results[skill_i][action], self.BIN_MEANING)
                value = entropy(results[skill_i][action], qk=super_skill, base=6)
                value *= norm.pdf(percentage, loc=self._action_norm[a]['loc'], scale=self._action_norm[a]['scale'])
                results_2[skill_i][action] = [results[skill_i][action], value, percentage]

        print results_2

        if logger:
            logging.log(self.LOG_LEVEL, "[w_actions]" + json.dumps(results_2))
        self._last_action = self._arg_max(results_2)

        if sim:
            self._last_action[0] = 'RABBIT'

        if logger:
            logging.log(self.LOG_LEVEL, "[action]" + json.dumps(self._last_action))
         
        return self._last_action

    def _arg_max(self, result):
        """
            Function for arg_max of the probable action for a skill.

            :param result: List of all skills with all actions and their effects on each skill.
            :return: the best skill/action combination to be done.
        """
        best_skill_action = [-1, -1, -maxint]
        for skill in result.keys():
            for a in result[skill].keys():
                if result[skill][a][1] > best_skill_action[2]:
                    best_skill_action = [skill, a, result[skill][a][1]]
        return best_skill_action


def main():
    keys = ["sk1", "sk2", "sk3", "sk4", "sk5", "sk6", "sk7", "sk8", "sk9"]
    cm = ChildModel(keys, 30, 9)

    # TODO check if the correction is also counted? --> change that
    # cm.error_statistics = {"sk1":(5.,5.), "sk2":(0.,0.), "sk3":(0.,0.), "sk4":(5.,5.), "sk5":(0.,0.), "sk6":(0.,0.)}
    # #cm._prepare_recap()
    # print "skill chunks ", cm.evaluate_error_statistics()#cm._skill_chunks
    # for i in xrange(0, 10):
    #     next_action = cm.get_next_action()
    #     print str(next_action[1]) + " for skill " + next_action[0]
    #     cm.update_belief("-O")
    #     sleep(1)
    #
    import numpy as np
    import matplotlib.pyplot as plt

    # x = np.arange(0, 11, 1.0)
    # y = cm.liste
    # print x,y
    # plt.ylim((0.0, 1.0))
    # plt.xlabel("task count")
    # plt.ylabel("probability")
    # plt.plot(x, y)
    # plt.show()

    # from scipy.stats import norm
    # fig, ax = plt.subplots(1, 1)
    # x = np.linspace(0, 0.3, 100)
    # ax.plot(x, norm.pdf(x, loc=.15, scale=.05), 'r-', lw=2, alpha=0.6, label='norm pdf')
    # x = np.linspace(norm.ppf(0.01, loc=.40, scale=.05), norm.ppf(0.99, loc=.4, scale=.05), 100)
    # ax.plot(x, norm.pdf(x, loc=.4, scale=.05), 'g-', lw=2, alpha=0.6, label='norm pdf')
    # x = np.linspace(norm.ppf(0.01, loc=.625, scale=.05), norm.ppf(0.99, loc=.625, scale=.05), 100)
    # ax.plot(x, norm.pdf(x, loc=.625, scale=.05), 'b-', lw=2, alpha=0.6, label='norm pdf')
    # x = np.linspace(norm.ppf(0.01, loc=.85, scale=.05), norm.ppf(0.99, loc=.85, scale=.05), 100)
    # ax.plot(x, norm.pdf(x, loc=.85, scale=.05), 'y-', lw=2, alpha=0.6, label='norm pdf')
    # plt.show()

    while True:
        next_action = cm.get_next_action()
        print str(next_action[1]) + " for skill " + next_action[0]
        obs = raw_input("Please enter observation (+O/-O/q for quit): ")
        print "you entered", obs
        if obs == 'q':
            break
        cm.update_belief(obs)
        cm._round_nr += 1

if __name__ == "__main__":
    main()
