import numpy as np

class ShapeDescribor:
    def get_blob_orientation(self, input_array, window=(3, 3), nb_interval=4, nb_directions=None):
        if not nb_directions:
            array = input_array
            nb_elements = 360
        else:
            array = (input_array // (360 / nb_directions)).astype(np.uint8)
            nb_elements = nb_directions

        blob_hist = np.zeros((nb_elements, nb_interval), dtype=np.int32)
        interval_size = 100 / nb_interval

        for i in range(0, array.shape[1] - window[1] + 1):
            for j in range(0, array.shape[0] - window[0] + 1):
                current_window = array[i:i + window[0], j:j + window[1]]
                hist, _ = np.histogram(current_window.flatten(), bins=nb_elements, range=(0, nb_elements-1))
                total_pixels = current_window.size
                freq_percentages = (hist / total_pixels) * 100
                for value, freq_percent in enumerate(freq_percentages):
                    interval_idx = int(freq_percent / interval_size)
                    if interval_idx != 0:  
                        blob_hist[value, interval_idx-1] += 1
        return blob_hist
    
    def get_norm_and_orientation(self, image, filter):
        if filter == "sobel":
            mat_x = np.array([[-1, 0, 1],[-2, 0, 2],[-1, 0, 1]])
            mat_y = np.array([[-1, -2, -1],[0, 0, 0],[1, 2, 1]])
        elif filter == "scharr":
            mat_x = np.array([[-3, 0, 3],[-10, 0, 10],[-3, 0, 3]])
            mat_y = np.array([[-3, -10, -3],[0, 0, 0],[3, 10, 3]])
        elif filter == "prewitt":
            mat_x = np.array([[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]])
            mat_y = np.array([[-1, -1, -1],[0, 0, 0],[1, 1, 1]])
        else:
            mat_x = np.array([[-1, 0, 1],[-1, 0, 1],[-1, 0, 1]])
            mat_y = np.array([[1, 1, 1],[0, 0, 0],[-1, -1, -1]])

        x_gradient = np.zeros((image.shape[0] - mat_x.shape[0] + 1, image.shape[1] - mat_x.shape[1] + 1), dtype=np.int32)
        y_gradient = np.zeros((image.shape[0] - mat_y.shape[0] + 1, image.shape[1] - mat_y.shape[1] + 1), dtype=np.int32)

        for mat, gradient in [(mat_x,x_gradient), (mat_y,y_gradient)]:
            for i in range(0, gradient.shape[0]):
                for j in range(0, gradient.shape[1]):
                    current_window = image[i:i + mat.shape[0], j:j + mat.shape[1]]
                    value = np.mean(current_window * mat) 
                    gradient[i, j] = value
        
        norm = np.round((x_gradient**2 + y_gradient**2)**(1/2)).astype(int)
        ort = np.degrees(np.arctan2(y_gradient, x_gradient))  # Convert radians to degrees
        ort = (ort.astype(int) + 360) % 360  # Normalize to range [0, 359]
        
        return (norm,ort)
    
    def get_histogram_orientation(self, image, filter):
        if image.ndim == 2:
            orientation = self.get_norm_and_orientation(image, filter)[1]
            hist = np.histogram(orientation, bins=360, range=(0, 359))[0]
        else:
            histograms = [np.histogram(self.get_norm_and_orientation(image[channel], filter)[1], bins=360, range=(0, 359))[0] for channel in range(image.shape[0])]
            hist = np.concatenate(histograms)
        return hist
    
    def get_norm_weighted_histogram_orientation(self, image, filter):
        if image.ndim == 2:
            norm, orientation = self.get_norm_and_orientation(image, filter)
            hist_orientation_weighted = np.histogram(orientation, bins=360, range=(0, 359), weights=norm)[0]
        else:
            histograms = [np.histogram(self.get_norm_and_orientation(image[channel], filter)[1], bins=360, range=(0, 359), weights=self.get_norm_and_orientation(image[channel], filter)[0])[0] for channel in range(image.shape[0])]
            hist_orientation_weighted = np.concatenate(histograms)
        return hist_orientation_weighted
    
    def get_histogram_blob_orientation(self, image, window=(3, 3), nb_interval=4, nb_directions=None):
        if image.ndim == 2:
            blob_orientation = self.get_blob_orientation(image, window, nb_interval, nb_directions).flatten()
        else:
            blob_orientations = [self.get_blob_orientation(image[channel], window, nb_interval, nb_directions).flatten() for channel in range(image.shape[0])]
            blob_orientation = np.concatenate(blob_orientations)
        return blob_orientation

if __name__ == "__main__":
    shape_describor = ShapeDescribor()
    image = np.zeros((3,448,448))
    print(image.shape)
    orientation = shape_describor.get_norm_and_orientation(image, "")
    print(orientation)
    blob_orientation = shape_describor.get_histogram_blob_orientation(orientation)
    print(blob_orientation)
