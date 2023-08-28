DEFAULT_RISE_BEGIN = 0.5
DEFAULT_RISE_END = 4.5
DEFAULT_MAX_RISE_TIME = 5.0
DEFAULT_DISPLAY_WINDOW = 10.0
DEFAULT_TARGET = 1


class Parameters:
    def __init__(self):
        """
        Initialize parameters with default values.\n
        Rise Start-Begin: the closest point in time following an event at which a potential response can start in
        order for it to be considered valid (default 0.5 sec.)\n
        Rise Start-End: the furthest point in time following an event at which a potential response can start in order
        for it to be considered valid (default 4.5 sec.)\n
        Max Rise Time: the maximum duration of the rising portion of a potential response for it to be considered
        valid (default 5 sec.)\n
        Display_window: the length of time following an event in which the program will look for responses in the
        electrodermal data (default 10 sec.)\n
        Target: the reversed number of event (default 1)
        """
        self.target = None
        self.display_window = None
        self.max_rise_time = None
        self.rise_end = None
        self.rise_begin = None
        self.reset_to_defaults()

    def reset_to_defaults(self):
        """
        Reset all parameters to their default values.
        """
        self.rise_begin = DEFAULT_RISE_BEGIN
        self.rise_end = DEFAULT_RISE_END
        self.max_rise_time = DEFAULT_MAX_RISE_TIME
        self.display_window = DEFAULT_DISPLAY_WINDOW
        self.target = DEFAULT_TARGET

    def update_parameters(self, rise_begin=None, rise_end=None, max_rise_time=None, display_window=None, target=None):
        """
        Update parameters. If a parameter is None, it will not be updated.
        """
        if rise_begin is not None:
            self.rise_begin = rise_begin
        if rise_end is not None:
            self.rise_end = rise_end
        if max_rise_time is not None:
            self.max_rise_time = max_rise_time
        if display_window is not None:
            self.display_window = display_window
        if target is not None:
            self.target = target
