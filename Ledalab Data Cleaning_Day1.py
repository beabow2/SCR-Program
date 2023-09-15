# import pakages
import pandas as pd
import os


class Ledalab_Cleaning():

    # initialize
    def __init__(self):
        # CS-
        self.CSM = None
        self.CSM_acq = None
        self.CSM_ext = None
        # CS+
        self.CSP = None
        self.CSP_acq = None
        self.CSP_ext = None
        # US
        self.US = None
        # acq
        self.acq = None
        # ext
        self.ext = None

    # def data_loading function
    def data_loading(self, file_path, delimiter="\t"):
        # only load txt file
        if os.path.exists(file_path) and file_path.endswith(".txt"):
            df = pd.read_csv(file_path, delimiter=delimiter)
            return df

    def event_separate(self, data):
        # find CS- response
        self.CSM = data[data["Event.NID"] == 1]["CDA.PhasicMax"]
        # find CS+ response
        self.CSP = data[data["Event.NID"] == 2]["CDA.PhasicMax"]
        # find US response
        self.US = data[data["Event.NID"] == 3]["CDA.PhasicMax"]
        self.US.name = "US"
        self.US.index = range(1, len(self.US) + 1)

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
            df_acq.index = range(1, len(df_acq) + 1)
            # redo
            df_ext = df.iloc[-ext_num:]
            df_ext.index = range(1, len(df_ext) + 1)
            setattr(self, f'{event}_acq', df_acq)
            setattr(self, f'{event}_ext', df_ext)

    def combine_event(self):
        # acq
        self.acq = pd.concat([self.CSM_acq, self.CSP_acq, self.US], axis=1)
        # ext
        self.ext = pd.concat([self.CSM_ext, self.CSP_ext], axis=1)

    def acq_output(self, filename,save_path):
        csv_file_name = f"acq_{filename[:-17]}_ledalab.csv"
        self.acq.to_csv(save_path+csv_file_name, index=True)

    def ext_output(self, filename,save_path):
        csv_file_name = f"ext_{filename[:-17]}_ledalab.csv"
        self.ext.to_csv(save_path+csv_file_name, index=True)

    # batch data cleaning
    def ledalab_cleaning(self, filename, ext_num):
            loaded_data = self.data_loading(filename)
            # separate event
            self.event_separate(loaded_data)
            # separate phase
            self.phase_separate(ext_num)
            # combine event
            self.combine_event()


    def day1_data_output(self,folder_path,save_path,ext_num):
        #create acq and ext group
        total_acq_df = {'CSM': [0] * 100, 'CSP': [0] * 100, 'US': [0] * 100,'difference': [0] * 100}
        total_acq_df = pd.DataFrame.from_dict(total_acq_df)
        # reset index
        total_acq_df.index = range(1, len(total_acq_df) + 1)
        total_ext_df = {'CSM': [0] * 100, 'CSP': [0] * 100,'difference': [0] * 100}
        total_ext_df = pd.DataFrame.from_dict(total_ext_df)
        #reset index
        total_ext_df.index = range(1, len(total_ext_df) + 1)
        #clean all data
        file_counter = 0
        for filename in os.listdir(folder_path):
            # Data loading
            file_path = os.path.join(folder_path, filename)
            if not file_path.endswith('.txt'):
                continue
            self.ledalab_cleaning(file_path,ext_num)
            #cal difference
            self.acq['difference'] = round(self.acq['CSP'] - self.acq['CSM'],4)
            self.ext['difference'] = round(self.ext['CSP'] - self.ext['CSM'],4)
            # output individual analysis to CSV
            self.acq_output(filename,save_path)
            self.ext_output(filename,save_path)
            #add group analysis
            total_acq_df += self.acq
            total_ext_df += self.ext
            file_counter += 1

        # Save group analysis
        csv_file_name = f"acq_group_{filename[:-17]}_ledalab.csv"
        total_acq_df = round(total_acq_df/file_counter,4)
        total_acq_df.to_csv(save_path+csv_file_name, index=True)
        csv_file_name = f"ext_group_{filename[:-17]}_ledalab.csv"
        total_ext_df = round(total_ext_df/file_counter,4)
        total_ext_df.to_csv(save_path+csv_file_name, index=True)

app = Ledalab_Cleaning()
app.day1_data_output(r"D:\data\Day1\leda",r"D:\data\Day1\leda\result\\",15)
