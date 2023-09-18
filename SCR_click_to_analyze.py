import os
import pandas as pd
from SCR_Response import SCR_RESP
class DataAnalysis:

    def __init__(self, folder_path):
        self.folder_path = folder_path

    def data_loading(self, file_path, delimiter="\t", header=None):
        """
        Load data from a text file into a pandas DataFrame.

        Args:
            file_path (str): The path to the text file.
            delimiter (str, optional): The delimiter used in the text file. Defaults to "\t".
            header (int, optional): The row number to use as the column names. Defaults to None.

        Returns:
            pandas.DataFrame: The loaded data as a DataFrame.
        """
        if os.path.exists(file_path) and file_path.endswith(".txt"):
            df = pd.read_csv(file_path, delimiter=delimiter, header=header)
            return df

    def max_US_resp(self, SCR, df, rise_begin, rise_end, max_rise_time, display_window):
        # set rise_end to capture US response
        if rise_end < 9.2:
            rise_end = 9.2
        US_len = len(df.loc[df[2] == 3])
        max_us_list = []
        for target in range(1, US_len + 1):
            SCR.scr_resp(rise_begin, rise_end, max_rise_time, cs_type=3,
                         target=target, display_window=display_window)
            max_us_list.append(SCR.get_SCR_response())
        max_us = round(max(max_us_list), 4)
        return max_us

    def data_analysis(self,phase,rise_begin, rise_end, max_rise_time, display_window, ext_num, output="both", standardze=True):
        """
        Perform data analysis on the given data
        :param standardze: whether to standardize the data
        :param phase: which state to analyze, with "acq" or "ext"
        :param ext_num: the number of CS in extinction phase
        :param output:  the output type with default "both" and options "both", "individual", and "group"
        """
        if phase == "acq":
            total_df = {'CS-': [0] * 100, 'CS+': [0] * 100, 'US': [0] * 100,'difference': [0] * 100}
        elif phase == "ext":
            total_df = {'CS-': [0] * 100, 'CS+': [0] * 100,'difference': [0] * 100}

        total_df = pd.DataFrame(total_df)

        # Read each file in the folder
        for filename in os.listdir(self.folder_path):
            # Data loading
            file_path = os.path.join(self.folder_path, filename)
            loaded_data = self.data_loading(file_path)
            # Define Object SCR
            SCR = SCR_RESP(loaded_data)
            cs_type_data = {}

            # Run through all types
            for cs_type in range(1, 4):
                cs_type_response = []

                # Acq phase
                if phase == "acq":
                    # Target number
                    target_num = len(loaded_data[loaded_data[2] == cs_type]) - ext_num
                    if cs_type == 3:
                        rise_end = 9.2
                        target_num = len(loaded_data[loaded_data[2] == cs_type])
                    # Calculate response
                    for target in range(1, target_num + 1):
                        SCR.scr_resp(rise_begin, rise_end, max_rise_time, cs_type, target, display_window, order="normal")
                        SCR_response = SCR.get_SCR_response()
                        cs_type_response.append(SCR_response)

                # Ext phase
                elif phase == "ext" and cs_type != 3:
                    target_num = ext_num
                    for target in range(-target_num + 1, 1):
                        SCR.scr_resp(rise_begin, rise_end, max_rise_time, cs_type, target, display_window, order="normal")
                        SCR_response = SCR.get_SCR_response()
                        cs_type_response.append(SCR_response)

                if phase != "ext" or cs_type != 3:
                    # Save response
                    cs_type_data[f"cs_type{cs_type}"] = cs_type_response
                    cs_type_data[f"cs_type{cs_type}"] = cs_type_response

            # Transform data to dataframe
            results_df = pd.DataFrame.from_dict(cs_type_data, orient='index').T

            # Standardize
            if standardze:
                max_us = self.max_US_resp(SCR, loaded_data, rise_begin, rise_end, max_rise_time, display_window)
                results_df = round(results_df / max_us, 4)

            # Rename
            results_df.rename(columns={"cs_type1": "CS-", "cs_type2": "CS+", "cs_type3": "US"}, inplace=True)

            # Sum up individual analysis
            total_df += results_df

            #add difference
            results_df["difference"] = round(results_df["CS+"] - results_df["CS-"],4)
            total_df["difference"] = round(total_df["CS+"] - total_df["CS-"],4)


            # Save individual analysis
            if output == "both" or output == "individual":
                csv_file_name = f"{phase}_{filename[:-4]}_analysis.csv"
                results_df.to_csv(csv_file_name, index=True)

        # Save group analysis
        if output == "both" or output == "group":
            # Calculate group mean
            total_df = total_df / len(os.listdir(self.folder_path))
            # Save group analysis
            csv_file_name = f"{phase}_group_analysis.csv"
            total_df.to_csv(csv_file_name, index=True)

    def output_both_phase(self, rise_begin, rise_end, max_rise_time, display_window,ext_num, output="both", standardze=True):
        self.data_analysis("acq",rise_begin, rise_end, max_rise_time, display_window, ext_num, output, standardze)
        self.data_analysis("ext",rise_begin, rise_end, max_rise_time, display_window ,ext_num, output, standardze)



## run class DataAnalysis

if __name__ == "__main__":
    data_analysis = DataAnalysis(r"D:\data\11")
    data_analysis.output_both_phase(0.5,4.5,5,10,15,"both",False)
    """
    data_analysis.data_analysis("acq",15,"both")
    data_analysis.data_analysis("ext",15,"both")
    """
