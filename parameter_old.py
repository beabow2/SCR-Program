class Parameters:
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
    DEFAULT_TARGET = 1
    DEFAULT_RISE_END = 4.5
    DEFAULT_RISE_BEGIN = 0.5
    DEFAULT_MAX_RISE_TIME = 5.0
    DEFAULT_DISPLAY_WINDOW = 10.0

    def __init__(self, rise_begin=DEFAULT_RISE_BEGIN, rise_end=DEFAULT_RISE_END, max_rise_time=DEFAULT_MAX_RISE_TIME, display_window=DEFAULT_DISPLAY_WINDOW, target=DEFAULT_TARGET):
        self.rise_begin = rise_begin
        self.rise_end = rise_end
        self.max_rise_time = max_rise_time
        self.display_window = display_window
        self.target = target

    def get_rise_begin(self):
        """
        Get the value of rise_begin parameter.
        """
        return self.rise_begin

    def set_rise_begin(self, value):
        """
        Set the value of rise_begin parameter.
        """
        self.rise_begin = value

    def get_rise_end(self):
        """
        Get the value of rise_end parameter.
        """
        return self.rise_end

    def set_rise_end(self, value):
        """
        Set the value of rise_end parameter.
        """
        self.rise_end = value

    def get_max_rise_time(self):
        """
        Get the value of max_rise_time parameter.
        """
        return self.max_rise_time

    def set_max_rise_time(self, value):
        """
        Set the value of max_rise_time parameter.
        """
        self.max_rise_time = value

    def get_display_window(self):
        """
        Get the value of display_window parameter.
        """
        return self.display_window

    def set_display_window(self, value):
        """
        Set the value of display_window parameter.
        """
        self.display_window = value

    def get_target(self):
        """
        Get the value of target parameter.
        """
        return self.target

    def set_target(self, value):
        """
        Set the value of target parameter.
        """
        self.target = value

    def __repr__(self):
        return f"Parameters(rise_begin={self.rise_begin}, rise_end={self.rise_end}, max_rise_time={self.max_rise_time}, display_window={self.display_window}, target={self.target})"
