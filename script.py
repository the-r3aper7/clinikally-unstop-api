import json
import random

# List of image URLs
image_urls = [
    "https://s.cdnsbn.com/images/products/l/21233566801.jpg",
    "https://s.cdnsbn.com/images/products/l/21235166801.jpg",
    "https://s.cdnsbn.com/images/products/l/13989180431-1.jpg",
    "https://s.cdnsbn.com/images/products/l/33146881101.jpg",
    "https://s.cdnsbn.com/images/products/l/24146821601.jpg",
    "https://s.cdnsbn.com/images/products/l/33535402744.jpg",
    "https://s.cdnsbn.com/images/products/l/18489000444.jpg"
]

def add_product_images(input_file, output_file):
    try:
        # Read the JSON file
        with open(input_file, 'r') as file:
            data = json.load(file)
        
        # Add random image URL to each product
        for product in data['products']:
            product['product_image'] = random.choice(image_urls)
        
        # Write the updated data back to a new JSON file
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=2)
        
        print(f"Successfully added product images and saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {input_file} contains invalid JSON.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    input_file = "data.json"  # Replace with your input file name
    output_file = "data_with_images.json"  # Replace with desired output file name
    add_product_images(input_file, output_file)