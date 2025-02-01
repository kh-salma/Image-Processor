import numpy as np

class Normalizer:
    @staticmethod
    def probability_normalization(vector):
        return vector / np.sum(vector)

    @staticmethod
    def norm_normalization(vector):
        return vector / np.sqrt(np.sum(vector**2))

    @staticmethod
    def minmax_normalization(vector):
        min_val = np.min(vector)
        max_val = np.max(vector)
        return (vector - min_val) / (max_val - min_val)

    @staticmethod
    def standardization(vector):
        mean = np.mean(vector)
        std = np.std(vector)
        return (vector - mean) / std

    @staticmethod
    def rank_normalization(vector):
        return np.argsort(np.argsort(vector)) + 1
