import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import numpy as np
import json
import sys
import os
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import glob
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from InterfaceGraphique.Preprocessor.FileSplitter import FileSplitter
from InterfaceGraphique.Filters.DistanceFilter import DistanceFilter
from InterfaceGraphique.Describors.Normalizer import Normalizer
from InterfaceGraphique.Assets.config import color_spaces, descriptors_json_file_path, gray_image_type, h_image_type, indexed_image_type, hist_keys

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        FileSplitter.recombine_texture_histograms(color_spaces, descriptors_json_file_path)
        self.distance_filter = DistanceFilter()

        self.requested_image_name = None
        self.color_space = None
        self.color_describor_entry = None
        self.shape_describor_entry = None
        self.filter_name = None
        self.texture_describor_entry = None
        self.cnn_describor_entry = None
        self.distance_filter_entry = None

        self.setup_window()
        self.create_layout()
        self.create_sidebar()
        self.create_main_content()

    def setup_window(self):
        self.title("DEEPSCAN")
        self.geometry("1500x1000")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

    def create_layout(self):
        self.header_label = ctk.CTkLabel(self, text="DEEPSCAN: POWERED IMAGE COMPARATOR", 
                                                   font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=5)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

    def create_sidebar(self):
        components = [
            ("Choose The Requested Image", "image_request_label", 0),
            ("Select The Color Space", "color_space_label", 1),
            ("Select The Distance Filter", "distances_label", 2),
            ("Select The Describor", "describors_label", 3),
            ("Color Describor", "color_describors_label", 4),
            ("Shape Describer", "shape_descriptor_label", 5),
            ("Choose Filter", "shape_filter_label", 6),
            ("Texture Describer", "texture_descriptor_label", 7),
            ("CNN Describer", "cnn_descriptor_label", 8),
            ("Normalization Method", "normalization_label", 9)
        ]

        for text, attr_name, row in components:
            setattr(self, attr_name, self.create_label(text, row))

        self.choose_image_button = ctk.CTkButton(self.sidebar_frame, text="Browse Image", command=self.choose_image)
        self.choose_image_button.grid(row=0, column=1, padx=30, pady=(20, 10), sticky="w")

        menus = [
            ("color_space_menu", ["RGB", "Grayscale Uniform", "Grayscale - Norme 601", "Grayscale - Norme 907", 
                                  "Indexed Image 2,2,2", "Indexed Image 4,4,4", "Indexed Image 8,8,8", "YIQ", "YUV", 
                                  "I1I2I3I", "Normalized RGB", "HSV", "HSL", "CMYK"], 1),
            ("distances_menu", ["Euclydienne", "Manhattan", "Tchebychev", "Histogrammes Intersection X", 
                                "Histogrammes Intersection Y", "Chi-2", "Minkowski"], 2),
            ("color_describor_menu", ["...", "Histogram", "Hue Histogram", "Blob Histogram"], 4),
            ("shape_describor_menu", ["...", "Orientation Histogram", "Norm Weighted Orientation Histogram", 
                                      "Blob Orientation Histogram", "Blob Directional Histogram"], 5),
            ("shape_filter_menu", ["Sobel", "Scharr", "Prewitt"], 6),
            ("texture_describor_menu", ["...", "Statical Histogram", "LBP Histogram", "Blob LBP Histogram", "Haralick Histogram"], 7),
            ("cnn_describor_menu", ["...", "MobileNet Model"], 8),
            ("normalization_menu", ["...", "Probability", "Norm", "MinMax", "Standardization", "Rank"], 9)
        ]

        for attr_name, values, row in menus:
            setattr(self, attr_name, self.create_menu(attr_name, values, row))

        self.scan_button = ctk.CTkButton(self.sidebar_frame, text="Scan", command=self.scan_images, text_color="white")
        self.scan_button.grid(row=10, column=0, columnspan=2, padx=30, pady=40, sticky="ns")

        self.evaluation_button = ctk.CTkButton(self.sidebar_frame, text="Evaluation", command=self.show_evaluation_table, text_color="white", fg_color="green", hover_color="dark green")
        self.evaluation_button.grid(row=11, column=0, columnspan=2, padx=30, pady=(160, 10), sticky="ew")

    def create_main_content(self):
        self.requested_image_placeholder = ctk.CTkLabel(self, text="Requested Image", width=120, height=100, fg_color="white")
        self.requested_image_placeholder.grid(row=1, column=1, padx=0, pady=10, sticky="n")

        self.default_image_placeholder = ctk.CTkFrame(self, width=800, height=400)
        self.default_image_placeholder.grid(row=1, rowspan=4, column=1, columnspan=5, padx=0, pady=(10,0))

        self.returned_image = 18
        self.images_placeholders(self.returned_image)

        self.image_count_entry = ctk.CTkEntry(self.default_image_placeholder, placeholder_text="Nb. Images (max.18)")
        self.image_count_entry.grid(row=3, column=4, padx=0, pady=(0,10), sticky="ew")

        self.submit_button = ctk.CTkButton(self.default_image_placeholder, text="Reset", command=self.reset_images_placeholders, text_color="white", fg_color="gray", hover_color="dark gray")
        self.submit_button.grid(row=3, column=5, padx=10, pady=(0,10), sticky="w")

    def create_label(self, text, row, column=0, padx=20, pady=5):
        return ctk.CTkLabel(self.sidebar_frame, text=text, anchor="w", 
                                      font=ctk.CTkFont(size=14, weight="bold"), text_color="grey").grid(
                                      row=row, column=column, padx=padx, pady=pady, sticky="w")

    def create_menu(self, attr_name, values, row, column=1, padx=25, pady=5):
        menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=values,
            command=self.update_menu_options if attr_name == "color_space_menu" else None
        )
        menu.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
        setattr(self, attr_name, menu)
        return menu
    
    def update_menu_options(self, color_space_entry):
        color_options = ["...", "Histogram"]
        if color_spaces[color_space_entry] in h_image_type:
            color_options.append("Hue Histogram")
        if color_spaces[color_space_entry] in gray_image_type + h_image_type + indexed_image_type:
            color_options.append("Blob Histogram")
        
        shape_options = ["...", "Orientation Histogram", "Norm Weighted Orientation Histogram"]
        if color_spaces[color_space_entry] in gray_image_type + h_image_type + indexed_image_type:
            shape_options.append("Blob Orientation Histogram")
            shape_options.append("Blob Directional Histogram")

        texture_options = ["...", "Statical Histogram", "LBP Histogram", "Haralick Histogram"]
        if color_spaces[color_space_entry] in gray_image_type + h_image_type + indexed_image_type:
            texture_options.append("Blob LBP Histogram")

        self.color_describor_menu.configure(values=color_options)
        self.color_describor_menu.set(color_options[0])
        
        self.shape_describor_menu.configure(values=shape_options)
        self.shape_describor_menu.set(shape_options[0])

        self.texture_describor_menu.configure(values=texture_options)
        self.texture_describor_menu.set(texture_options[0])

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        ).replace("/", "\\")
        
        if file_path:
            # Extract the image name
            image_name = os.path.basename(file_path)
            
            # Find the "BD_images" directory in the file path
            parts = file_path.split(os.sep)  # Split the path into parts
            try:
                # Find the index of "BD_images" in the path
                bd_images_index = parts.index("BD_images")
                # Reconstruct the directory path up to "BD_images"
                directory_path = os.sep.join(parts[:bd_images_index + 1])
            except ValueError:
                # If "BD_images" is not found, use the parent directory of the image
                directory_path = os.path.dirname(file_path)
                print("Warning: 'BD_images' directory not found in the file path.")
            
            # Conserve the directory path and image name (e.g., store them as attributes)
            self.directory_path = directory_path
            self.requested_image_name = image_name
            
            # Display the image
            self.display_image(self.requested_image_placeholder, self.requested_image_name)

    def display_image(self, widget, image_name):
        search_pattern = os.path.join(self.directory_path, '**', image_name)
        matching_files = glob.glob(search_pattern, recursive=True)
        
        if not matching_files:
            print(f"No image found with the name '{image_name}' in '{self.directory_path}' or its subdirectories.")
            return
        
        # Use the first matching file 
        file_path = matching_files[0]
        
        # Open and display the image
        image = Image.open(file_path)
        self.resized_requested_image = image.resize((120, 100)) 
        ctk_image = ctk.CTkImage(self.resized_requested_image, size=(120, 100))  
        widget.configure(image=ctk_image, text="")
        widget.image = ctk_image

    def images_placeholders(self, number):
        number = min(number, 18)
        mod = number % 6
        rows = number // 6 + (1 if mod != 0 else 0)
        self.image_labels = []
        for row in range(rows):
            columns = mod if row == rows - 1 and mod != 0 else 6
            for column in range(columns):
                image_placeholder = ctk.CTkLabel(self.default_image_placeholder, text="", anchor="w", width=120, height=100, fg_color="white")
                image_placeholder.grid(row=row, column=column, padx=20, pady=20, sticky="w")
                self.image_labels.append(image_placeholder)

    def reset_images_placeholders(self):
        for widget in self.default_image_placeholder.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.destroy()
        self.returned_image = int(self.image_count_entry.get())
        self.images_placeholders(self.returned_image)

    def set_images(self, images_path):
        for image_path, label in zip(images_path, self.image_labels):
            self.display_image(label, image_path)

    def scan_images(self):
        self.color_space = self.color_space_menu.get()
        self.color_describor_entry = self.color_describor_menu.get()
        self.shape_describor_entry = self.shape_describor_menu.get()
        self.filter_name = self.shape_filter_menu.get().lower()
        self.texture_describor_entry = self.texture_describor_menu.get()
        self.cnn_describor_entry = self.cnn_describor_menu.get()
        self.distance_filter_entry = self.distances_menu.get()

        if not self.requested_image_name:
            tkinter.messagebox.showerror("Invalid Image", "Please select an image.")
            return

        if self.color_describor_entry == "..." and self.shape_describor_entry == "..." and self.texture_describor_entry == "..." and self.cnn_describor_entry == "...":
            tkinter.messagebox.showerror("Invalid Combination", "Please select at least one describor.")
            return

        if self.color_describor_entry == "Hue Histogram" and color_spaces[self.color_space] not in h_image_type:
            tkinter.messagebox.showerror("Invalid Combination", "Hue Histogram is only available for HSV and HSL color spaces.")
            return
        
        if ("Blob" in self.color_describor_entry or "Blob" in self.shape_describor_entry or "Blob" in self.texture_describor_entry)  and color_spaces[self.color_space] not in gray_image_type + h_image_type + indexed_image_type:
            tkinter.messagebox.showerror("Invalid Combination", "Blob Histogram is only available for Grayscale, HSV, HSL, and Indexed Image color spaces.")
            return

        distance_filters = {
            "Euclydienne": self.distance_filter.distance_euclidienne,
            "Manhattan": self.distance_filter.distance_manhattan,
            "Tchebychev": self.distance_filter.distance_tchebychev,
            "Histogrammes Intersection X": self.distance_filter.distance_intersection_histogrammes,
            "Histogrammes Intersection Y": self.distance_filter.distance_intersection_histogrammes,
            "Chi-2": self.distance_filter.distance_chi_2,
            "Minkowski": self.distance_filter.distance_minkowshki
        }

        self.images_hist_dict = {}

        if self.color_space in color_spaces:
            self.process_descriptors("color")
            self.process_descriptors("shape", self.filter_name)
            self.process_descriptors("texture")
            self.process_descriptors("cnn")

        requested_image_hist = np.concatenate(self.images_hist_dict[self.requested_image_name])
        distances = {}

        match self.distance_filter_entry:
            case "Euclydienne" | "Manhattan" | "Tchebychev" | "Chi-2" | "Minkowski" | "Histogrammes Intersection X":
                distance_func = distance_filters[self.distance_filter_entry]
                for image_name, hist in self.images_hist_dict.items():
                    hist = np.concatenate(hist)
                    if image_name != self.requested_image_name:  
                        distances[image_name] = distance_func(requested_image_hist, hist)

            case "Histogrammes Intersection Y":
                intersection_func = distance_filters[self.distance_filter_entry]
                for image_name, hist in self.images_hist_dict.items():
                    hist = np.concatenate(hist)
                    if image_name != self.requested_image_name:  
                        distances[image_name] = intersection_func(hist, requested_image_hist)

        sorted_distances = sorted(distances.items(), key=lambda item: item[1])
        top_closest = sorted_distances[:self.returned_image]
        top_image_paths = [image_name for image_name, distance in top_closest]
        self.set_images(top_image_paths)


    def process_descriptors(self, descriptor_type, filter_name=None):
        if descriptor_type == "cnn":
            descriptor_file = descriptors_json_file_path("rgb") + f"\\{descriptor_type}_vectors.json"
        else:
            descriptor_file = descriptors_json_file_path(color_spaces[self.color_space]) + f"\\{descriptor_type}_histograms.json"
            
        try:
            with open(descriptor_file, 'r', encoding='utf-8') as json_file:
                descriptors_dict = json.load(json_file)
                descriptor_entry = getattr(self, f"{descriptor_type}_describor_entry")
                if descriptor_entry == "...":
                    return
                hist_key = self.get_hist_key(descriptor_type, descriptor_entry)

                for image_name, image_hists in descriptors_dict.items():
                    if image_name not in self.images_hist_dict:
                        self.images_hist_dict[image_name] = []
                    if descriptor_type == "shape" and filter_name:
                        hist = np.array(image_hists[hist_key][filter_name])
                    else:
                        hist = np.array(image_hists[hist_key])
                    
                    # Apply normalization
                    normalized_hist = self.normalize_histogram(hist)
                    self.images_hist_dict[image_name].append(normalized_hist)
                    
        except FileNotFoundError:
            tkinter.messagebox.showerror("Error", f"The file {descriptor_file} does not exist.")
        except json.JSONDecodeError:
            tkinter.messagebox.showerror("Error", f"Failed to decode JSON from {descriptor_file}.")

    def normalize_histogram(self, histogram):
        normalization_method = self.normalization_menu.get()
        normalizer = Normalizer()
        
        if normalization_method == "Probability":
            return normalizer.probability_normalization(histogram)
        elif normalization_method == "Norm":
            return normalizer.norm_normalization(histogram)
        elif normalization_method == "MinMax":
            return normalizer.minmax_normalization(histogram)
        elif normalization_method == "Standardization":
            return normalizer.standardization(histogram)
        elif normalization_method == "Rank":
            return normalizer.rank_normalization(histogram)
        else:
            return histogram  # No normalization

    def get_hist_key(self, descriptor_type, descriptor_entry):
        return hist_keys[descriptor_type][descriptor_entry]
    
    def show_evaluation_table(self):
        try:
            self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)  # 5-second timeout
            self.db = self.mongo_client["image_retrieval"]
            self.collection = self.db["evaluation_results"]
            self.map_collection = self.db["map_results"]
            # Check if the server is available
            self.mongo_client.server_info()  # This will raise an exception if the server is not reachable
            
            print("Successfully connected to the MongoDB server.")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            # Handle the case where the server is not found or unavailable
            raise Exception(f"Failed to connect to the MongoDB server. Make sure the server is running and accessible.")
        
        # Hide main content
        self.sidebar_frame.grid_remove()
        self.default_image_placeholder.grid_remove()
        self.requested_image_placeholder.grid_remove()

        # Create evaluation frame
        self.evaluation_frame = ctk.CTkFrame(self)
        self.evaluation_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        self.evaluation_frame.grid_columnconfigure(0, weight=1)
        self.evaluation_frame.grid_rowconfigure(1, weight=1)

        # Add return button
        self.return_button = ctk.CTkButton(self.evaluation_frame, text="Return", command=self.return_to_main, text_color="white", fg_color="gray", hover_color="dark gray")
        self.return_button.grid(row=0, column=0, padx=20, pady=(20,0), sticky="nw")

        # Create table (example with 7 columns)
        columns = ("Rank", "Color Space", "Color Descriptor", "Shape Descriptor", "Shape Filter", "Texture Descriptor", "CNN Filter", "Distance", "MAP")
        self.table = tkinter.ttk.Treeview(self.evaluation_frame, columns=columns, show='headings', style="Custom.Treeview")
        style = tkinter.ttk.Style()
        style.configure("Custom.Treeview.Heading", font=('Helvetica', 16, 'bold'), foreground="gray")
        style.configure("Custom.Treeview", font=('Helvetica', 14), rowheight=40)

        for col in columns:
            self.table.heading(col, text=col)
            if col in ["Rank", "MAP"]:
                self.table.column(col, width=80, anchor="center")
            else:
                self.table.column(col, width=150, anchor="center")

        self.table.grid(row=1, column=0, padx=50, pady=50, sticky="nsew")

        # Retrieve data from MongoDB and populate the table
        results = self.map_collection.find().sort("map", -1)
        for rank, result in enumerate(results, start=1):
            combo = result['combination']
            self.table.insert("", "end", values=(
                rank,
                combo['color_space'] or "-",
                combo['color_desc'] or "-",
                combo['shape_desc'] or "-",
                combo['shape_filter'] or "-",
                combo['texture_desc'] or "-",
                combo['cnn_desc'] or "-",
                combo['distance'] or "-",
                f"{result['map']:.4f}"
            ))

    def return_to_main(self):
        # Hide evaluation frame
        self.evaluation_frame.grid_remove()

        # Show main content
        self.sidebar_frame.grid()
        self.default_image_placeholder.grid()
        self.requested_image_placeholder.grid()
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
