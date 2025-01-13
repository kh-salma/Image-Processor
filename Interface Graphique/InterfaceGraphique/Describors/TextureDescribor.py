import numpy as np
from skimage.feature import graycomatrix, graycoprops
from InterfaceGraphique.Assets.config import h_image_type, indexed_image_type


class TextureDescribor:
    def stats_calculation(self, data):
        mean = np.mean(data)
        std = np.std(data)
        q_1 = np.percentile(data, 25)
        median = np.median(data)
        q_3 = np.percentile(data, 75)
        return np.array([mean, std, q_1, median, q_3])

    def get_stats_array(self, image):
        if image.ndim == 2:
            stats = self.stats_calculation(image)
        else:
            stats = np.concatenate([self.stats_calculation(image[channel]) for channel in range(image.shape[0])])
        return stats
    
    def local_binary_pattern_calculation(self, image):
        lbp_array = np.zeros((image.shape[0] - 3 + 1, image.shape[1] - 3 + 1), dtype=np.int32)
        for i in range(lbp_array.shape[0]):
            for j in range(lbp_array.shape[1]):
                current_window = image[i:i + 3, j:j + 3]
                center = current_window[1, 1]
                cal_window = current_window - center
                cal_window = (cal_window > 0).astype(np.int32)
                cal_window_vector = cal_window.flatten()
                cal_window_vector = np.delete(cal_window_vector, 4)
                print(cal_window_vector)
                value = np.sum(cal_window_vector * (2 ** np.arange(cal_window_vector.size)))
                print(value)
                lbp_array[i, j] = value
        return lbp_array
    
    def get_local_binary_pattern(self, image):
        if image.ndim == 2:
            lbp = self.local_binary_pattern_calculation(image).flatten()
        else:
            lbps = [self.local_binary_pattern_calculation(image[channel]).flatten() for channel in range(image.shape[0])]
            lbp = np.concatenate(lbps)
        return lbp
    
    def get_local_binary_pattern_histogram_blob(self, input_array, window=(3, 3), nb_interval=4):
        nb_elements = 256
        blob_hist = np.zeros((nb_elements, nb_interval), dtype=np.int32)
        interval_size = 100 / nb_interval

        for i in range(0, input_array.shape[1] - window[1] + 1):
            for j in range(0, input_array.shape[0] - window[0] + 1):
                current_window = input_array[i:i + window[0], j:j + window[1]]
                hist, _ = np.histogram(current_window.flatten(), bins=nb_elements, range=(0, nb_elements-1))
                total_pixels = current_window.size
                freq_percentages = (hist / total_pixels) * 100
                for value, freq_percent in enumerate(freq_percentages):
                    interval_idx = int(freq_percent / interval_size)
                    if interval_idx != 0:  
                        blob_hist[value, interval_idx-1] += 1
        return blob_hist.flatten()
    
    def get_haralick_histogram(self, image, image_type, distances=[1], angles=[0], symmetric=True, normed=True, canaux=None):
        if image_type in h_image_type:
            levels = 360
        elif image_type in indexed_image_type:
            levels = canaux[0]*canaux[1]*canaux[2]
        else:
            levels = 256
        
        if len(image.shape) == 3:
            haralick_features = []
            for channel in range(image.shape[2]):
                glcm = graycomatrix(image[:, :, channel], distances=distances, angles=angles, levels=levels, symmetric=symmetric, normed=normed)
                haralick_feature = np.hstack([graycoprops(glcm, prop).ravel() for prop in ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM']])
                haralick_features.append(haralick_feature.flatten())
            combined_harilick = np.sum(haralick_features, axis=0)
            return combined_harilick
        else:
            glcm = graycomatrix(image, distances=distances, angles=angles, levels=levels, symmetric=symmetric, normed=normed)
            haralick_features = np.hstack([graycoprops(glcm, prop).ravel() for prop in ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM']])
            return haralick_features.flatten()
       