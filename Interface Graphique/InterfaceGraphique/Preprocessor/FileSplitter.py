import os
import json
import glob
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from InterfaceGraphique.Assets.config import descriptors_json_file_path, color_spaces

class FileSplitter:
    def __init__(self, input_file, output_prefix="part_", chunk_size=100*1024*1024):
        """
        Initialize the splitter
        :param input_file: Path to the file to split
        :param output_prefix: Prefix for output chunks
        :param chunk_size: Maximum size per chunk in bytes (default: 100MB)
        """
        self.input_file = input_file
        self.output_prefix = output_prefix
        self.chunk_size = chunk_size
        self.chunk_files = []

    def split(self):
        """Split the input file into chunks"""
        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_prefix)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        part_num = 0
        with open(self.input_file, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                
                # Handle JSON structure if splitting JSON file
                if self.input_file.endswith('.json'):
                    chunk = self._handle_json_boundaries(f, chunk)

                chunk_file = f"{self.output_prefix}{part_num:04d}.json"
                with open(chunk_file, 'wb') as chunk_f:
                    chunk_f.write(chunk)
                
                self.chunk_files.append(chunk_file)
                part_num += 1

        return self.chunk_files

    def _handle_json_boundaries(self, file_obj, chunk):
        """Handle JSON structure when splitting files"""
        # Check if we're in the middle of a JSON structure
        try:
            json.loads(chunk + b']')  # Try closing array
            return chunk
        except json.JSONDecodeError:
            # Find the last valid closing brace/bracket
            pos = chunk.rfind(b'}')
            if pos == -1:
                pos = chunk.rfind(b']')
            
            if pos != -1:
                # Seek back to the valid split point
                file_obj.seek(pos - len(chunk) + 1, os.SEEK_CUR)
                return chunk[:pos+1]
            
        return chunk  # Return as-is if no valid split point found

    @staticmethod
    def recombine(input_pattern, output_file):
        """
        Recombine chunk files into original file
        :param input_pattern: Glob pattern to match chunk files (e.g. "part_*.json")
        :param output_file: Path to output file
        """
        # Get sorted list of chunk files
        chunk_files = sorted(glob.glob(input_pattern))
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file, 'wb') as outfile:
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as infile:
                    outfile.write(infile.read())

        # Verify JSON integrity if JSON file
        if output_file.endswith('.json'):
            with open(output_file, 'r') as f:
                try:
                    json.load(f)
                except json.JSONDecodeError:
                    raise ValueError("Recombined JSON file is corrupted!")

        return output_file

    @staticmethod
    def recombine_texture_histograms(color_spaces, descriptors_json_file_path):
        """Recombine texture histograms chunks for all color spaces if not already recombined"""
        for color_space in color_spaces.values():
            texture_descriptor_json_file_path = descriptors_json_file_path(color_space)
            texture_histograms_file = os.path.join(texture_descriptor_json_file_path, "texture_histograms.json")
            
            # Check if the texture histograms file exists
            if not os.path.exists(texture_histograms_file):
                # Recombine the chunks
                recombined_file = FileSplitter.recombine(
                    input_pattern=os.path.join(texture_descriptor_json_file_path, "texture_histograms_chunks", "texture_histograms_part_*.json"),
                    output_file=texture_histograms_file
                )
                print(f"Recombined file: {recombined_file}")
    

# if __name__ == "__main__":
    # Split the file
    # for color_space in color_spaces.values():
    #     texture_descriptor_json_file_path = descriptors_json_file_path(color_space)
    #     splitter = FileSplitter(
    #         input_file=texture_descriptor_json_file_path+"\\texture_histograms.json",
    #         output_prefix=texture_descriptor_json_file_path+"\\texture_histograms_chunks\\texture_histograms_part_",
    #         chunk_size=100*1024*1024  # 100MB
    #     )
    #     chunks = splitter.split()
    #     print(f"Created chunks for {color_space}: {chunks}")