import sys
import os
import argparse

from PIL import Image

def convert_file(tex_path):
    tex_path = tex_path.strip()
    assert tex_path.endswith(".tex"), "Tex file name '{}' does not ends with '.tex'".format(tex_path)

    tex_dir = os.path.dirname(tex_path)
    aux_path = tex_path[:-4] + ".aux"
    dvi_path = tex_path[:-4] + ".dvi"
    log_path = tex_path[:-4] + ".log"
    png_path = tex_path[:-4] + ".png"

    os.system('latex "{}" -output-directory="{}"'.format(tex_path, tex_dir))
    os.system('dvipng "{}" -o "{}" -pp 1'.format(dvi_path, png_path))
    os.remove(aux_path)
    os.remove(log_path)
    os.remove(dvi_path)

    im = Image.open(png_path)
    im_width, im_height = im.size
    left_margin = 0
    top_margin = 0
    right_margin = 0
    bottom_margin = 0

    # left margin
    while True:
        if len(im.crop((0, 0, left_margin + 1, im_height)).getcolors()) == 1:
            left_margin += 1
        else:
            break

    # top margin
    while True:
        if len(im.crop((0, 0, im_width, top_margin + 1)).getcolors()) == 1:
            top_margin += 1
        else:
            break

    # right margin
    while True:
        if len(im.crop((im_width - 1 - right_margin, 0, im_width, im_height)).getcolors()) == 1:
            right_margin += 1
        else:
            break

    # bottom margin
    while True:
        if len(im.crop((0, im_height - 1 - bottom_margin, im_width, im_height)).getcolors()) == 1:
            bottom_margin += 1
        else:
            break

    region =  im.crop((left_margin, top_margin, im_width - right_margin, im_height - bottom_margin))
    region.save(png_path)


def main():
    parser = argparse.ArgumentParser(description = "Convert latex file to a png image")
    parser.add_argument("path", help = "path to a latex file or directory containing latex files")
    args = vars(parser.parse_args())

    ipath = args["path"]
    if os.path.isdir(ipath):
        tex_files = os.listdir(ipath)
        tex_files = [os.path.join(ipath, x) for x in tex_files if x.endswith(".tex")]
        for tex_file in tex_files:
            convert_file(tex_file)
    elif os.path.isfile(ipath):
        convert_file(ipath)
    else:
        print("Path '{}' is neither a directory nor a file".format(ipath))

if __name__ == '__main__':
    main()