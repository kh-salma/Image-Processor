import numpy as np
import os
import cv2
import json
import gc

class ColorConversion:
    """
    A class that contains methods for converting RGB images to various color spaces.
    """
    
    def rgb2gray_uniform(self, image):
        """
        Converts an RGB image to grayscale using a uniform method (average of the RGB channels).

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - Grayscale image as a numpy array with the same dimensions as the input.
        """
        return np.mean(image, axis=0).astype(np.uint8)
    
    def rgb2gray_601(self, image):
        """
        Converts an RGB image to grayscale using the ITU-R BT.601 luma formula.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - Grayscale image as a numpy array.
        """
        return np.sum(image * (np.array([0.299, 0.587, 0.114])).reshape(3, 1, 1), axis=0).astype(int)
    
    def rgb2gray_907(self, image):
        """
        Converts an RGB image to grayscale using the ITU-R BT.709 luma formula.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - Grayscale image as a numpy array.
        """
        return np.sum(image * (np.array([0.2125, 0.7154, 0.0721])).reshape(3, 1, 1), axis=0).astype(int)
    
    def rgb2yuv(self, image):
        """
        Converts an RGB image to YUV color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - YUV image as a numpy array.
        """
        yuv_matrix = np.array([[0.299, 0.587, 0.114], 
                               [-0.147, -0.289, 0.436], 
                               [0.615, -0.515, -0.100]])
        yuv_image = np.dot(image.reshape(-1, 3), yuv_matrix.T).reshape(image.shape)
        return yuv_image.astype(int)
    
    def rgb2yiq(self, image):
        """
        Converts an RGB image to YIQ color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - YIQ image as a numpy array.
        """
        yiq_matrix = np.array([[0.299, 0.587, 0.114], 
                               [0.596, -0.274, -0.322], 
                               [0.211, -0.253, -0.312]])
        yiq_image = np.dot(image.reshape(-1, 3), yiq_matrix.T).reshape(image.shape)
        return yiq_image.astype(int)
    
    def rgb_to_i1i2i3(self, image):
        """
        Converts an RGB image to the I1I2I3 color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - I1I2I3 image as a numpy array.
        """
        R = image[0, :, :]
        G = image[1, :, :]
        B = image[2, :, :]
        I1 = (R + G + B) / 3
        I2 = (R - B) / 2
        I3 = (2 * G - (R + B)) / 4
        i1i2i3_image = np.stack((I1, I2, I3), axis=0)
        return i1i2i3_image.astype(int)
    
    def rgb_to_nrgb(self, image):
        """
        Converts an RGB image to normalized RGB (nRGB) color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - nRGB image as a numpy array.
        """
        R = image[0, :, :]
        G = image[1, :, :]
        B = image[2, :, :]
        sum_rgb = R + G + B
        sum_rgb[sum_rgb == 0] = 1  # Prevent division by zero
        R_ = R / sum_rgb
        G_ = G / sum_rgb
        B_ = B / sum_rgb
        nrgb_image = np.stack((R_, G_, B_), axis=0)
        return nrgb_image.astype(int)
    
    def rgb_to_hsv(self, image):
        """
        Converts an RGB image to HSV (Hue, Saturation, Value) color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - HSV image as a numpy array with H, S, and V channels.
        """
        R = image[0, :, :] / 255.0
        G = image[1, :, :] / 255.0
        B = image[2, :, :] / 255.0

        Cmax = np.max([R, G, B], axis=0)
        Cmin = np.min([R, G, B], axis=0)
        delta = Cmax - Cmin

        H = np.zeros_like(Cmax)
        S = np.zeros_like(Cmax)
        V = Cmax

        mask = delta != 0
        idx = (Cmax == R) & mask
        H[idx] = np.mod((60 * ((G[idx] - B[idx]) / delta[idx])), 360)

        idx = (Cmax == G) & mask
        H[idx] = (60 * ((B[idx] - R[idx]) / delta[idx])) + 120

        idx = (Cmax == B) & mask
        H[idx] = (60 * ((R[idx] - G[idx]) / delta[idx])) + 240

        H = np.round(H).astype(int)

        S[Cmax != 0] = delta[Cmax != 0] / Cmax[Cmax != 0]
        S = np.round(S * 100).astype(int)

        V = np.round(V * 100).astype(int)

        return np.stack((H, S, V), axis=0)
    
    def rgb_to_hsl(self, image):
        """
        Converts an RGB image to HSL (Hue, Saturation, Lightness) color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - HSL image as a numpy array with H, S, and L channels.
        """
        R = image[0, :, :] / 255.0
        G = image[1, :, :] / 255.0
        B = image[2, :, :] / 255.0

        Cmax = np.max([R, G, B], axis=0)
        Cmin = np.min([R, G, B], axis=0)
        delta = Cmax - Cmin

        H = np.zeros_like(Cmax)
        S = np.zeros_like(Cmax)
        L = (Cmax + Cmin) / 2

        mask = delta != 0
        idx = (Cmax == R) & mask
        H[idx] = np.mod((60 * ((G[idx] - B[idx]) / delta[idx])), 360)

        idx = (Cmax == G) & mask
        H[idx] = (60 * ((B[idx] - R[idx]) / delta[idx])) + 120

        idx = (Cmax == B) & mask
        H[idx] = (60 * ((R[idx] - G[idx]) / delta[idx])) + 240

        H = np.round(H).astype(int)

        idx1 = (delta != 0) & (L != 0) & (L != 1)
        S[idx1] = delta[idx1] / (1 - np.abs(2 * L[idx1] - 1))
        S = np.round(S * 100).astype(int)

        L = np.round(L * 100).astype(int)

        return np.stack((H, S, L), axis=0)
    
    def rgb_to_cmyk(self, image):
        """
        Converts an RGB image to CMYK (Cyan, Magenta, Yellow, Key/Black) color space.

        Parameters:
        - image: numpy array representing an RGB image.

        Returns:
        - CMYK image as a numpy array with C, M, Y, and K channels.
        """
        R = image[0, :, :] / 255.0
        G = image[1, :, :] / 255.0
        B = image[2, :, :] / 255.0

        K = 1 - np.max([R, G, B], axis=0)

        C = np.zeros_like(K)
        M = np.zeros_like(K)
        Y = np.zeros_like(K)

        mask = (K != 1)
        C[mask] = (1 - R[mask] - K[mask]) / (1 - K[mask])
        M[mask] = (1 - G[mask] - K[mask]) / (1 - K[mask])
        Y[mask] = (1 - B[mask] - K[mask]) / (1 - K[mask])

        C = np.round(C * 100).astype(int)
        M = np.round(M * 100).astype(int)
        Y = np.round(Y * 100).astype(int)
        K = np.round(K * 100).astype(int)

        return np.stack((C, M, Y, K), axis=0)
    
    def rgb_to_indexed_image(self, image, quantity_r, quantity_g, quantity_b):
        """
        Converts an RGB image to an indexed image using quantization for each color channel.

        Parameters:
        - image (numpy.ndarray): A 3D numpy array representing an RGB image (3 x height x width).
        - quantity_r (int): The number of quantization levels for the red channel.
        - quantity_g (int): The number of quantization levels for the green channel.
        - quantity_b (int): The number of quantization levels for the blue channel.

        Returns:
        - numpy.ndarray: A 2D numpy array representing the indexed image, where each pixel is 
        a single integer value corresponding to the quantized color.
        """
        R = image[0, :, :]
        G = image[1, :, :]
        B = image[2, :, :]

        pr = 256 / quantity_r
        pg = 256 / quantity_g
        pb = 256 / quantity_b

        index_r = (R / pr).astype(int)
        index_g = (G / pg).astype(int)
        index_b = (B / pb).astype(int)

        result_img = index_b * (quantity_r * quantity_g) + index_g * quantity_r + index_r
        return result_img
    
    def process_stock_converted_images(self, input_folder, output_folder):
        """
        Processes images by applying multiple color space conversions and saving the results
        in separate JSON files for each color space.

        Parameters:
        - input_folder (str): The folder containing the images to process.
        - output_folder (str): The folder where the JSON files will be stored.
        """

        color_spaces = {
            "rgb": lambda img: img,
            "gray_uniform": self.rgb2gray_uniform,
            "gray_601": self.rgb2gray_601,
            "gray_907": self.rgb2gray_907,
            "yuv": self.rgb2yuv,
            "yiq": self.rgb2yiq,
            "i1i2i3": self.rgb_to_i1i2i3,
            "nrgb": self.rgb_to_nrgb,
            "hsv": self.rgb_to_hsv,
            "hsl": self.rgb_to_hsl,
            "cmyk": self.rgb_to_cmyk,
            "indexed_222": lambda img: self.rgb_to_indexed_image(img, 2, 2, 2),
            "indexed_444": lambda img: self.rgb_to_indexed_image(img, 4, 4, 4),
            "indexed_888": lambda img: self.rgb_to_indexed_image(img, 8, 8, 8)
        }

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Dictionnaires pour stocker les résultats pour chaque espace colorimétrique
        image_data_by_space = {space: {} for space in color_spaces.keys()}

        for root, dirs, files in os.walk(input_folder):
            print(root)
            for file in files:
                if file.endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(root, file)
                    image = cv2.imread(file_path, cv2.COLOR_BGR2RGB)
                    resized_image = cv2.resize(image, (448,448))

                    if image is not None:
                        adapted_image = np.transpose(resized_image, (2, 1, 0))

                        # Traitement de chaque espace colorimétrique
                        for color_space, conversion_func in color_spaces.items():
                            converted_image = conversion_func(adapted_image)
                            converted_image_list = converted_image.tolist()
                            # Ajout des résultats au dictionnaire
                            image_data_by_space[color_space][file_path] = converted_image_list

                        # Force la collecte des déchets pour libérer la mémoire
                        gc.collect()

        for color_space, image_data in image_data_by_space.items():
            output_json_path = os.path.join(output_folder, f"{color_space}_converted_images.json")
            with open(output_json_path, 'w', encoding='utf-8') as json_file:
                json.dump(image_data, json_file, ensure_ascii=False)

        print("Conversion complète. Fichiers JSON créés pour chaque espace colorimétrique.")

if __name__ == "__main__":
    color_conversion = ColorConversion()
    base_images = color_conversion.process_stock_converted_images(
        "C:\\Users\\salma\\OneDrive\\Documents\\URCA - M2\\INF00903\\Projet\\BD_images",
        "C:/Users/salma/OneDrive/Documents/URCA - M2/INF00903/Projet/converted_BD_images"
    )