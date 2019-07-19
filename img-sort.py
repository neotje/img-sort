import os
import re
import sys
import datetime
from exif import Image
from shutil import copyfile

arg_len = len(sys.argv)
imglist = []
operations = []

# check if enough arguments are given
if arg_len == 1 or arg_len == 2:
    print("too few arguments!")
    exit()

origin_dir = sys.argv[1]
target_dir = sys.argv[2]

print("origin: ", origin_dir)
print("target: ", target_dir)

# check if user want's a different target path
if arg_len == 4:
    target_path = sys.argv[3]
else:
    target_path = "/$year$/$month$/$day$"

# check if user want's a different file nameing sceme.
if arg_len == 5:
    filename = sys.argv[4]
else:
    filename = "{hour}-{minute}-{model}-{filename}"

# scan for image files
# r=root, d=directories, f = files
for r, d, f in os.walk(origin_dir):
    for file in f:
        if ".png" in os.path.join(r, file).lower() or ".jpg" in os.path.join(r, file).lower():
            imglist.append(os.path.join(r, file))

print("{} images found".format(len(imglist)))

needed_tags = []

for match in re.findall(r"\{(\w+)\}", filename):
    if not (match in ["year", "month", "day", "hour", "minute", "second", "filename"]) and not(match in needed_tags):
        needed_tags.append(match)

for img_path in imglist:
    print("{}% processed".format(str(round(len(operations) / len(imglist) * 100))), end="\r")

    with open(img_path, 'rb') as image_file:
        image = Image(image_file)

    new_path = ""
    new_folder = target_dir + "/"
    new_file = ""

    # collect image dates
    img_date = datetime.datetime.strptime(image["datetime"], '%Y:%m:%d %H:%M:%S')
    data = {
        "year": str(img_date.year),
        "month": str(img_date.month),
        "day": str(img_date.day),
        "hour": str(img_date.hour),
        "minute": str(img_date.minute),
        "second": str(img_date.second),
        "filename": os.path.basename(img_path)
    }

    for tag in needed_tags:
        data[tag] = image[tag].strip(' \t\n\r')

    # print(target_path.split("/"))

    for sub_folder in target_path.split("/"):
        if sub_folder == "":
            continue

        if sub_folder[0] == "$" and sub_folder[len(sub_folder)-1] == "$":
            tag = sub_folder.replace("$", "")
            # print(tag)

            if tag in ["year", "month", "day", "hour", "minute", "second"]:
                new_folder += data[tag]
            else:
                data[tag] = image[tag].strip(' \t\n\r')
                new_folder += data[tag]
                new_folder += "/"
        else:
            new_folder += sub_folder
            new_folder += "/"

    # print(new_folder)

    new_file = filename.format(**data)

    # print(new_file)
    path_list = [new_folder, new_file]
    new_path = os.path.join(*path_list)

    operations.append([img_path, new_path, os.path.join(target_dir, new_folder)])

print("{}% processed".format("100"), end="\r")
print("")

i = 1
for operation in operations:
    print("{}% copied".format(str(round(i / len(operations) * 100))), end="\r")
    # print("copying {} to {}".format(operation[0], operation[1]))

    if not os.path.exists(operation[2]):
        os.makedirs(operation[2])

    copyfile(operation[0], operation[1])

    i += 1

print("{}% copied".format("100"), end="\r")
print("")
print("done!")
