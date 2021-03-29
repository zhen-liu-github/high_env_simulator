from torch.utils.data import DataLoader, Dataset

import torch
import pandas as pd
import numpy as np
import os
from glob import glob
import sys
import torch
class WindowSelectionDataset(Dataset):
    def __init__(self, batch_size=16):
        super(WindowSelectionDataset, self).__init__()
        path = sys.path[0]
        path = os.path.join(path, 'models', 'dataset','data', '*.csv')
        file_list = glob(path)
        self.batch_size = batch_size
        self.data = {}
        for name in file_list:
            data = pd.read_csv(name)
            data = data.to_numpy()
            data = data.reshape(-1, eval(name.split('\\')[-1].split('.')[0]), data.shape[-1])
            self.data[eval(name.split('\\')[-1].split('.')[0])] = data
        self.length = 0
        for key in self.data.keys():
            self.length+=len(self.data[key])
    def __len__(self):
        return self.length
    def __getitem__(self, index):
        key_list = list(self.data.keys())
        np.random.shuffle(key_list)
        key_index = key_list[0]
        np.random.shuffle(self.data[key_index])
        result = self.data[key_index][:self.batch_size]
        label = np.array([res[0][15] for res in result])
        result = result[:,:,:12]
        result = result.reshape(-1, 1, *result.shape[-2:])
        return torch.from_numpy(result).float(), torch.from_numpy(label).float()
    def process(self, sample):
        return sample
