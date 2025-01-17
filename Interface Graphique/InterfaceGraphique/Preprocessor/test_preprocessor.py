import os
import cv2
import json
import numpy as np
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from InterfaceGraphique.Preprocessor.ColorConversion import ColorConversion
from InterfaceGraphique.Describors.ShapeDescribor import ShapeDescribor
from InterfaceGraphique.Assets.config import gray_image_type, h_image_type, indexed_image_type


class Preprocessor:
    def __init__(self):
        self.color_conversion = ColorConversion()
        self.shape_describor = ShapeDescribor()
        self.color_spaces = {
            # "rgb": lambda img: img,
            "gray_uniform": self.color_conversion.rgb2gray_uniform,
            # "gray_601": self.color_conversion.rgb2gray_601,
            # "gray_907": self.color_conversion.rgb2gray_907,
            # "yuv": self.color_conversion.rgb2yuv,
            # "yiq": self.color_conversion.rgb2yiq,
            # "i1i2i3": self.color_conversion.rgb_to_i1i2i3,
            # "nrgb": self.color_conversion.rgb_to_nrgb,
            # "hsv": self.color_conversion.rgb_to_hsv,
            # "hsl": self.color_conversion.rgb_to_hsl,
            # "cmyk": self.color_conversion.rgb_to_cmyk,
            # "indexed_222": lambda img: self.color_conversion.rgb_to_indexed_image(img, 2, 2, 2),
            # "indexed_444": lambda img: self.color_conversion.rgb_to_indexed_image(img, 4, 4, 4),
            # "indexed_888": lambda img: self.color_conversion.rgb_to_indexed_image(img, 8, 8, 8)
        }
    
    def process_images_and_save_histograms(self, input_folder, output_folder):
        for color_space, conversion_func in self.color_spaces.items():
            # Create a directory for each color space
            color_space_folder = os.path.join(output_folder, color_space)
            if not os.path.exists(color_space_folder):
                os.makedirs(color_space_folder)

            # Initialize dictionaries to store data for each descriptor
            shape_histograms = {}

            for root, _, files in os.walk(input_folder):
                for file in files:
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        file_path = os.path.join(root, file)
                        image = cv2.imread(file_path)

                        if image is None:
                            print(f"Warning: Unable to read {file_path}. Skipping.")
                            continue

                        try:
                            resized_image = cv2.resize(image, (448, 448))
                            adapted_image = np.transpose(resized_image, (2, 0, 1))
                            converted_image = conversion_func(adapted_image)

                            canaux = None
                            if color_space in indexed_image_type:
                                parts = color_space.split("_")
                                canaux = tuple(map(int, parts[1]))

                            print("Shape Descriptors")
                            # Process and store shape descriptors
                            orientation = {
                                filter_name: self.shape_describor.get_norm_and_orientation(converted_image, filter_name)[1]
                                if color_space in gray_image_type + h_image_type + indexed_image_type else None
                                for filter_name in ["sobel", "scharr", "prewitt"]
                            }
                            shape_histograms[file_path] = {
                                "orientation_hist": {
                                    filter_name: self.shape_describor.get_histogram_orientation(converted_image, filter=filter_name).tolist()
                                    for filter_name in ["sobel", "scharr", "prewitt"]
                                },
                                "norm_weighted_orientation_hist": {
                                    filter_name: self.shape_describor.get_norm_weighted_histogram_orientation(converted_image, filter=filter_name).tolist()
                                    for filter_name in ["sobel", "scharr", "prewitt"]
                                },
                                "blob_orientation_hist": {
                                    filter_name: self.shape_describor.get_histogram_blob_orientation(orientation[filter_name]).tolist()
                                    if color_space in gray_image_type + h_image_type + indexed_image_type else None
                                    for filter_name in ["sobel", "scharr", "prewitt"]
                                },
                                "blob_direction_hist": {
                                    filter_name: self.shape_describor.get_histogram_blob_orientation(orientation[filter_name], nb_directions=8).tolist()
                                    if color_space in gray_image_type + h_image_type + indexed_image_type else None
                                    for filter_name in ["sobel", "scharr", "prewitt"]
                                }
                            }

                        except Exception as e:
                            print(f"Error processing {file_path} in {color_space}: {e}")

            # Save data for this color space
            self.save_to_file(color_space_folder, "shape_histograms.json", shape_histograms)
            
    @staticmethod
    def save_to_file(output_folder, file_name, data):
        output_path = os.path.join(output_folder, file_name)
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Saved data to {output_path}")


if __name__ == "__main__":
    preprocessor = Preprocessor()
    preprocessor.process_images_and_save_histograms(
        "/home/salmak/Documents/projects/Image-Processor/Interface Graphique/InterfaceGraphique/Assets/BD_images",
        "/home/salmak/Documents/projects/Image-Processor/Interface Graphique/InterfaceGraphique/Assets/Json Files"
    )
