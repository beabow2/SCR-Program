import pandas as pd
import os


class Ledalab_Cleaning_Base:

    # initialize
    def __init__(self):
        # CS-
        self.CSM = None
        # CS+
        self.CSP = None

    # data loading
    def data_loading(self, file_path, delimiter="\t"):
        if os.path.exists(file_path) and file_path.endswith(".txt"):
            df = pd.read_csv(file_path, delimiter=delimiter)
            return df

    # data output

    def data_output(self, filename, save_path, data, phase):
        csv_file_name = f"{phase}_{filename[:-17]}_ledalab.csv"
        data.to_csv(save_path + csv_file_name, index=True)

    # event separate
    def event_separate(self, data, day):
        # find CS- response
        self.CSM = data[data["Event.NID"] == 1]["CDA.PhasicMax"]
        # find CS+ response
        self.CSP = data[data["Event.NID"] == 2]["CDA.PhasicMax"]
        if day == "Day1":
            # find US response
            self.US = data[data["Event.NID"] == 3]["CDA.PhasicMax"]
            self.US.name = "US"
            self.US.index = range(1,len(self.US)+1)


class Ledalab_Cleaning_Day1(Ledalab_Cleaning_Base):
    def __init__(self):
        super().__init__()
        # Initialize Day1 specific attributes
        # US
        self.US = None
        self.max_US_list = []
        # acq
        self.acq = None
        self.CSM_acq = None
        self.CSP_acq = None
        # ext
        self.ext = None
        self.CSM_ext = None
        self.CSP_ext = None

    def phase_separate(self, ext_num):
        event_list = ["CSM", "CSP"]
        for event in event_list:
            df = getattr(self, event)
            df.name = event
            # find acq_num
            acq_num = len(df) - ext_num
            # find corresponding df
            df_acq = df.iloc[:acq_num]
            # reindex
            df_acq.index = range(0, len(df_acq))
            # redo
            df_ext = df.iloc[-ext_num:]
            df_ext.index = range(0, len(df_ext))
            setattr(self, f'{event}_acq', df_acq)
            setattr(self, f'{event}_ext', df_ext)

    def combine_event(self):
        # acq
        self.acq = pd.concat([self.CSM_acq, self.CSP_acq, self.US], axis=1)
        # ext
        self.ext = pd.concat([self.CSM_ext, self.CSP_ext], axis=1)

    def ledalab_cleaning(self, filename, ext_num):
        loaded_data = self.data_loading(filename)
        # separate event
        self.event_separate(loaded_data, "Day1")
        # separate phase
        self.phase_separate(ext_num)
        # combine event
        self.combine_event()

    def US_resp(self):
        return self.US.max()

    def standardize_resp(self):
        self.acq = round(self.acq / self.US_resp(), 4)
        self.ext = round(self.ext / self.US_resp(), 4)

    def get_max_US(self):

        return self.max_US_list


    def day1_data_output(self, folder_path, save_path, ext_num, standardize=True):
        # create acq and ext group
        total_acq_df = {'CSM': [0] * 100, 'CSP': [0] * 100, 'US': [0] * 100, 'difference': [0] * 100}
        total_acq_df = pd.DataFrame.from_dict(total_acq_df)
        # reset index
        total_acq_df.index = range(0, len(total_acq_df) )
        total_ext_df = {'CSM': [0] * 100, 'CSP': [0] * 100, 'difference': [0] * 100}
        total_ext_df = pd.DataFrame.from_dict(total_ext_df)
        # reset index
        total_ext_df.index = range(0, len(total_ext_df))
        # clean all data
        file_counter = 0
        for filename in os.listdir(folder_path):
            print(filename)
            # Data loading
            file_path = os.path.join(folder_path, filename)
            if not file_path.endswith('.txt'):
                continue
            self.ledalab_cleaning(file_path, ext_num)
            if standardize:
                self.standardize_resp()
                self.max_US_list.append(self.US_resp())
            # cal difference
            self.acq['difference'] = round(self.acq['CSP'] - self.acq['CSM'], 4)
            self.ext['difference'] = round(self.ext['CSP'] - self.ext['CSM'], 4)
            # output individual analysis to CSV
            self.data_output(filename, save_path, self.acq, 'acq')
            self.data_output(filename, save_path, self.ext, 'ext')
            # add group analysis
            total_acq_df += self.acq
            total_ext_df += self.ext
            file_counter += 1

        # Save group analysis
        csv_file_name = f"acq_group_ledalab.csv"
        total_acq_df = round(total_acq_df / file_counter, 4)
        total_acq_df.to_csv(save_path + csv_file_name, index=True)
        csv_file_name = f"ext_group_ledalab.csv"
        total_ext_df = round(total_ext_df / file_counter, 4)
        total_ext_df.to_csv(save_path + csv_file_name, index=True)


class Ledalab_Cleaning_Day2(Ledalab_Cleaning_Base):
    def __init__(self):
        super().__init__()
        # Initialize Day2 specific attributes
        #reext
        self.CSM_reext = None
        self.CSP_reext = None
        self.reext = None
        #reinst
        self.CSM_reinst = None
        self.CSP_reinst = None
        self.reinst = None

    def phase_separate(self, ext_num):
        event_list = ["CSM", "CSP"]
        for event in event_list:
            df = getattr(self, event)
            df.name = event
            # reext
            # find corresponding df
            df_reext = df.iloc[:ext_num]
            # reindex
            df_reext.index = range(1, len(df_reext) + 1)
            # reinst
            df_reinst = df.iloc[-13:]
            df_reinst.index = range(1, len(df_reinst) + 1)
            # assign value
            setattr(self, f'{event}_reext', df_reext)
            setattr(self, f'{event}_reinst', df_reinst)

    def combine_event(self):
        # reext
        self.reext = pd.concat([self.CSM_reext, self.CSP_reext], axis=1)
        # reinst
        self.reinst = pd.concat([self.CSM_reinst, self.CSP_reinst], axis=1)

    def ledalab_cleaning(self, filename, ext_num):
            loaded_data = self.data_loading(filename)
            # separate event
            self.event_separate(loaded_data, "Day2")
            # separate phase
            self.phase_separate(ext_num)
            # combine event
            self.combine_event()

    def standardize_resp(self,max_US=1):
        self.reext = round(self.reext / max_US, 4)
        self.reinst = round(self.reinst / max_US, 4)
    def day2_data_output(self,folder_path,save_path,ext_num,max_US_list=None,standardize=True):
        #create reext and reinst group
        total_reext_df = {'CSM': [0] * 100, 'CSP': [0] * 100,'difference': [0] * 100}
        total_reext_df = pd.DataFrame.from_dict(total_reext_df)
        # reset index
        total_reext_df.index = range(1, len(total_reext_df) + 1)
        total_reinst_df = {'CSM': [0] * 100, 'CSP': [0] * 100,'difference': [0] * 100}
        total_reinst_df = pd.DataFrame.from_dict(total_reinst_df)
        #reset index
        total_reinst_df.index = range(1, len(total_reinst_df) + 1)
        #clean all data
        file_counter = 0
        for filename in os.listdir(folder_path):
            print(filename)
            # Data loading
            file_path = os.path.join(folder_path, filename)
            if not file_path.endswith('.txt'):
                continue
            self.ledalab_cleaning(file_path,ext_num)
            #standardize
            if standardize:
                self.standardize_resp(max_US_list[file_counter])
            #cal difference
            self.reext['difference'] = round(self.reext['CSP'] - self.reext['CSM'],4)
            self.reinst['difference'] = round(self.reinst['CSP'] - self.reinst['CSM'],4)
            # output individual analysis to CSV
            self.data_output(filename,save_path,self.reext,'reext')
            self.data_output(filename,save_path,self.reinst,'reinst')
            #add group analysis
            total_reext_df += self.reext
            total_reinst_df += self.reinst
            file_counter += 1

        # Save group analysis
        csv_file_name = f"reext_group_ledalab.csv"
        total_reext_df = round(total_reext_df/file_counter,4)
        total_reext_df.to_csv(save_path+csv_file_name, index=True)
        csv_file_name = f"reinst_group_ledalab.csv"
        total_reinst_df = round(total_reinst_df/file_counter,4)
        total_reinst_df.to_csv(save_path+csv_file_name, index=True)


# Usage


if __name__ == "__main__":
    day1 = Ledalab_Cleaning_Day1()
    day1.day1_data_output(r"D:\data\Day1\leda", r"D:\data\Day1\leda\result\\", 15,standardize=True)
    max_US = day1.get_max_US()
    day2 = Ledalab_Cleaning_Day2()
    day2.day2_data_output(r"D:\data\Day2", r"D:\data\Day2\result\\", 15, max_US,standardize=True)
