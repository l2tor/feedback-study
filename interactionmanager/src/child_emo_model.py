# -*- coding: utf-8 -*-


class ChildEmoModel:
    """
        This class holds information about the mental state of the child.
    """
    def __init__(self):
        # the different states of valence
        self._valence = ["Pos", "Neu", "Neg"]
        # the different level of engagement
        self._engagement = ["L", "M", "H"]
        # the different "discrete" level of motivation
        self._motivation = [("L", 0.33), ("M", 0.66), ("H", 1.00)]

        # default values for valence and engagement
        self._p_val = 1.0
        self._p_eng = 1.0

    def get_motivation(self):
        """
            This function calculates the motivation for the current child w.r.t. the level of engagement and valence.

            :return: A discrete value for the motivation: "L" for low
                                                          "M" for medium
                                                          "H" for high
        """
        p = self._p_val * self._p_eng
        # find discrete value for the continual value of the motivation
        for key, val in self._motivation:
            if p <= val:
                return key

    def update_motivation(self, positive=True):
        """
            This function updates the motivation level either positive or negative.

            :param positive: If positive, the motivation will be raised.
        """
        # define update_rates
        update_rate_pos = 0.1
        update_rate_neg = 0.3

        # update levels of engagement and valence
        if positive:
            self._p_val += update_rate_pos
            if self._p_val > 1.:
                self._p_val = 1.
            self._p_eng += update_rate_pos
            if self._p_eng > 1.:
                self._p_eng = 1.
        else:
            self._p_val -= update_rate_neg
            if self._p_val < 0.:
                self._p_val = 0.
            self._p_eng -= update_rate_neg
            if self._p_eng < 0.:
                self._p_eng = 0.

        print self._p_val, self._p_eng, self._p_val*self._p_eng
        print "motivation updated"

    def reset_motivation(self):
        """
            This function resets the motivation, calculated through engagement and valence, to default values.
        """
        self._p_eng = 1.0
        self._p_val = 1.0
