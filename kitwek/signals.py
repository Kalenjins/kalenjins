from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO




def compress_image(image, max_width=800, max_height=800, max_size_kb=500, quality=85):
    """
    Resize and compress an image until it is below a certain file size.

    :param image: The image to be resized and compressed
    :param max_width: Maximum allowed width of the image
    :param max_height: Maximum allowed height of the image
    :param max_size_kb: Maximum allowed size of the image in KB
    :param quality: Quality of the image to start with (used for JPEG compression)
    :return: Compressed and resized image
    """
    img = Image.open(image)
    img_format = img.format

    # Resize the image to fit within max_width and max_height while maintaining aspect ratio
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    # Save the image into a BytesIO object first
    img_io = BytesIO()
    img.save(img_io, format=img_format, quality=quality)
    img_io.seek(0)

    # If the image size exceeds max_size_kb, reduce the quality and save again
    while img_io.getbuffer().nbytes > max_size_kb * 1024:  # max_size_kb in bytes
        # Reduce the quality by 5 and check again
        quality -= 5
        if quality < 10:  # Don't reduce the quality below a certain threshold (e.g., 10)
            raise ValidationError("Image size exceeds 500 KB even after compression.")
        
        # Clear BytesIO and save again with reduced quality
        img_io = BytesIO()
        img.save(img_io, format=img_format, quality=quality)
        img_io.seek(0)

    # Create a new InMemoryUploadedFile for the compressed image to be saved
    temp_file = InMemoryUploadedFile(
        img_io, 
        field_name='image', 
        name=image.name, 
        content_type=f'image/{img_format.lower()}',
        size=img_io.getbuffer().nbytes, 
        charset=None
    )

    return temp_file
