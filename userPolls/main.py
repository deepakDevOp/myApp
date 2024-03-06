from PIL import Image
import io

# Path to the downloaded image file
image_path = "C:/Users/GOKU/Pictures/image.jpg"  # Replace with the path to your downloaded image

# Open the image file
with open(image_path, "rb") as file:
    # Read the binary data from the image file
    binary_data = file.read()

# Convert binary data back to an image
image = Image.open(io.BytesIO(binary_data))

# Save the image again (optional)
image.save("C:/Users/GOKU/Pictures/downloaded_image_copy.jpg")

print("Image conversion and saving completed successfully")
