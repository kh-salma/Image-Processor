import os

# Directories Path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
converted_base_path = os.path.join(base_dir, 'Interface Graphique', 'InterfaceGraphique', 'Assets', 'Json Files', 'converted_BD_images')
histograms_json_files_path = os.path.join(base_dir, 'Interface Graphique', 'InterfaceGraphique', 'Assets', 'Json Files', 'histograms_BD_images')
descriptors_json_file_path = lambda color_space: os.path.join(histograms_json_files_path, color_space)

# Usable Variables
color_spaces = {
    "RGB": "rgb",
    "Grayscale Uniform": "gray_uniform",
    "Grayscale - Norme 601": "gray_601",
    "Grayscale - Norme 907": "gray_907",
    "YUV": "yuv",
    "YIQ": "yiq",
    "I1I2I3I": "i1i2i3",
    "Normalized RGB": "nrgb",
    "HSV": "hsv",
    "HSL": "hsl",
    "CMYK": "cmyk",
    "Indexed Image 2,2,2": "indexed_222",
    "Indexed Image 4,4,4": "indexed_444",
    "Indexed Image 8,8,8": "indexed_888",
}
gray_image_type = ["gray_uniform", "gray_601", "gray_907"]
h_image_type = ["hsv", "hsl"]
indexed_image_type = ["indexed_222", "indexed_444", "indexed_888"]
converted_json_files = [
    'cmyk__converted_images.json',
    'grey_601__converted_images.json',
    'grey_907__converted_images.json',
    'grey_uniform__converted_images.json',
    'hsl__converted_images.json',
    'hsv__converted_images.json',
    'i1i2i3__converted_images.json',
    'indexed_222__converted_images.json',
    'indexed_444__converted_images.json',
    'indexed_888__converted_images.json',
    'nrgb__converted_images.json',
    'rgb__converted_images.json',
    'yiq__converted_images.json',
    'yuv__converted_images.json'
]
descriptors = {
    "color": ["", "Histogram", "Hue Histogram", "Blob Histogram"],
    "shape": ["", "Orientation Histogram", "Norm Weighted Orientation Histogram", "Blob Orientation Histogram", "Blob Directional Histogram"],
    "texture": ["", "Statical Histogram", "LBP Histogram", "Blob LBP Histogram", "Haralick Histogram"],
    "cnn": ["", "MobileNet Model"]
}
hist_keys = {
    "color": {"Histogram": "hist", "Hue Histogram": "saturated_hue_hist", "Blob Histogram": "blob_hist"},
    "shape": {"Orientation Histogram": "orientation_hist", "Norm Weighted Orientation Histogram": "norm_weighted_orientation_hist",
                "Blob Orientation Histogram": "blob_orientation_hist", "Blob Directional Histogram": "blob_direction_hist"},
    "texture": {"Statical Histogram": "stats_hist", "LBP Histogram": "lbp_hist", "Blob LBP Histogram": "blob_lbp_hist", "Haralick Histogram": "haralick_hist"},
    "cnn": {"MobileNet Model": "cnn_vector"}
}
distances = ["euclidienne", "manhattan", "tchebychev", "intersection_histogramme_x", "intersection_histogramme_y", "chi_2", "minkowshki"]
shape_filters = ["sobel", "scharr", "prewitt"]
normalization = ["", "Probability", "Norm", "MinMax", "Standardization", "Rank"]
color_spaces_ = ["rgb", "gray_uniform", "gray_601", "gray_907", "yuv", "yiq", "i1i2i3", "nrgb", "hsv", "hsl", "cmyk", "indexed_222", "indexed_444", "indexed_888"]
