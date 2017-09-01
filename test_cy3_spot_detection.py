import os

from PIL import Image, ImageDraw

from circle_detector import CircleDetector, DetectionType
from imageprocessor import ImageProcessor
from spots import Spots

result_dirname = "results/"
result_filename = "results.csv"
image_dirname = "images_test/"
temp = os.listdir(image_dirname)
images = []
image_processor = ImageProcessor()

with open(result_dirname + result_filename, 'w') as f:
    f.write(",#detected,false+,false-\n")

for image in temp:
    filename_without_extension = image[:-4]
    images.append(filename_without_extension)

for image in images:
    spots = Spots({'x':  508, 'y':  204},
                  {'x': 3328, 'y': 3224},
                  {'x':   33, 'y':   35}, 1.0)
    clahe_filename = image + "_CLAHE.jpg"
    plot_filename = image + "_plot.jpg"

    img = Image.open(image_dirname + image + ".jpg")
    
    BC_image = image_processor.apply_BCT(img, False)
    BCT_image = image_processor.apply_BCT(img)

    BC_image.save(result_dirname + clahe_filename)

    keypoints = image_processor.detect_keypoints(BCT_image)
    spots_from_kp, spots_from_edges, spots_from_white = spots.create_spots_from_keypoints(keypoints, BCT_image, 1.0)
    print(image)
    print("kp1 %d " % len(keypoints))
    print("kp2 %d " % len(spots_from_kp)) 
    print("edge %d " % len(spots_from_edges)) 
    print("white %d " % len(spots_from_white))
    total_spot_amount = len(spots_from_kp) + len(spots_from_edges) + len(spots_from_white)
    print("total %d" % total_spot_amount)

    spot_radius = 10
    canvas = ImageDraw.Draw(BC_image)

    for spot in spots_from_kp:
        #print("%d, %d" % (spot['arrayPosition']['x'], spot['arrayPosition']['y']))
        render_spot = [
            spot['renderPosition']['x'] - spot_radius,
            spot['renderPosition']['y'] - spot_radius,
            spot['renderPosition']['x'] + spot_radius,
            spot['renderPosition']['y'] + spot_radius
        ]
        canvas.ellipse(render_spot, fill=(255, 0, 0), outline=None)

    for spot in spots_from_edges:
        render_spot = [
            spot['renderPosition']['x'] - spot_radius,
            spot['renderPosition']['y'] - spot_radius,
            spot['renderPosition']['x'] + spot_radius,
            spot['renderPosition']['y'] + spot_radius
        ]
        canvas.ellipse(render_spot, fill=(0, 255, 0), outline=None)

    for spot in spots_from_white:
        render_spot = [
            spot['renderPosition']['x'] - spot_radius,
            spot['renderPosition']['y'] - spot_radius,
            spot['renderPosition']['x'] + spot_radius,
            spot['renderPosition']['y'] + spot_radius
        ]
        canvas.ellipse(render_spot, fill=(0, 0, 255), outline=None)

    BC_image.save(result_dirname + plot_filename)

    with open(result_dirname + result_filename, 'a') as f:
        f.write("%s,%s,,\n" % (image, total_spot_amount))
