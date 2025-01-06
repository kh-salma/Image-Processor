import numpy as np
from InterfaceGraphique.Assets.config import gray_image_type, h_image_type, indexed_image_type

class ColorDescribor:
    def get_histogram(self, image):
        if image.ndim == 2:
            hist = np.histogram(image, bins=256, range=(0, 255))[0]
        else:
            histograms = [np.histogram(image[channel], bins=256, range=(0, 255))[0] for channel in range(image.shape[0])]
            hist = np.concatenate(histograms)
        return hist

    def get_normalized_histogram(self, image):
        if image.ndim == 2:
            hist = np.histogram(image, bins=256, range=(0, 255), density=True)[0]
        else:
            histograms = [np.histogram(image[channel], bins=256, range=(0, 255), density=True)[0] for channel in range(image.shape[0])]
            hist = np.concatenate(histograms)
        return hist

    def get_saturated_hue_histogram(self, image):
        hue_channel = image[0, :, :]  
        saturation_channel = image[1, :, :]  
        hist_hue_weighted = np.histogram(hue_channel, bins=256, range=(0, 255), weights=saturation_channel)[0]
        return hist_hue_weighted

    def get_histogram_blob(self, image, image_type, window=(3,3), nb_interval=4, canaux=None):
        if image_type in gray_image_type:
            nb_elements = 256
        elif image_type in h_image_type:
            nb_elements = 360
            image = image[0, :, :]
        elif image_type in indexed_image_type:
            nb_elements = canaux[0]*canaux[1]*canaux[2]

        blob_hist = np.zeros((nb_elements, nb_interval), dtype=np.int32)
        interval_size = 100 / nb_interval

        for i in range(0, image.shape[1] - window[1] + 1):
            for j in range(0, image.shape[0] - window[0] + 1):
                current_window = image[i:i + window[0], j:j + window[1]]
                hist, _ = np.histogram(current_window.flatten(), bins=nb_elements, range=(0, nb_elements-1))
                total_pixels = current_window.size
                freq_percentages = (hist / total_pixels) * 100
                for value, freq_percent in enumerate(freq_percentages):
                    interval_idx = int(freq_percent / interval_size)
                    if interval_idx != 0:  
                        blob_hist[value, interval_idx-1] += 1
        return blob_hist
      