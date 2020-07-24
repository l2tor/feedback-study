# -*- coding: utf-8 -*-
from math import log


def sum_to_percentage(distribution, bin_meaning):
    """
        Calculates the overall probability for the given distribution.

        :param distribution: The distribution
        :param bin_meaning: The discrete meaning for each bin in the distribution
                            e.g. [0.0,.2,.4 ...] for [0%, 20%, 40%]
        :return: overall probability
    """
    result = 0.0
    for i in xrange(0, len(distribution)):
        result += bin_meaning[i] * distribution[i]
    return result


def calc_entropy(b):
    """
        This function calculates the entropy of the probability-distribution b.

        :param b: The probability-distribution for which the entropy should be calculated.
        :return: The entropy of the given distribution.
    """
    result = 0.0
    for item in b:
        result += item * log(item, len(b))
    return -result
