import pandas as pd
import os
import numpy as np


class Data_Combine:

    def __init__(self, file_path):
        self.file_path = file_path
        self.acq = None
        self.ext = None
        self.reext = None
        self.reinst = None
        self.total_df = None

    ##load all data
    def load_sub_data(self, subject_number):
        subject_number = str(subject_number)
        for filename in os.listdir(self.file_path):
            if filename.endswith(".csv") and subject_number in filename:
                if 'acq' in filename:
                    self.acq = pd.read_csv(os.path.join(self.file_path, filename), index_col=0)
                elif 'reext' in filename:
                    self.reext = pd.read_csv(os.path.join(self.file_path, filename), index_col=0)
                elif 'ext' in filename:
                    self.ext = pd.read_csv(os.path.join(self.file_path, filename), index_col=0)
                else:
                    self.reinst = pd.read_csv(os.path.join(self.file_path, filename), index_col=0)

    ## combine all data in different phase
    def data_combine(self):
        df_list = [self.acq, self.ext, self.reext, self.reinst]
        combined_df = pd.concat(df_list).reset_index(drop=True)
        combined_df = combined_df.T
        return (combined_df)

    # reshape data
    def data_reshape(self, subject_number):
        # create empty dataframe
        df = pd.DataFrame()
        # load subject's data
        self.load_sub_data(subject_number)
        # create combined_df
        combined_df = self.data_combine()
        # reshape data
        for name, row in combined_df.iterrows():
            df = pd.concat([df, row])
        df = df.T
        columns = df.columns.tolist()
        counter = 0
        for i in range(len(columns)):
            if columns[i] == 0:
                counter += 1
            if counter == 1:
                columns[i] = 'CSM' + str(i)
            elif counter == 2:
                columns[i] = "CSPA" + str(i)
            elif counter == 3:
                columns[i] = "CSPB" + str(i)
            else:
                columns[i] = "US" + str(i)
        df.columns = columns
        print(df)
        return (df)

    def data_output(self,data,file_name):
        data.to_csv(os.path.join(self.file_path, file_name), index=True)

    def subject_combine(self, subject_number_lower, subject_number_upper):
        self.total_df = pd.DataFrame()

        for subject_number in range(subject_number_lower, subject_number_upper + 1):
            df = self.data_reshape(subject_number)
            self.total_df = pd.concat([self.total_df, df])

        subject_len = subject_number_upper - subject_number_lower + 1
        subject_group = ["Choice" if i % 2 == 0 else "Control" for i in range(subject_len)]
        print(subject_group)
        self.total_df.insert(0, 'Group', subject_group)
        self.total_df.index = range(1, len(self.total_df) + 1)

    def total_df_return(self):
        print(self.total_df)

        return (self.total_df)

    def resp_choose(self, response):
        columns = self.total_df.columns[self.total_df.columns.str.contains(response)]
        return (columns)

    def mean_cal(self, response):
        columns = self.resp_choose(response)
        self.total_df[f"{response}_mean"] = self.total_df[columns].mean(axis=1)

    def spone_recovery_resp(self, number, response):
        columns = self.resp_choose(response)
        resp = self.total_df[columns].T.iloc[number]
        return (resp)

    def spone_recovery_resp_cal(self, indicator, number_diff, phase):
        if phase == "acq":
            respM = self.spone_recovery_resp(indicator + number_diff, 'CSM')
        else:
            respM = self.spone_recovery_resp(indicator, 'CSM')
        respA = self.spone_recovery_resp(indicator, 'CSPA')
        respB = self.spone_recovery_resp(indicator, 'CSPB')
        spone_recovA = respA - respM
        spone_recovB = respB - respM
        return (spone_recovA, spone_recovB)

    def spone_recovery_resp_mean(self, number_diff, lower_csp_number, spone_num=1, phase="previous"):
        spone_recov_sumA = 0
        spone_recov_sumB = 0

        if phase == "previous" or phase == "acq":
            indicator_lower = lower_csp_number - spone_num + 1
            indicator_upper = lower_csp_number + 1
        elif phase == "current":
            indicator_lower = lower_csp_number + 1
            indicator_upper = lower_csp_number + spone_num + 1

        for indicator in range(indicator_lower, indicator_upper):
            spone_recov_single = self.spone_recovery_resp_cal(indicator, number_diff, phase)
            spone_recov_singleA = spone_recov_single[0]
            spone_recov_singleB = spone_recov_single[1]
            spone_recov_sumA += spone_recov_singleA
            spone_recov_sumB += spone_recov_singleB

        spone_recov_meanA = spone_recov_sumA / spone_num
        spone_recov_meanB = spone_recov_sumB / spone_num

        return (spone_recov_meanA, spone_recov_meanB)

    def spone_recovery_cal(self, number_diff, lower_csp_number, spone_num=1):

        spone_recov_current = self.spone_recovery_resp_mean(number_diff, lower_csp_number, spone_num, phase="current")
        spone_recov_previous = self.spone_recovery_resp_mean(number_diff, lower_csp_number, spone_num, phase="previous")
        spone_recov_A = spone_recov_current[0] - spone_recov_previous[0]
        spone_recov_B = spone_recov_current[1] - spone_recov_previous[1]
        return (spone_recov_A, spone_recov_B)

    def spone_recovery_acqext(self, number_diff, acq_csp_number, ext_csp_number, spone_num=1):

        spone_recov_current = self.spone_recovery_resp_mean(number_diff, ext_csp_number, spone_num, phase="current")
        spone_recov_acq = self.spone_recovery_resp_mean(number_diff, acq_csp_number, spone_num, phase="acq")

        spone_recov_A = spone_recov_current[0] - spone_recov_acq[0]
        spone_recov_B = spone_recov_current[1] - spone_recov_acq[1]
        return (spone_recov_A, spone_recov_B)

    def find_max_us(self):
        columns = self.resp_choose('US')
        self.total_df["Max_US"] = self.total_df[columns].max(axis=1)

    def data_analysis(self, number_diff, spone_num):

        # mean calculate
        response_list = ["CSM", "CSPA", "CSPB", "US"]
        for response in response_list:
            self.mean_cal(response)

        #find max US
        self.find_max_us()

        # calculate spontaneous recovery
        acq_ext_spone_recovery = self.spone_recovery_acqext(number_diff, acq_csp_number=2, ext_csp_number=6,
                                                            spone_num=spone_num)
        ext_reext_spone_recovery = self.spone_recovery_cal(number_diff, lower_csp_number=14, spone_num=spone_num)
        reext_reinst_spone_recovery = self.spone_recovery_cal(number_diff, lower_csp_number=22, spone_num=spone_num)
        # add
        spone_column = {
            f"A_{spone_num}_acq_ext_Spon_Recov": acq_ext_spone_recovery[0],
            f"B_{spone_num}_acq_ext_Spon_Recov": acq_ext_spone_recovery[1],
            f"A_{spone_num}_ext_reext_Spon_Recov": ext_reext_spone_recovery[0],
            f"B_{spone_num}_ext_reext_Spon_Recov": ext_reext_spone_recovery[1],
            f"A_{spone_num}_reext_reinst_Spon_Recov": reext_reinst_spone_recovery[0],
            f"B_{spone_num}_reext_reinst_Spon_Recov": reext_reinst_spone_recovery[1]
        }

        # 使用 pd.concat 一次性添加所有新列
        self.total_df = pd.concat([self.total_df, pd.DataFrame(spone_column, index=self.total_df.index)], axis=1)


    def standardize(self):
            #standardized data
            # Copy the original dataset to avoid changing it
            data_original = self.total_df.copy()

            # Identifying numeric columns to apply the division operation
            numeric_columns = data_original.select_dtypes(include=['float64', 'int64']).columns

            # Divide only the numeric columns by the corresponding Max_US value, keeping NaN as is
            for col in numeric_columns:
                # Skip the 'Max_US' column itself to avoid dividing it by itself
                if col != "Max_US":
                    data_original[col] = data_original.apply(
                        lambda row: row[col] / row["Max_US"] if (row["Max_US"] != 0 and not pd.isna(row[col])) else row[
                            col], axis=1)

            # Display the first few rows of the dataset after normalization
            self.total_df = round(data_original,4)

    def data_grouped(self):
        grouped_df = self.total_df.groupby('Group')
        for group_name,group_df in grouped_df:
            self.data_output(group_df, f"{group_name}_data.csv")


if __name__ == "__main__":
    subject_data_path = r"C:\Users\sharo\OneDrive\桌面\RA Paper\Realtime Reward Data\SCR\Result"
    subject_data = Data_Combine(subject_data_path)

    subject_data.subject_combine(6, 15)
    subject_data.data_analysis(3, 1)
    subject_data.data_analysis(3, 2)
    subject_data.standardize()
    subject_data.data_output(subject_data.total_df,"total_data.csv")
    subject_data.data_grouped()

