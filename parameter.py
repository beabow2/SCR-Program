DEFAULT_RISE_BEGIN = 0.5
DEFAULT_RISE_END = 4.5
DEFAULT_MAX_RISE_TIME = 5.0
DEFAULT_DISPLAY_WINDOW = 10.0
DEFAULT_TARGET = 1


class Parameters:
    def __init__(self):
        """
        Rise Start-Begin: the closest point in time following an event at which a potential response can start in
        order for it to be considered valid (default 0.5 sec.)\n
        Rise Start-End: the furthest point in time following an event at which a potential response can start in order
        for it to be considered valid (default 4.5 sec.)\n
        Max Rise Time: the maximum duration of the rising portion of a potential response for it to be considered
        valid (default 5 sec.)\n
        Display_window: the length of time following an event in which the program will look for responses in the
        electrodermal data (default 10 sec.)\n
        Target: the reversed number of event (default 1.)
        """
        self.rise_begin = DEFAULT_RISE_BEGIN
        self.rise_end = DEFAULT_RISE_END
        self.max_rise_time = DEFAULT_MAX_RISE_TIME
        self.display_window = DEFAULT_DISPLAY_WINDOW
        self.target = DEFAULT_TARGET
