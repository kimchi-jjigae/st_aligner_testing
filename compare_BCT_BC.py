# -*- coding: utf-8 -*-
# Takes a 4k Cy3 image and applies BCT and BC only
# compares the amount of KP found through both

from imageprocessor import ImageProcessor
from PIL import Image

image_processor = ImageProcessor()

dark_image = Image.open("dark_image.jpg")
#dark_image = Image.open("fake_dark_image.jpg")

pixel_length = 55

(dark_image, sf) = image_processor.resize_image(dark_image, [4000, 4000])

unadjusted_image = image_processor.apply_BCT(dark_image, False)
adjusted_image = image_processor.apply_BCT(dark_image, True)

unadjusted_image.save("not_thresholded15.jpg")
adjusted_image.save("thresholded.jpg")

unadjusted_kp = image_processor.detect_keypoints(unadjusted_image)
adjusted_kp = image_processor.detect_keypoints(adjusted_image)

print("Unadjusted:")
print(len(unadjusted_kp))
print("Adjusted:")
print(len(adjusted_kp))
