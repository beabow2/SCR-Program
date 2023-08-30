import os
import pandas as pd
from SCR_Response import SCR_RESP
from parameter import Parameters
class DataAnalysis:

    def __init__(self,folder_path):
        self.folder_path = folder_path
        self.parameter = Parameters()

    def data_loading(self,file_path, delimiter="\t", header=None):

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

    def data_analysis(self,phase,ext_num,output = "both"):
        """
        Perform data analysis on the given data
        :param phase: which state to analyze, with "acq" or "ext"
        :param ext_num: the number of CS in extinction phase
        :param output:  the output type with default "both" and options "both", "individual", and "group"
        """
        #folder_path = r"C:\Users\sharo\OneDrive\桌面\RA Paper\Data Analysis"
        # Initialize parameter
        rise_begin = self.parameter.rise_begin  # default 0.5
        rise_end = self.parameter.rise_end  # default 4.5
        max_rise_time = self.parameter.max_rise_time  # default 5
        display_window = self.parameter.display_window  # default 10

        if phase == "acq":
            total_df = {'CS-': [0] * 100, 'CS+': [0] * 100, 'US': [0] * 100}
        elif phase == "ext":
            total_df = {'CS-': [0] * 100, 'CS+': [0] * 100}

        total_df = pd.DataFrame(total_df)

        #Read each file in the folder
        for filename in os.listdir(self.folder_path):
            #data loading
            file_path = os.path.join(self.folder_path, filename)
            loaded_data = self.data_loading(file_path)
            #define Object SCR
            SCR = SCR_RESP(loaded_data)
            cs_type_data = {}
            # run through all of type
            for cs_type in range(1, 4):
                cs_type_response = []
                ## acq phase
                if phase == "acq":
                    # target number
                    target_num = len(loaded_data[loaded_data[2] == cs_type]) - ext_num
                    if cs_type == 3:
                        rise_end = 9.2
                        target_num = len(loaded_data[loaded_data[2] == cs_type])
                    #calculate response
                    for target in range(1, target_num + 1):

                        SCR.scr_resp(rise_begin, rise_end, max_rise_time, cs_type, target, display_window, order="normal")
                        SCR_response = SCR.get_SCR_response()
                        cs_type_response.append(SCR_response)
                ## ext phase
                elif phase == "ext" and cs_type != 3:
                    target_num = ext_num
                    for target in range(-target_num + 1, 1):
                        SCR.scr_resp(rise_begin, rise_end, max_rise_time, cs_type, target, display_window, order="normal")
                        SCR_response =  SCR.get_SCR_response()
                        cs_type_response.append(SCR_response)

                if phase != "ext" or cs_type != 3:
                    cs_type_data[f"cs_type{cs_type}"] = cs_type_response
            # save individual analysis
            results_df = pd.DataFrame.from_dict(cs_type_data, orient='index').T
            results_df.rename(columns={"cs_type1": "CS-", "cs_type2": "CS+", "cs_type3": "US"}, inplace=True)
            if output == "both" or output == "individual":
                csv_file_name = f"{phase}_{filename[:-4]}_analysis.csv"
                results_df.to_csv(csv_file_name, index=True)

            # sum up individual analysis
            total_df += results_df
        if output == "both" or output == "group":
            # calculate group mean
            total_df = total_df / len(os.listdir(self.folder_path))
            # save group analysis
            csv_file_name = f"{phase}_group_analysis.csv"
            total_df.to_csv(csv_file_name, index=True)

    def output_both_phase(self,ext_num,output = "both"):

        self.data_analysis("acq", ext_num,output)
        self.data_analysis("ext", ext_num,output)



## run class DataAnalysis

data_analysis = DataAnalysis(r"C:\Users\sharo\OneDrive\桌面\RA Paper\Data Analysis")
data_analysis.output_both_phase(15,"both")
"""
data_analysis.data_analysis("acq",15,"both")
data_analysis.data_analysis("ext",15,"both")
"""
