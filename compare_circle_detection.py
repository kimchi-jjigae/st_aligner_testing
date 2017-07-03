# -*- coding: utf-8 -*-
# Takes a 4k Cy3 image and given the TL and BR it runs spot detection and spot assignment and
# displays and compares the ones detected from keypoints, edges, and whiteness :)

from circle_detector import CircleDetector, DetectionType
from spots import Spots
from imageprocessor import ImageProcessor

from PIL import Image, ImageDraw

circle_detector = CircleDetector()
image_processor = ImageProcessor()
spots = Spots({'x':  430, 'y':  290}, # these need to be hardcoded
              {'x': 3260, 'y': 3320},
              {'x':   33, 'y':   35}, 1.0)

image = Image.open("resized_dark_image.jpg")
image.save("circles_1_orig.jpg")

BCT_image = image_processor.apply_BCT(image)
BC_image = image_processor.apply_BCT(image, False)

BCT_image.save("circles_2_BCT.jpg")
BC_image.save("circles_3_BC.jpg")

keypoints = image_processor.detect_keypoints(BCT_image)
spots_from_kp, spots_from_edges, spots_from_white = spots.create_spots_from_keypoints(keypoints, BCT_image, 1.0)
print(len(spots_from_kp))
print(len(spots_from_edges))
print(len(spots_from_white))
for adsf in spots_from_edges:
    print(adsf)

print("asdf")
for adsf in spots_from_white:
    print(adsf)

## rendering

spot_radius = 10
canvas = ImageDraw.Draw(BC_image)

for spot in spots_from_kp:
    render_spot = [
        spot['renderPosition']['x'] - spot_radius,
        spot['renderPosition']['y'] - spot_radius,
        spot['renderPosition']['x'] + spot_radius,
        spot['renderPosition']['y'] + spot_radius
    ]
    canvas.ellipse(render_spot, fill=(255, 0, 0), outline=None)

BC_image.save("circles_4_kp.jpg")

for spot in spots_from_edges:
    render_spot = [
        spot['renderPosition']['x'] - spot_radius,
        spot['renderPosition']['y'] - spot_radius,
        spot['renderPosition']['x'] + spot_radius,
        spot['renderPosition']['y'] + spot_radius
    ]
    canvas.ellipse(render_spot, fill=(0, 255, 0), outline=None)

BC_image.save("circles_5_edge.jpg")

for spot in spots_from_white:
    render_spot = [
        spot['renderPosition']['x'] - spot_radius,
        spot['renderPosition']['y'] - spot_radius,
        spot['renderPosition']['x'] + spot_radius,
        spot['renderPosition']['y'] + spot_radius
    ]
    canvas.ellipse(render_spot, fill=(0, 0, 255), outline=None)

BC_image.save("circles_6_white.jpg")
