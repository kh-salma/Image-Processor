color_spaces = {
    "RGB": "rgb",
    "Grayscale Uniform": "grey_uniform",
    "Grayscale - Norme 601": "grey_601",
    "Grayscale - Norme 907": "grey_907",
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
converted_base_path = 'C:\\Users\\salma\\OneDrive\\Documents\\URCA - M2\\INF00903\\Projet\\Interface Graphique\\InterfaceGraphique\\Assets\\Json Files\\converted_BD_images'
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
histograms_json_files_path = "C:\\Users\\salma\\OneDrive\\Documents\\URCA - M2\\INF00903\\Projet\\Interface Graphique\\InterfaceGraphique\\Assets\\Json Files\\histograms_BD_images"
descriptors_json_file_path = lambda color_space:histograms_json_files_path+"\\"+color_space