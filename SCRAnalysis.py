import pandas as pd
import numpy as np
from scipy.signal import find_peaks


class SCRAnalysis:
    def __init__(self, parameters):
        self.parameters = parameters
        self.file_path = ""
        self.df = None
        self.CSP_response = 0
        self.CSM_response = 0
        # Initialize more instance variables as needed

    def load_data(self):
        self.df = pd.read_csv(self.file_path, delimiter="\t", header=None)
        # More data processing code here...

    def scr_resp(self, rise_begin, rise_end, max_rise_time, cs_type, target, display_window):
        """
            :param rise_begin:
            :param rise_end:
            :param max_rise_time:
            :param cs_type: 1=CS-, 2=CS+, 3=CS+E
            :param target: which CS 由後往前數，1=最後一個
            :param display_window: window (sec)
            :return:
            """
        # initialize min and max index
        max_index = 0
        min_index = 0
        place_scr = self.df.loc[self.df[2] == cs_type].iloc[-target][0]  # event onset time

        # find the space of scr response
        SCR_start = self.df[(self.df[0] >= place_scr + rise_begin) & (self.df[0] <= place_scr + rise_end)]  # resp開始算數的範圍
        SCR_df = self.df[(self.df[0] >= place_scr) & (self.df[0] <= place_scr + display_window)]
        trough_index = find_peaks(-SCR_start[1])[0]  # 找 through 和 peak 正找波峰 負找波谷
        SCR_response = 0
        # if no trough found in the space
        if len(trough_index) == 0:
            SCR_response = 0
            min_index = 0
            max_index = 0
            # if we ignore rise_begin
            if rise_begin == 0:
                min_index = SCR_start[1].idxmin()
                if (min_index + int(max_rise_time / 0.1)) <= SCR_df.iloc[-1].name:
                    SCR_peaks = SCR_df.loc[min_index:min_index + int(max_rise_time / 0.1)]
                else:
                    SCR_peaks = SCR_df.loc[min_index:]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_min = SCR_peaks[1].iloc[0]
                # if no peak
                if len(peak_index) == 0:
                    SCR_response = 0
                    min_index = 0
                    max_index = 0
                # if peak
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > SCR_response:
                        SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
        # if we find trough in the space
        else:
            for i in range(len(trough_index)):
                SCR_peaks = SCR_df[
                            trough_index[i] + int(rise_begin / 0.1):trough_index[i] + int(rise_begin / 0.1) + int(
                                max_rise_time / 0.1) + 1]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_troughrow = SCR_peaks.iloc[0]
                SCR_min = SCR_troughrow[1]
                min_index_temp = SCR_troughrow.name
                # if no peak
                if len(peak_index) == 0:
                    SCR_response = 0
                    min_index = 0
                    max_index = 0
                # if peak
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > SCR_response:
                        SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
                        min_index = min_index_temp
        # draw the response
        SCR_res_figure = SCR_df.loc[min_index:max_index]
        trough_check = find_peaks(-SCR_res_figure[1])[0]
        # if there is trough between the response
        if len(trough_check) != 0:
            SCR_response = 0
            min_index = 0
            max_index = 0
            SCR_res_figure = SCR_df.loc[min_index:max_index]
        return (SCR_response, SCR_df, SCR_res_figure)

    def toggle_analysis(self):
        if max_analysis_var.get() == 1:
            # after standardized
            CS_resp_update(CSP_response_stand, CSM_response_stand, CSP_df_stand, CSM_df_stand, CSP_res_figure_stand,
                           CSM_res_figure_stand)
            update_plot()
        else:
            # before standardized
            CS_resp_update(CSP_response_ns, CSM_response_ns, CSP_df_ns, CSM_df_ns, CSP_res_figure_ns, CSM_res_figure_ns)
            update_plot()

    def data_analysis(self):
        ##CS+
        CSP_func = self.scr_resp(rise_begin, rise_end, max_rise_time, 2, target, display_window)
        CSP_response_ns = round(CSP_func[0], 4)
        CSP_df_ns = CSP_func[1]
        CSP_res_figure_ns = CSP_func[2]
        ##CS-
        CSM_fun = self.scr_resp(rise_begin, rise_end, max_rise_time, 1, target, display_window)
        CSM_response_ns = round(CSM_fun[0], 4)
        CSM_df_ns = CSM_fun[1]
        CSM_res_figure_ns = CSM_fun[2]
        # Standardization
        ###US
        max_us = round(max_US_resp(rise_begin, rise_end, max_rise_time, target, display_window), 4)
        MUS_label.config(text=f"Max US:{max_us:}")
        ###Standarize CSP and CSM
        CSP_response_stand = round(CSP_response_ns / max_us, 4)
        CSM_response_stand = round(CSM_response_ns / max_us, 4)
        CSP_df_stand = CSP_df_ns / max_us
        CSM_df_stand = CSM_df_ns / max_us
        CSP_res_figure_stand = CSP_res_figure_ns / max_us
        CSM_res_figure_stand = CSM_res_figure_ns / max_us
        if max_analysis_var.get() == 1:
            CS_resp_update(CSP_response_stand, CSM_response_stand, CSP_df_stand, CSM_df_stand, CSP_res_figure_stand,
                           CSM_res_figure_stand)
        else:
            CS_resp_update(CSP_response_ns, CSM_response_ns, CSP_df_ns, CSM_df_ns, CSP_res_figure_ns, CSM_res_figure_ns)

    # More methods related to SCR Analysis
    # Find Maximum US
    def max_US_resp(self, rise_begin, rise_end, max_rise_time, target, display_window):
        # set rise_end to capture US response
        if rise_end <= 9.2:
            rise_end = 9.2
        US_len = len(self.df.loc[self.df[2] == 3])
        max_us = 0
        # find maximum US response
        max_us_list = [self.scr_resp(rise_begin, rise_end, max_rise_time, 3, target, display_window)[0] for target in
                       range(1, US_len + 1)]
        max_us_temp = max(max_us_list)
        if max_us_temp > max_us and len(max_us_list) != 0:
            max_us = max_us_temp
        return (max_us)


    # Update CS Response
    def CS_resp_update(CSP_res_temp, CSM_res_temp, CSP_df_temp, CSM_df_temp, CSP_res_figure_temp, CSM_res_figure_temp):
        global CSP_response
        global CSM_response
        global CSP_df
        global CSM_df
        global CSP_res_figure
        global CSM_res_figure
        # update CS response
        CSP_response = CSP_res_temp
        CSM_response = CSM_res_temp
        CSP_df = CSP_df_temp
        CSM_df = CSM_df_temp
        CSP_res_figure = CSP_res_figure_temp
        CSM_res_figure = CSM_res_figure_temp
        # update CS response shown on the GUI
        CSP_label.config(text=f"CS+ Response:{CSP_response:}")
        CSM_label.config(text=f"CS- Response:{CSM_response:}")
        diff = round(CSP_response - CSM_response, 4)
        Diff_label.config(text=f"Difference:{diff}")
        reward = round(300 - 100 * diff)
        reward_label.config(text=f"Reward:{reward:}")
        # graph SCR response
        if len(CSP_res_figure) != 0:
            CSP_initial = CSP_res_figure.iloc[0].name
            CSP_res_figure.index = range(CSP_df.index.get_loc(CSP_initial) + 1,
                                         CSP_df.index.get_loc(CSP_initial) + len(CSP_res_figure) + 1)
        if len(CSM_res_figure) != 0:
            CSM_initial = CSM_res_figure.iloc[0].name
            CSM_res_figure.index = range(CSM_df.index.get_loc(CSM_initial) + 1,
                                         CSM_df.index.get_loc(CSM_initial) + len(CSM_res_figure) + 1)
        CSP_df.index = range(1, len(CSP_df) + 1)
        CSM_df.index = range(1, len(CSM_df) + 1)
        ##Find y-axis
        global min_y_ax1_ax2
        global max_y_ax1_ax2
        min_y_ax1_ax2 = min(min(CSP_df[1]), min(CSM_df[1])) - 0.5
        max_y_ax1_ax2 = max(max(CSP_df[1]), max(CSM_df[1])) + 0.5
        global min_y_ax3
        global max_y_ax3
        min_y_ax3 = min(CSP_df[1] - CSM_df[1]) - 0.5
        max_y_ax3 = max(CSP_df[1] - CSM_df[1]) + 0.5