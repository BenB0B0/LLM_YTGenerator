from PIL import Image

def resize_and_mirror(image_path, target_width, target_height):
    # Open the original image
    original_image = Image.open(image_path)

    # Get the original image dimensions
    original_width, original_height = original_image.size

    # Calculate the scaling factors for width and height
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height

    # Choose the scaling factor that results in the larger image
    scale_factor = max(width_ratio, height_ratio)

    # Calculate the new dimensions after scaling
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    # Create a new image with the target dimensions
    new_image = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # Calculate the position to paste the original image
    paste_position = ((target_width - new_width) // 2, (target_height - new_height) // 2)

    # Paste the resized original image onto the new image
    new_image.paste(original_image.resize((new_width, new_height), Image.LANCZOS), paste_position)

    # Create a mirrored reflection of the original image
    mirrored_image = original_image.transpose(Image.FLIP_LEFT_RIGHT)

    # Calculate the position to paste the mirrored image
    mirrored_paste_position = ((target_width - new_width) // 2, paste_position[1] + new_height)

    # Paste the mirrored image onto the new image
    new_image.paste(mirrored_image.resize((new_width, new_height), Image.LANCZOS), mirrored_paste_position)

    # Save the result
    new_image.save(image_path)


