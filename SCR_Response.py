from scipy.signal import find_peaks
class SCR_RESP:
    def __init__(self,df):
        self.max_index=0
        self.min_index=0
        self.SCR_df = None
        self.SCR_res_figure = None
        self.SCR_response = 0
        self.df = df

    def scr_resp(self,rise_begin, rise_end, max_rise_time, cs_type, target, display_window,order = "normal", time_step=0.1):
        """
        :param rise_begin: the minimum response onset time
        :param rise_end:   the maximum response onset time
        :param max_rise_time:  the maximum time of the rising portion
        :param cs_type: CS+, CS-, CS+E
        :param target: which CS to be analyzed (reversed count)
        :param display_window: window (sec)
        :param time_step: time step (sec)
        :param order: how  to calculate the response target
        """
        min_index = 0
        max_index = 0
        if order == "normal":
            place_SCR = self.df.loc[self.df[2] == cs_type].iloc[target-1][0]
        elif order == "reverse":
            place_SCR = self.df.loc[self.df[2] == cs_type].iloc[-target][0]  # event onset time

        # Estimate CS Response
        SCR_start = self.df[(self.df[0] >= place_SCR + rise_begin) & (self.df[0] <= place_SCR + rise_end)]
        SCR_df = self.df[(self.df[0] >= place_SCR) & (self.df[0] <= place_SCR + display_window)]
        trough_index = find_peaks(-SCR_start[1])[0]
        self.SCR_response = 0
        # if no trough found in the space
        if len(trough_index) == 0:
            min_index = 0
            max_index = 0

            # if we ignore rise_begin
            if rise_begin == 0:
                min_index = SCR_start[1].idxmin()
                if (min_index + int(max_rise_time / time_step)) <= SCR_df.iloc[-1].name:
                    SCR_peaks = SCR_df.loc[min_index:min_index + int(max_rise_time / time_step)]
                else:
                    SCR_peaks = SCR_df.loc[min_index:]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_min = SCR_peaks[1].iloc[0]

                # if no peak
                if len(peak_index) == 0:
                    min_index = 0
                    max_index = 0
                # if peak
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > self.SCR_response:
                        self.SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
        # if we find trough in the space
        else:
            for i in range(len(trough_index)):
                SCR_peaks = SCR_df[trough_index[i] + int(rise_begin / time_step):trough_index[i] + int(
                    rise_begin / time_step) + int(
                    max_rise_time / time_step) + 1]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_troughrow = SCR_peaks.iloc[0]
                SCR_min = SCR_troughrow[1]
                min_index_temp = SCR_troughrow.name

                # if no peak
                if len(peak_index) == 0:
                    min_index = 0
                    max_index = 0
                # if peak
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > self.SCR_response:
                        self.SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
                        min_index = min_index_temp

        # draw the response
        self.SCR_res_figure = SCR_df.loc[min_index:max_index]
        self.SCR_df = SCR_df
        trough_check = find_peaks(-self.SCR_res_figure[1])[0]
        # if there is trough between the response
        if len(trough_check) != 0:
            self.SCR_response = 0
            min_index = 0
            max_index = 0
            self.SCR_res_figure = SCR_df.loc[min_index:max_index]
    def get_SCR_response(self):
        return round(self.SCR_response,4)
    def get_SCR_df(self):
        return self.SCR_df
    def get_SCR_res_figure(self):
        return self.SCR_res_figure


