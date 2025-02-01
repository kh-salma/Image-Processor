
import os
import json
def modify_json_keys(directory):
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):  # Process only JSON files
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                
                try:
                    # Load the JSON file
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # Modify the dictionary keys
                    modified_data = {}
                    for key, value in data.items():
                        # Find the part of the key after "image0"
                        new_key = key.split("\\image")[-1]
                        # Add "image0" back to the new key
                        new_key = "image" + new_key
                        modified_data[new_key] = value
                    
                    # Save the modified data back to the JSON file
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(modified_data, f, indent=4)
                    
                    print(f"Modified keys in file: {file_path}")
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

# Example usage
directory = "C:\\Users\\salma\\OneDrive\\Documents\\URCA - M2\\INF00903\\Projet\\Interface Graphique\\InterfaceGraphique\\Assets\\Json Files\\histograms_BD_images\\yuv"
modify_json_keys(directory)