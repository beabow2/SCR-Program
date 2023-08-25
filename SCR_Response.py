import pandas as pd
from scipy.signal import find_peaks
from parameter import Parameters
class SCR_resp:
    def __int__(self):
        self.max_index=0
        self.min_index=0
        self.df = None
        self.SCR_df = None
        self.SCR_res_figure = None
        self.SCR_response = 0
        self.parameter = Parameters()
    def SCR_resp(self,rise_begin, rise_end, max_rise_time, situation, target,display_window,df):
        place_SCR = df.loc[df[2] == situation].iloc[target-1][0]
        # Estimate CS Response
        #SCR_start = df[(df[0] >= place_SCR + rise_begin) & (df[0] <= place_SCR + rise_end)]
        #SCR_window = df[(df[0]>= place_SCR + rise_begin) & (df[0]<= place_SCR+display_window-rise_begin)]
        SCR_start = df[(df[0] >= place_SCR + rise_begin) & (df[0] <= place_SCR + rise_end)]
        SCR_df = df[(df[0]>= place_SCR) & (df[0]<= place_SCR+display_window)]
        trough_index = find_peaks(-SCR_start[1])[0]
        if len(trough_index) == 0 :
            if rise_begin == 0:
                min_index = SCR_start[1].idxmin()
                if (min_index+int(max_rise_time/0.1)) <= SCR_df.iloc[-1].name:
                    SCR_peaks = SCR_df.loc[min_index:min_index + int(max_rise_time/0.1)]
                else:
                    SCR_peaks = SCR_df.loc[min_index:]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_min = SCR_peaks[1].iloc[0]
                if len(peak_index) == 0 :
                    SCR_response = 0
                    min_index = 0
                    max_index = 0
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > SCR_response:
                        SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
        else:
            for i in range(len(trough_index)):
                SCR_peaks = SCR_df[trough_index[i]+int(rise_begin/0.1):trough_index[i] + int(rise_begin/0.1) + int(max_rise_time/0.1)+1]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_troughrow = SCR_peaks.iloc[0]
                SCR_min = SCR_troughrow[1]
                min_index_temp = SCR_troughrow.name
                if len(peak_index) == 0:
                    SCR_response = 0
                    min_index = 0
                    max_index = 0

                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > SCR_response:
                        SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
                        min_index = min_index_temp
        SCR_res_figure = SCR_df.loc[min_index:max_index]
        trough_check = find_peaks(-SCR_res_figure[1])[0]
        if len(trough_check) != 0:
            SCR_response = 0
            min_index = 0
            max_index = 0
            SCR_res_figure = SCR_df.loc[min_index:max_index]
        return(SCR_response)
