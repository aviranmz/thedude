
def build_image_gallery(images, captions):
    # Combine image URL with caption in tuple format
    return [
        {"photo": img, "caption": cap}
        for img, cap in zip(images, captions)
    ]
