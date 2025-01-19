import os
import cv2
import json
import numpy as np
import sys
from tqdm import tqdm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from InterfaceGraphique.Preprocessor.ColorConversion import ColorConversion
from InterfaceGraphique.Describors.ColorDescribor import ColorDescribor
from InterfaceGraphique.Describors.ShapeDescribor import ShapeDescribor
from InterfaceGraphique.Assets.config import gray_image_type, h_image_type, indexed_image_type, converted_base_path, converted_json_files


class Preprocessor:
    def __init__(self):
        self.color_conversion = ColorConversion()
        # self.color_describor = ColorDescribor()
        self.shape_describor = ShapeDescribor()

        self.color_spaces_data = {}
        for file_name in converted_json_files:
            with open(os.path.join(converted_base_path, file_name), 'r') as file:
                self.color_spaces_data[file_name.split('__')[0]] = json.load(file)
        
        self.color_spaces = {
            # "rgb": self.color_spaces_data['rgb'],
            # "gray_uniform": self.color_spaces_data['grey_uniform'],
            # "gray_601": self.color_spaces_data['grey_601'],
            # "gray_907": self.color_spaces_data['grey_907'],
            # "yuv": self.color_spaces_data['yuv'],
            # "yiq": self.color_spaces_data['yiq'],
            # "i1i2i3": self.color_spaces_data['i1i2i3'],
            # "nrgb": self.color_spaces_data['nrgb'],
            "hsv": self.color_spaces_data['hsv'], # Didn't execute well
            "hsl": self.color_spaces_data['hsl'], # Didn't execute well
            # "cmyk": self.color_spaces_data['cmyk'],
            # "indexed_222": self.color_spaces_data['indexed_222'],
            # "indexed_444": self.color_spaces_data['indexed_444'],
            # "indexed_888": self.color_spaces_data['indexed_888']
        }

    def get_image_data(self, image_path, color_space):
        if color_space in self.color_spaces:
            return self.color_spaces[color_space].get(image_path, None)
        return None
    
    def generate_color_space_converted_images(self, input_folder, output_folder):
        for color_space in self.color_spaces.keys():
            # Create a directory for each color space
            color_space_folder = os.path.join(output_folder, color_space)
            if not os.path.exists(color_space_folder):
                os.makedirs(color_space_folder)

            for root, _, files in os.walk(input_folder):
                for file in files:
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        image_path = os.path.join(root, file)
                        image = cv2.imread(image_path)

                        if image is None:
                            print(f"Warning: Unable to read {image_path}. Skipping.")
                            continue

                        try:
                            converted_image = self.color_conversion.rgb_to_color_space(image, color_space)
                            output_path = os.path.join(color_space_folder, file)
                            cv2.imwrite(output_path, converted_image)
                            print(f"Saved converted image to {output_path}")
                        except Exception as e:
                            print(f"Error processing {image_path} in {color_space}: {e}")
    
    
    def process_images_and_save_histograms(self, input_folder, output_folder):
        for color_space in self.color_spaces.keys():
            # Create a directory for each color space
            color_space_folder = os.path.join(output_folder, color_space)
            if not os.path.exists(color_space_folder):
                os.makedirs(color_space_folder)

            # Initialize dictionaries to store data for each descriptor
            shape_histograms = {}

            for root, _, files in os.walk(input_folder):
                for file in tqdm(files, desc=f"Processing {color_space} images"):
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        image_path = os.path.join(root, file)
                        image = np.array(self.get_image_data(image_path, color_space))

                        if image is None:
                            print(f"Warning: Unable to read {image_path}. Skipping.")
                            continue

                        try:
                            canaux = None
                            if color_space in indexed_image_type:
                                parts = color_space.split("_")
                                canaux = tuple(map(int, parts[1]))

                            # print("Color Descriptors")
                            # # Process and store color descriptors
                            # color_histograms[file_path] = {
                            #     "hist": self.color_describor.get_histogram(image).tolist(),
                            #     "saturated_hue_hist": (
                            #         self.color_describor.get_saturated_hue_histogram(image).tolist()
                            #         if color_space in h_image_type else None
                            #     ),
                            #     "blob_hist": (
                            #         self.color_describor.get_histogram_blob(image, color_space, canaux=canaux).tolist()
                            #         if color_space in gray_image_type + h_image_type + indexed_image_type else None
                            #     ),
                            # }

                            # print("Shape Descriptors")
                            # Process and store shape descriptors
                            orientation = {
                                filter_name: self.shape_describor.get_norm_and_orientation(image, filter_name)[1]
                                if color_space in gray_image_type + h_image_type + indexed_image_type else None
                                for filter_name in ["sobel", "scharr", "prewitt"]
                            }
                            shape_histograms[image_path] = {
                                "orientation_hist": {
                                    filter_name: self.shape_describor.get_histogram_orientation(image, filter=filter_name).tolist()
                                    for filter_name in ["sobel", "scharr", "prewitt"]
                                },
                                "norm_weighted_orientation_hist": {
                                    filter_name: self.shape_describor.get_norm_weighted_histogram_orientation(image, filter=filter_name).tolist()
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
                            print(f"Error processing {image_path} in {color_space}: {e}")

            # Save data for this color space
            # self.save_to_file(color_space_folder, "color_histograms.json", color_histograms)
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
        "C:\\Users\\salma\\OneDrive\\Documents\\URCA - M2\\INF00903\\Projet\\BD_images",
        "C:\\Users\\salma\\OneDrive\\Documents\\URCA - M2\\INF00903\\Projet\\Interface Graphique\\InterfaceGraphique\\Assets\\Json Files\\histograms_BD_images"
    )
