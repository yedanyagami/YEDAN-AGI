"""
Design Extractor
Extracts dominant colors from the brand image to generate a consistent color palette.
"""
from PIL import Image
import collections
import sys

def get_dominant_colors(image_path, num_colors=5):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((150, 150)) # Resize for speed
        pixels = list(img.getdata())
        
        # Simple frequency count
        counter = collections.Counter(pixels)
        most_common = counter.most_common(num_colors)
        
        hex_colors = []
        for count in most_common:
            rgb = count[0]
            hex_code = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
            hex_colors.append(hex_code)
            
        return hex_colors
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    img_path = r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/uploaded_image_1767438896099.jpg"
    print(f"Analyzing {img_path}...")
    colors = get_dominant_colors(img_path)
    
    print("\n[Brand Palette Detected]")
    for i, c in enumerate(colors):
        print(f"Color {i+1}: {c}")
        
    # Generate a theme config snippet
    if len(colors) >= 3:
        print("\n[Recommended Theme Settings]")
        print(f"Primary (Button): {colors[0]}")
        print(f"Secondary (Links): {colors[1]}")
        print(f"Background (Warm): {colors[2]}")
