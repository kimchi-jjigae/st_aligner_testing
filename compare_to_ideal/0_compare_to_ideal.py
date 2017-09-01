#!/usr/bin/python
# takes in three files:
#   the "ideal" spots file
#   the output spots file for testing
#   the corresponding Cy3 image
# compares how many are correct are not, their accuracy etc.
# plots it to an image, scales it down to 4k x 4k

import sys
import numpy
import warnings
from PIL import Image, ImageDraw

warnings.simplefilter('ignore', Image.DecompressionBombWarning)

if(len(sys.argv) != 4):
    print("ERROR! Usage: python thisscript.py ideal_spots.tsv output_spots.tsv image.jpg")
    sys.exit()

ideal_filename = sys.argv[1]
test_filename = sys.argv[2]
image_filename = sys.argv[3]

ideal_spots_str = ideal_filename.split(".")[0]
test_spots_str = test_filename.split(".")[0]

output_file = ideal_spots_str + "_vs_" + test_spots_str + ".txt"
output_image_filename = ideal_spots_str + "_vs_" + test_spots_str + ".jpg"
print("Comparing %s with %s using image %s" % (ideal_spots_str, test_spots_str, image_filename))

def get_spots_from_file(filename):
    spots = []
    with open(filename) as f:
        for spot_line in f:
            spot_line = spot_line.replace("\n", "").split("\t")
            if(spot_line[0] == "x"):
                continue
            old_coord = (int(spot_line[0]), int(spot_line[1]))
            new_coord = (float(spot_line[2]), float(spot_line[3]))
            pixel_coord = (float(spot_line[4]), float(spot_line[5]))
            spot = {
                'old_coord': old_coord,
                'new_coord': new_coord,
                'pixel_coord': pixel_coord,
                'comparison': None
            }
            spots.append(spot)

    return spots

def distance_between_spots(spot1, spot2):
    # take two float tuples with x, y spot positions,
    # do the standard pythagoras shit
    a = spot1[0] - spot2[0]
    b = spot1[1] - spot2[1]
    return numpy.hypot(a, b)

ideal_spots = get_spots_from_file(ideal_filename)
test_spots = get_spots_from_file(test_filename)

correct_spots = []
missing_spots = []
extra_spots = []

pixel_distances = []

for ideal_spot in ideal_spots:
    spot_found = False
    for test_spot in test_spots:
        if(ideal_spot['old_coord'] == test_spot['old_coord']):
            spot_found = True
            test_spot['comparison'] = "same"
            correct_spots.append(test_spot)
            difference = distance_between_spots(
                ideal_spot['pixel_coord'],
                test_spot['pixel_coord'])
            pixel_distances.append(difference)

    if(spot_found == False):
        ideal_spot['comparison'] = "missing"
        missing_spots.append(ideal_spot)

for test_spot in test_spots:
    if(test_spot['comparison'] == None):
        test_spot['comparison'] = 'extra'
        extra_spots.append(test_spot)

pixel_accuracy_string = "less than the threshold, so it is okay."
pixel_accuracy = numpy.mean(pixel_distances)
if(pixel_accuracy > 50.0):
    pixel_accuracy_string = "more than the threshold, something's wrong."

a = "Of the %d spots in the Cy3 image, %d were correctly detected." % (len(ideal_spots), len(correct_spots))
b1 = "%d were missing:" % len(missing_spots)
#print(missing_spots)
c1 = "%d were extra spots: " % len(extra_spots)
#print(extra_spots)
d = "Pixel accuracy is %f pixels which is %s" % (pixel_accuracy, pixel_accuracy_string)

with open(output_file, 'w') as f:
    f.write(a + "\n")
    f.write(b1 + "\n")
    f.write(c1 + "\n")
    f.write(d + "\n")

print(a)
print(b1)
print(c1)
print(d)
print("Outputs saved as %s and %s" % (output_file, output_image_filename))

# TODO: do automatic downscaling

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ RENDERING NOW

columns = [[] for i in range(32)]
rows = [[] for i in range(34)]

for spot in ideal_spots:
    column = spot['old_coord'][0] - 1
    row = spot['old_coord'][1] - 1
    column_pos = spot['pixel_coord'][0]
    row_pos = spot['pixel_coord'][1]
    columns[column].append(column_pos)
    rows[row].append(row_pos)

columns = [numpy.mean(positions) for positions in columns]
rows = [numpy.mean(positions) for positions in rows]

column_diff = columns[2] - columns[1]
row_diff = rows[2] - rows[1]
columns[0] = columns[1] - column_diff
rows[0] = rows[1] - row_diff

Cy3_image = Image.open(image_filename)
Cy3_canvas = ImageDraw.Draw(Cy3_image)

def draw_spots_on_canvas(canvas, spots, colour):
    spot_radius = 150
    for spot in spots:
        render_spot = [
            spot['pixel_coord'][0] - spot_radius,
            spot['pixel_coord'][1] - spot_radius,
            spot['pixel_coord'][0] + spot_radius,
            spot['pixel_coord'][1] + spot_radius
        ]
        canvas.ellipse(render_spot, fill=colour, outline=None)

correct_colour = ( 20, 255,  20) #green
missing_colour = ( 20,  20, 255) #bluish
extra_colour   = (255,  20,  20) #red

draw_spots_on_canvas(Cy3_canvas, correct_spots, colour=correct_colour)
draw_spots_on_canvas(Cy3_canvas, extra_spots,   colour=extra_colour)
draw_spots_on_canvas(Cy3_canvas, missing_spots, colour=missing_colour)

for i, x in enumerate(columns):
    if(i == 0):
        continue
    y = rows[0]
    spot_radius = 80
    if(i % 10 == 9 or i % 5 == 4):
        spot_radius = 190

    render_spot = [
        x - spot_radius,
        y - spot_radius,
        x + spot_radius,
        y + spot_radius,
    ]
    if(i % 10 == 9):
        Cy3_canvas.rectangle(render_spot, fill=(255, 0, 0), outline=None)
    else:
        Cy3_canvas.ellipse(render_spot, fill=(255, 0, 0), outline=None)

for i, y in enumerate(rows):
    if(i == 0):
        continue
    x = columns[0]
    spot_radius = 80
    if(i % 10 == 9 or i % 5 == 4):
        spot_radius = 190

    render_spot = [
        x - spot_radius,
        y - spot_radius,
        x + spot_radius,
        y + spot_radius,
    ]
    if(i % 10 == 9):
        Cy3_canvas.rectangle(render_spot, fill=(255, 0, 0), outline=None)
    else:
        Cy3_canvas.ellipse(render_spot, fill=(255, 0, 0), outline=None)

Cy3_image.thumbnail((4000, 4000), Image.ANTIALIAS)
Cy3_image.save(output_image_filename)
