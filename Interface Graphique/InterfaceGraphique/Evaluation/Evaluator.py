import pymongo
from itertools import product
import random
import numpy as np
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from InterfaceGraphique.Preprocessor.FileSplitter import FileSplitter
from InterfaceGraphique.Filters.DistanceFilter import DistanceFilter
from InterfaceGraphique.Describors.Normalizer import Normalizer
from InterfaceGraphique.Assets.config import color_spaces, descriptors_json_file_path, descriptors, distances, shape_filters, color_spaces_, hist_keys, gray_image_type, h_image_type, indexed_image_type, normalization

class Evaluator:
    def __init__(self):
        self.images_hist_dict = {}
        FileSplitter.recombine_texture_histograms(color_spaces, descriptors_json_file_path)
        self.distance_filter = DistanceFilter()
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client["image_retrieval"]
        self.combinations_collection = self.db["combinations"]
        self.collection = self.db["evaluation_results"]
        self.map_collection = self.db["map_results"]

    def generate_and_store_combinations(self):
        valid_combinations = []
        for combo in product(color_spaces_, descriptors["color"], descriptors["shape"], descriptors["texture"], descriptors["cnn"], normalization, distances):
            color_space, color_desc, shape_desc, texture_desc, cnn_desc, normalization_method, distance = combo
            
            if color_desc == "" and shape_desc == "" and texture_desc == "" and cnn_desc == "":
                continue

            if color_desc == "Hue Histogram" and color_space not in h_image_type:
                continue
            
            if ("Blob" in color_desc or "Blob" in shape_desc or "Blob" in texture_desc) and color_space not in gray_image_type + h_image_type + indexed_image_type:
                continue

            shape_filter = "" if shape_desc == "" else random.choice(shape_filters)
            
            valid_combinations.append((color_space, color_desc, shape_desc, shape_filter, texture_desc, cnn_desc, normalization_method, distance))

        random.shuffle(valid_combinations)
        
        bulk_operations = [
            pymongo.UpdateOne(
                {"_id": i},
                {"$set": {
                    "combination": combo,
                    "processed": False
                }},
                upsert=True
            ) for i, combo in enumerate(valid_combinations)
        ]
        
        self.combinations_collection.bulk_write(bulk_operations)
        print(f"Stored {len(valid_combinations)} combinations")

    def process_combinations(self, batch_size=100):
        while True:
            combinations_to_process = list(self.combinations_collection.find(
                {"processed": False}
            ).limit(batch_size))
            
            if not combinations_to_process:
                break
            
            for combo_doc in combinations_to_process:
                combo = combo_doc["combination"]
                print(f"Processing combination: {combo}")
                color_space, color_desc, shape_desc, shape_filter, texture_desc, cnn_desc, normalization_method, distance = combo
                
                self.images_hist_dict.clear()
                self.process_descriptors("color", color_space, color_desc, normalization_method)
                self.process_descriptors("shape", color_space, shape_desc, normalization_method, shape_filter)
                self.process_descriptors("texture", color_space, texture_desc, normalization_method)
                self.process_descriptors("cnn", "rgb", cnn_desc)

                for query_image in self.images_hist_dict.keys():
                    distances = self.calculate_distances(query_image, distance)
                    ranked_images = self.rank_images(distances)
                    
                    result = {
                        "image_path": query_image,
                        "combination": {
                            "color_space": color_space,
                            "color_desc": color_desc,
                            "shape_desc": shape_desc,
                            "shape_filter": shape_filter,
                            "texture_desc": texture_desc,
                            "cnn_desc": cnn_desc,
                            "normalization_method": normalization_method,
                            "distance": distance
                        },
                        "distances": {k: float(v) for k, v in distances.items()},
                        "ranked_images": ranked_images
                    }
                    
                    self.collection.insert_one(result)
                
                self.combinations_collection.update_one(
                    {"_id": combo_doc["_id"]},
                    {"$set": {"processed": True}}
                )

    def process_descriptors(self, descriptor_type, color_space, descriptor_entry, normalization_method=None, filter_name=None):
        if descriptor_type == "cnn":
            descriptor_file = descriptors_json_file_path("rgb") + f"\\{descriptor_type}_vectors.json"
        else:
            descriptor_file = descriptors_json_file_path(color_space) + f"\\{descriptor_type}_histograms.json"
        
        try:
            with open(descriptor_file, 'r', encoding='utf-8') as json_file:
                descriptors_dict = json.load(json_file)
                if descriptor_entry == "":
                    return
                hist_key = self.get_hist_key(descriptor_type, descriptor_entry)

                for image_name, image_hists in descriptors_dict.items():
                    # image_name = "BD_images" + image_name.split("BD_images")[-1]
                    if image_name not in self.images_hist_dict:
                        self.images_hist_dict[image_name] = {}
                    if descriptor_type == "shape" and filter_name:
                        hist = np.array(image_hists[hist_key][filter_name])
                    else:
                        hist = np.array(image_hists[hist_key])

                    if image_name not in self.images_hist_dict:
                        self.images_hist_dict[image_name] = {}
                    if descriptor_type == "shape" and filter_name:
                        hist = np.array(image_hists[hist_key][filter_name])
                    else:
                        hist = np.array(image_hists[hist_key])
                    
                    normalized_hist = self.normalize_histogram(hist, normalization_method)
                    self.images_hist_dict[image_name][descriptor_type] = normalized_hist

        except FileNotFoundError:
            print(f"Error: The file {descriptor_file} does not exist.")
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from {descriptor_file}.")

    def normalize_histogram(self, histogram, normalization_method=None):
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

    def calculate_distances(self, query_image, distance_type):
        distances = {}
        query_hist = np.concatenate([self.images_hist_dict[query_image][desc] for desc in self.images_hist_dict[query_image]])
        
        for image_name, hists in self.images_hist_dict.items():
            if image_name != query_image:
                image_hist = np.concatenate([hists[desc] for desc in hists])
                if distance_type == "intersection_histogramme_x":
                    distances[image_name] = getattr(self.distance_filter, "distance_intersection_histogrammes")(query_hist, image_hist)
                elif distance_type == "intersection_histogramme_y":
                    distances[image_name] = getattr(self.distance_filter, "distance_intersection_histogrammes")(image_hist, query_hist)
                else:
                    distances[image_name] = getattr(self.distance_filter, f"distance_{distance_type.lower()}")(query_hist, image_hist)

        return distances

    def rank_images(self, distances):
        return [k for k, v in sorted(distances.items(), key=lambda item: item[1])]

    def calculate_ap(self, retrieved_images, relevant_images, k=10):
        relevant_count = 0
        sum_precision = 0
        for i, image in enumerate(retrieved_images[:k], 1):
            if image in relevant_images:
                relevant_count += 1
                precision = relevant_count / i
                sum_precision += precision
        return sum_precision / len(relevant_images) if relevant_images else 0

    def calculate_map(self):
        combinations = self.collection.distinct("combination")
        for combo in combinations:
            if self.map_collection.find_one({"combination": combo}):
                continue  # Skip if MAP for this combination is already calculated
            
            results = self.collection.find({"combination": combo})
            ap_sum = 0
            count = 0
            for result in results:
                query_image = result["image_path"]
                retrieved_images = result["ranked_images"]
                query_class = query_image[5:7]
                relevant_images = [img for img in retrieved_images if img[5:7] == query_class]
                ap = self.calculate_ap(retrieved_images, relevant_images)
                ap_sum += ap
                count += 1
                
                self.collection.update_one(
                    {"_id": result["_id"]},
                    {"$set": {"average_precision": ap}}
                )

            map_value = ap_sum / count if count > 0 else 0
            
            self.map_collection.insert_one({
                "combination": combo,
                "map": map_value
            })

    def get_best_combination(self):
        best_combo = self.map_collection.find_one(sort=[("map", -1)])
        return best_combo["combination"], best_combo["map"]
    

if __name__ == "__main__":
    evaluator = Evaluator()
    if evaluator.combinations_collection.count_documents({}) == 0:
        evaluator.generate_and_store_combinations()
    # evaluator.process_combinations()
    evaluator.calculate_map()
    best_combo, best_map = evaluator.get_best_combination()
    print(f"Meilleure combinaison : {best_combo} avec MAP = {best_map}")