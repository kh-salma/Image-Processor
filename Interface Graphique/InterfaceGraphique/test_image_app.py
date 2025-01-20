import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import numpy as np
import json
from InterfaceGraphique.Filters.DistanceFilter import DistanceFilter
from InterfaceGraphique.Describors.ColorDescribor import ColorDescribor
from InterfaceGraphique.Assets.config import color_spaces, descriptors_json_file_path

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DEEPSCAN")
        self.geometry("1500x1000")
        
        self.grid_columnconfigure((0, 1), weight=(0, 1))
        self.grid_rowconfigure((0, 1), weight=(0, 1))
        
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
    def create_header(self):
        self.header_label = ctk.CTkLabel(self, text="DEEPSCAN: POWERED IMAGE COMPARATOR", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, pady=10)

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=5)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        elements = [
            ("Choose The Requested Image", None),
            ("Browse Image", self.choose_image),
            ("Select The Color Space", color_spaces),
            ("Select The Distance Filter", [
                "Euclydienne", "Manhattan", "Tchebychev", 
                "Histogrammes Intersection X", "Histogrammes Intersection Y", 
                "Chi-2", "Minkowski"
            ]),
            ("Select The Describor", None),
            ("Color Describor", ["Histogram", "Hue Histogram", "Blob Histogram"]),
            ("Shape Describer", [
                "Orientation Histogram", "Norm Weighted Orientation Histogram", 
                "Blob Orientation Histogram", "Blob Directional Histogram"
            ]),
            ("Shape Filter", ["Sobel filter", "Prewitt filter", "Scharr"]),
            ("Texture Describer", [
                "Statical Histogram", "LBP Histogram", "Blob LBP Histogram", 
                "Haralick Histogram"
            ]),
            ("CNN Describer", ["ImageNet Model"]),
            ("Scan", self.scan_images),
            ("Evaluate All Combinations", self.evaluate_combinations)
        ]

        for idx, (label, action_or_values) in enumerate(elements):
            if isinstance(action_or_values, list):
                menu = ctk.CTkOptionMenu(self.sidebar_frame, values=action_or_values)
                menu.grid(row=idx, column=1, padx=20, pady=(10, 10), sticky="ew")
                setattr(self, f"{label.lower().replace(' ', '_')}_menu", menu)
            elif callable(action_or_values):
                button = ctk.CTkButton(self.sidebar_frame, text=label, command=action_or_values)
                button.grid(row=idx, column=0, columnspan=2, padx=30, pady=20, sticky="ew")
            else:
                label_widget = ctk.CTkLabel(
                    self.sidebar_frame, text=label, 
                    anchor="w", font=ctk.CTkFont(size=14, weight="bold"), text_color="grey"
                )
                label_widget.grid(row=idx, column=0, padx=20, pady=(10, 10), sticky="w")

    def create_main_content(self):
        self.requested_image_placeholder = ctk.CTkLabel(self, text="Requested Image", width=120, height=100, fg_color="white")
        self.requested_image_placeholder.grid(row=1, column=1, padx=0, pady=10, sticky="n")

        self.default_image_placeholder = ctk.CTkFrame(self, width=800, height=400)
        self.default_image_placeholder.grid(row=1, rowspan=4, column=1, columnspan=5, padx=0, pady=(10,0))

        self.returned_image = 18
        self.images_placeholders(self.returned_image)

        self.image_count_entry = ctk.CTkEntry(self.default_image_placeholder, placeholder_text="Nb. Images (max.18)")
        self.image_count_entry.grid(row=3, column=4, padx=0, pady=(0,10), sticky="ew")

        self.submit_button = ctk.CTkButton(self.default_image_placeholder, text="Reset", command=self.reset_images_placeholders)
        self.submit_button.grid(row=3, column=5, padx=10, pady=(0,10), sticky="w")

    def choose_image(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]).replace("/","\\")
        if self.file_path:
            self.display_image(self.requested_image_placeholder, self.file_path)

    def display_image(self, widget, file_path):
        image = Image.open(file_path)
        self.resized_requested_image = image.resize((120, 100))
        ctk_image = ctk.CTkImage(self.resized_requested_image, size=(120, 100))
        widget.configure(image=ctk_image, text="")
        widget.image = ctk_image

    def images_placeholders(self, number):
        number = min(number, 18)
        rows = (number + 5) // 6
        for row in range(rows):
            columns = min(6, number - row * 6)
            for column in range(columns):
                image_placeholder = ctk.CTkLabel(self.default_image_placeholder, text="", anchor="w", width=120, height=100, fg_color="white")
                image_placeholder.grid(row=row, column=column, padx=20, pady=20, sticky="w")

    def reset_images_placeholders(self):
        for widget in self.default_image_placeholder.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.destroy()
        self.returned_image = int(self.image_count_entry.get())
        self.images_placeholders(self.returned_image)

    def set_images(self, images_path):
        for image_path, widget in zip(images_path, self.default_image_placeholder.winfo_children()):
            if isinstance(widget, ctk.CTkLabel):
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
            self.process_descriptors("color", images_hist_dict, requested_image_hists)
            self.process_descriptors("shape", images_hist_dict, requested_image_hists)
            self.process_descriptors("texture", images_hist_dict, requested_image_hists)

        requested_image_hist = np.concatenate(requested_image_hists)
        distances = {}

        match self.distance_describor_entry:
            case "Euclydienne" | "Manhattan" | "Tchebychev" | "Chi-2" | "Minkowski" | "Histogrammes Intersection X":
                distance_func = distance_describors[self.distance_describor_entry]
                for image_name, hist in images_hist_dict.items():
                    hist = np.concatenate(hist)
                    if image_name != self.file_path:  
                        distances[image_name] = distance_func(requested_image_hist, hist)

            case "Histogrammes Intersection Y":
                intersection_func = distance_describors[self.distance_describor_entry]
                for image_name, hist in images_hist_dict.items():
                    hist = np.concatenate(hist)
                    if image_name != self.file_path:  
                        distances[image_name] = intersection_func(hist, requested_image_hist)

        sorted_distances = sorted(distances.items(), key=lambda item: item[1])
        top_closest = sorted_distances[:self.returned_image]
        top_image_paths = [image_name for image_name, distance in top_closest]
        self.set_images(top_image_paths)


    def process_descriptors(self, descriptor_type, images_hist_dict, requested_image_hists):
        descriptor_file = descriptors_json_file_path(self.color_space) + f"\\{descriptor_type}_histograms.json"
        try:
            with open(descriptor_file, 'r', encoding='utf-8') as json_file:
                descriptors_dict = json.load(json_file)
                descriptor_entry = getattr(self, f"{descriptor_type}_describor_entry")
                hist_key = self.get_hist_key(descriptor_type, descriptor_entry)
                
                requested_image_hists.append(np.array(descriptors_dict[self.file_path][hist_key]))
                for image_name, image_hists in descriptors_dict.items():
                    if image_name not in images_hist_dict:
                        images_hist_dict[image_name] = []
                    images_hist_dict[image_name].append(np.array(image_hists[hist_key]))
        except FileNotFoundError:
            print(f"Error: The file {descriptor_file} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {descriptor_file}.")

    def get_hist_key(self, descriptor_type, descriptor_entry):
        hist_keys = {
            "color": {"Histogram": "hist", "Hue Histogram": "saturated_hue_hist", "Blob Histogram": "blob_hist"},
            "shape": {"Orientation Histogram": "orientation_hist", "Norm Weighted Orientation Histogram": "norm_weighted_orientation_hist",
                      "Blob Orientation Histogram": "blob_orientation_hist", "Blob Directional Histogram": "blob_direction_hist"},
            "texture": {"Statical Histogram": "stats_hist", "LBP Histogram": "lbp_hist", "Blob LBP Histogram": "blob_lbp_hist"}
        }
        return hist_keys[descriptor_type][descriptor_entry]
    
    def evaluate_combinations(self):
        # Placeholder for MLP function implementation
        results = self.run_mlp_evaluation()
        
        # Create a new window to display the results table
        results_window = ctk.CTkToplevel(self)
        results_window.title("Evaluation Results")
        results_window.geometry("800x600")
        results_window.attributes('-topmost', True)  # Set high z-index
        
        # Create a table to display the results
        table = ctk.CTkFrame(results_window)
        table.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add table headers
        headers = ["Color Space", "Descriptor", "Distance", "Accuracy"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(table, text=header, font=ctk.CTkFont(size=14, weight="bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
        
        # Add table rows
        for row, result in enumerate(results, start=1):
            for col, value in enumerate(result):
                label = ctk.CTkLabel(table, text=str(value))
                label.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

    def run_mlp_evaluation(self):
        # Placeholder for MLP function
        # This should be replaced with the actual MLP implementation
        return [
            ["RGB", "Histogram", "Euclidean", 0.85],
            ["HSV", "Hue Histogram", "Manhattan", 0.78],
            ["LAB", "Blob Histogram", "Chi-2", 0.92],
            # Add more sample results as needed
        ]


if __name__ == "__main__":
    app = App()
    app.mainloop()
