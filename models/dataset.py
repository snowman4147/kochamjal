import numpy as np
import torch
from torch.utils.data import Dataset


def scale(data, scale_factor):
    return data * scale_factor


def add_noise(data, noise_level=0.01):
    noise = np.random.normal(0, noise_level, data.shape)
    return data + noise


def time_shift(data, shift):
    return np.roll(data, shift, axis=0)


def dropout(data, drop_prob):
    mask = np.random.binomial(1, 1 - drop_prob, data.shape)
    return data * mask


class CNCDataset(Dataset):
    def __init__(self, data, seq_length, target_columns, augment=False):
        self.data = data
        self.seq_length = seq_length
        self.target_columns = target_columns
        self.augment = augment

    def __len__(self):
        return len(self.data) - self.seq_length

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.seq_length]
        y = self.data[idx + self.seq_length, self.target_columns]
        if self.augment:
            x = time_shift(x, shift=np.random.randint(-5, 5))
            x = add_noise(x, noise_level=0.01)
            x = scale(x, scale_factor=np.random.uniform(0.9, 1.1))
            x = dropout(x, drop_prob=0.1)
        return torch.tensor(x, dtype=torch.float), torch.tensor(y, dtype=torch.float)
