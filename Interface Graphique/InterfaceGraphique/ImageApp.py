import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import filedialog
from PIL import Image
import numpy as np
import json
from InterfaceGraphique.Filters.DistanceFilter import DistanceFilter
from InterfaceGraphique.Describors.ColorDescribor import ColorDescribor
from InterfaceGraphique.Assets.config import color_spaces, descriptors_json_file_path

customtkinter.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue", "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
    
        # configure window
        self.title("DEEPSCAN")
        self.geometry(f"{1500}x{1000}")  
        # self.attributes("-fullscreen", True)  

        # configure grid layout (2x2)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
         
        # create header (Title at the top)
        self.header_label = customtkinter.CTkLabel(self, text="DEEPSCAN: POWERED IMAGE COMPARATOR", font=customtkinter.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, pady=10)

        # create left sidebar (1/3 of interface)
        self.sidebar_frame = customtkinter.CTkFrame(self, width=300, corner_radius=5)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        # self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Sidebar content (Left section)
        self.image_request_label = customtkinter.CTkLabel(self.sidebar_frame, text="Choose The Requested Image", anchor="w", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="grey")
        self.image_request_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.choose_image_button = customtkinter.CTkButton(self.sidebar_frame, text="Browse Image", command=self.choose_image)
        self.choose_image_button.grid(row=0, column=1, padx=30, pady=(20, 10), sticky="w")

        # self.select_button = customtkinter.CTkButton(self.sidebar_frame, text="Select", command=self.select_processing)
        # self.select_button.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew")

        self.color_space_label = customtkinter.CTkLabel(self.sidebar_frame, text="Select The Color Space", anchor="w", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="grey")
        self.color_space_label.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="w")

        self.color_space_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["RGB", "Grayscale Uniform", "Grayscale - Norme 601", "Grayscale - Norme 907", "Indexed Image 2,2,2", "Indexed Image 4,4,4", "Indexed Image 8,8,8", "YIQ", "YUV", "I1I2I3I", "Normalized RGB", "HSV", "HSL", "LAB", "LUV", "CMYK"])
        self.color_space_menu.grid(row=1, column=1, padx=20, pady=(10, 10), sticky="ew")

        self.distances_label = customtkinter.CTkLabel(self.sidebar_frame, text="Select The Distance Filter", anchor="w", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="grey")
        self.distances_label.grid(row=2, column=0, padx=20, pady=(10, 10), sticky="w")

        self.distances_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Euclydienne", "Manhattan", "Tchebychev", "Histogrammes Intersection X", "Histogrammes Intersection Y", "Chi-2", "Minkowski"])
        self.distances_menu.grid(row=2, column=1, padx=20, pady=(10, 10), sticky="ew")

        self.describors_label = customtkinter.CTkLabel(self.sidebar_frame, text="Select The Describor", anchor="w", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="grey")
        self.describors_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")

        self.color_describors_label = customtkinter.CTkLabel(self.sidebar_frame, text="Color Describor", anchor="w", font=customtkinter.CTkFont(size=14), text_color="grey")
        self.color_describors_label.grid(row=4, column=0, padx=30, pady=5, sticky="w")
        self.color_describor_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Histogram", "Hue Histogram", "Blob Histogram"])
        self.color_describor_menu.grid(row=4, column=1, padx=25, pady=5, sticky="ew")

        self.shape_descriptor_label = customtkinter.CTkLabel(self.sidebar_frame, text="Shape Describer", anchor="w", font=customtkinter.CTkFont(size=14), text_color="grey")
        self.shape_descriptor_label.grid(row=5, column=0, padx=30, pady=5, sticky="w")
        self.shape_describor_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Orientation Histogram", "Norm Weighted Orientation Histogram", "Blob Orientation Histogram", "Blob Directional Histogram"])
        self.shape_describor_menu.grid(row=5, column=1, padx=25, pady=5, sticky="ew")

        self.texture_descriptor_label = customtkinter.CTkLabel(self.sidebar_frame, text="Texture Describer", anchor="w", font=customtkinter.CTkFont(size=14), text_color="grey")
        self.texture_descriptor_label.grid(row=6, column=0, padx=30, pady=5, sticky="w")
        self.texture_describor_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Statical Histogram", "LBP Histogram", "Blob LBP Histogram", "Haralick Histogram"])
        self.texture_describor_menu.grid(row=6, column=1, padx=25, pady=5, sticky="ew")
        
        self.cnn_descriptor_label = customtkinter.CTkLabel(self.sidebar_frame, text="CNN Describer", anchor="w", font=customtkinter.CTkFont(size=14), text_color="grey")
        self.cnn_descriptor_label.grid(row=7, column=0, padx=30, pady=5, sticky="w")
        self.cnn_describor_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["ImageNet Model", "", "", ""])
        self.cnn_describor_menu.grid(row=7, column=1, padx=25, pady=5, sticky="ew")

        self.scan_button = customtkinter.CTkButton(self.sidebar_frame, text="Scan", command=self.scan_images)
        self.scan_button.grid(row=8, column=0, columnspan=2, padx=30, pady=30, sticky="ns")

        # Main content (Right section)
        self.requested_image_placeholder = customtkinter.CTkLabel(self, text="Requested Image", width=120, height=100, fg_color="white")
        self.requested_image_placeholder.grid(row=1, column=1, padx=0, pady=10, sticky="n")

        self.default_image_placeholder = customtkinter.CTkFrame(self, width=800, height=400)
        self.default_image_placeholder.grid(row=1, rowspan=4, column=1, columnspan=5, padx=0, pady=(10,0))

        self.returned_image = 18
        self.images_placeholders(self.returned_image)

        self.image_count_entry = customtkinter.CTkEntry(self.default_image_placeholder, placeholder_text="Nb. Images (max.18)")
        self.image_count_entry.grid(row=3, column=4, padx=0, pady=(0,10), sticky="ew")

        self.submit_button = customtkinter.CTkButton(self.default_image_placeholder, text="Reset", command=self.reset_images_placeholders)
        self.submit_button.grid(row=3, column=5, padx=10, pady=(0,10), sticky="w")

    def choose_image(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        ).replace("/","\\")
        if self.file_path:
            self.display_image(self.requested_image_placeholder, self.file_path)

    def display_image(self, widget, file_path):
        image = Image.open(file_path)
        self.resized_requested_image = image.resize((120, 100)) 
        ctk_image = customtkinter.CTkImage(self.resized_requested_image, size=(120, 100))  
        widget.configure(image=ctk_image, text="")
        widget.image = ctk_image

    def images_placeholders(self, number):
        number = min(number, 18)
        mod = number % 6
        rows = number // 6 + (1 if mod != 0 else 0)
        elements = number
        for row in range(rows):
            columns = mod if row == rows - 1 and mod != 0 else 6
            for column in range(columns):
                self.image_placeholder = customtkinter.CTkLabel(self.default_image_placeholder, text="", anchor="w", width=120, height=100, fg_color="white")
                self.image_placeholder.grid(row=row, column=column, padx=20, pady=20, sticky="w")
            elements -= columns

    def reset_images_placeholders(self):
        for widget in self.default_image_placeholder.winfo_children():
            if isinstance(widget, customtkinter.CTkLabel):
                widget.destroy()
        self.returned_image = int(self.image_count_entry.get())
        self.images_placeholders(self.returned_image)

    def set_images(self, images_path):
        for index, (image_path,widget) in enumerate(zip(images_path, self.default_image_placeholder.winfo_children())):
            print(len(self.default_image_placeholder.winfo_children()))
            if isinstance(widget, customtkinter.CTkLabel):
                print(widget)
                print(image_path)
                self.display_image(widget, image_path)

    def scan_images(self):
        distance_describor = DistanceFilter()
        
        self.color_space = self.color_space_menu.get()
        self.color_describor_entry = self.color_describor_menu.get()
        self.shape_describor_entry = self.shape_describor_menu.get()
        self.texture_describor_entry = self.texture_describor_menu.get()
        self.cnn_describor_entry = self.cnn_describor_menu.get()
        self.distance_describor_entry = self.distances_menu.get()


        distance_describors = {
            "Euclydienne": distance_describor.distance_euclidienne,
            "Manhattan": distance_describor.distance_manhattan,
            "Tchebychev": distance_describor.distance_tchebychev,
            "Histogrammes Intersection X": distance_describor.intersection_histogrammes,
            "Histogrammes Intersection Y": distance_describor.intersection_histogrammes,
            "Chi-2": distance_describor.chi_2,
            "Minkowski": distance_describor.distance_minkowshki
        }

        images_hist_dict = {}
        requested_image_hists = []

        if self.color_space in color_spaces:
            color_describor_file = descriptors_json_file_path(self.color_space)+"\\color_histograms.json"
            try:
                with open(color_describor_file, 'r', encoding='utf-8') as json_file:
                    color_descriptors_dict = json.load(json_file)

                    match self.color_describor_entry:
                        case "Histogram":
                            requested_image_hists.append(np.array(color_descriptors_dict[self.file_path]["hist"]))
                            for image_name, image_hists in color_descriptors_dict.items():
                                images_hist_dict[image_name] = []
                                images_hist_dict[image_name].append(np.array(image_hists["hist"]))


                        case "Hue Histogram":
                            requested_image_hists.append(np.array(color_descriptors_dict[self.file_path]["saturated_hue_hist"]))
                            for image_name, image_hists in color_descriptors_dict.items():
                                images_hist_dict[image_name] = []
                                images_hist_dict[image_name].append(np.array(image_hists["saturated_hue_hist"]))

                        case "Blob Histogram":
                            requested_image_hists.append(np.array(color_descriptors_dict[self.file_path]["blob_hist"]))
                            for image_name, image_hists in color_descriptors_dict.items():
                                images_hist_dict[image_name] = []
                                images_hist_dict[image_name].append(np.array(image_hists["blob_hist"]))
 
            except FileNotFoundError:
                print(f"Error: The file {color_describor_file} does not exist.")
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {color_describor_file}.")

            shape_describor_file = descriptors_json_file_path(self.color_space)+"\\shape_histograms.json"
            try:
                with open(shape_describor_file, 'r', encoding='utf-8') as json_file:
                    shape_descriptors_dict = json.load(json_file)
                    image_hist = {}

                    match self.shape_describor_entry:
                        case "Orientation Histogram":
                            requested_image_hists.append(np.array(shape_descriptors_dict[self.file_path]["orientation_hist"]))
                            for image_name, image_hists in shape_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["orientation_hist"]))

                        case "Norm Weighted Orientation Histogram":
                            requested_image_hists.append(np.array(shape_descriptors_dict[self.file_path]["norm_weighted_orientation_hist"]))
                            for image_name, image_hists in shape_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["norm_weighted_orientation_hist"]))

                        case "Blob Orientation Histogram":
                            requested_image_hists.append(np.array(shape_descriptors_dict[self.file_path]["blob_orientation_hist"]))
                            for image_name, image_hists in shape_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["blob_orientation_hist"]))

                        case "Blob Directional Histogram":
                            requested_image_hists.append(np.array(shape_descriptors_dict[self.file_path]["blob_direction_hist"]))
                            for image_name, image_hists in shape_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["blob_direction_hist"]))
 
            except FileNotFoundError:
                print(f"Error: The file {shape_describor_file} does not exist.")
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {shape_describor_file}.")

            texture_describor_file = descriptors_json_file_path(self.color_space)+"\\texture_histograms.json"
            try:
                with open(texture_describor_file, 'r', encoding='utf-8') as json_file:
                    texture_descriptors_dict = json.load(json_file)
                    image_hist = {}

                    match self.texture_describor_entry:
                        case "Statical Histogram":
                            requested_image_hists.append(np.array(texture_descriptors_dict[self.file_path]["stats_hist"]))
                            for image_name, image_hists in texture_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["stats_hist"]))

                        case "LBP Histogram":
                            requested_image_hists.append(np.array(texture_descriptors_dict[self.file_path]["lbp_hist"]))
                            for image_name, image_hists in texture_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["lbp_hist"]))

                        case "Blob LBP Histogram":
                            requested_image_hists.append(np.array(texture_descriptors_dict[self.file_path]["blob_lbp_hist"]))
                            for image_name, image_hists in texture_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["blob_lbp_hist"]))

                        case "Haralick Histogram":
                            requested_image_hists.append(np.array(texture_descriptors_dict[self.file_path]["haralick_hist"]))
                            for image_name, image_hists in texture_descriptors_dict.items():
                                image_hist[image_name].append(np.array(image_hists["haralick_hist"]))
 
            except FileNotFoundError:
                print(f"Error: The file {texture_describor_file} does not exist.")
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON from {texture_describor_file}.")

            requested_image_hist = np.concatenate(requested_image_hists)
            distances = {}
            match self.distance_describor_entry:
                case "Euclydienne" | "Manhattan" | "Tchebychev" | "Chi-2" | "Minkowski" | "Histogrammes Intersection X":
                    distance_func = distance_describors[self.distance_describor_entry]
                    for image_name, hist in image_hist.items():
                        hist = np.concatenate(hist)
                        if image_name != self.file_path:  
                            distances[image_name] = distance_func(requested_image_hist, hist)

                case "Histogrammes Intersection Y":
                    intersection_func = distance_describors[self.distance_describor_entry]
                    for image_name, hist in image_hist.items():
                        hist = np.concatenate(hist)
                        if image_name != self.file_path:  
                            distances[image_name] = intersection_func(hist, requested_image_hist)

            sorted_distances = sorted(distances.items(), key=lambda item: item[1])
            top_closest = sorted_distances[:self.returned_image]
            print(top_closest)
            top_image_paths = [image_name for image_name, distance in top_closest]
            self.set_images(top_image_paths)

if __name__ == "__main__":
    app = App()
    app.mainloop()
