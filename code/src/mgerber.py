from gerber import load_layer
from gerber.render import RenderSettings
from gerber.render.cairo_backend import GerberCairoContext
from glob import glob
from utils import delete_folder, create_dir
import os
from collections import namedtuple

#GERBER_FOLDER = "./assets/original/gerbers/wire_layers/*"
#MODULE = "default"
#GERBER_FOLDER = f"./assets/original/gerbers/{MODULE}/*"
#OUTPUT = f"./assets/output/gerber/{MODULE}"
#gerber_folders = glob(GERBER_FOLDER)

# Manual manipulations: Start with 3 -> later 10
# See notes

# Config
is_rnd_solder_layer = False
clean_before_run = True
rnd = namedtuple('Colors', ['transparent', 'white', 'black', 'red', 'green'])
Colors = rnd(transparent=RenderSettings((0, 0, 0), alpha=0),
             white=RenderSettings((1, 1, 1)),
             black=RenderSettings((0, 0, 0)),
             red=RenderSettings((1, 0, 0), alpha=0.5),
             green=RenderSettings((0, 1, 0), alpha=0.5))


def get_file_info(path: str) -> (str, str):
    info = os.path.basename(path).split(".")
    return (info[0], info[1])


def get_folder_name(path: str) -> (str, str):
    return os.path.basename(path)


def color_for_layer(idx: int, layers: int):
    c = (1.0 / layers) * idx
    return RenderSettings((c, c, c), alpha=0.5 if idx > 1 else 1)


def color_for_layer2(idx: int, layers: int):
    c = (1.0 / layers) * idx
    return RenderSettings((c, c, c), alpha=1)


def check_dir(module: str):
    OUTPUT = f"./assets/output/gerber/{module}"
    if clean_before_run:
        delete_folder("{OUTPUT}/*")
    GERBER_FOLDER = f"./assets/original/gerbers/{module}/*"
    create_dir(OUTPUT)
    gerber_folders = glob(GERBER_FOLDER)
    print(f"Gerber files found in {GERBER_FOLDER}: ", gerber_folders.__len__())
    return gerber_folders


def layers_only():
    module = "default3"
    gerber_folders = check_dir(module)

    for gerber_folder in gerber_folders:
        ctx = GerberCairoContext(scale=50)
        folder_name = get_folder_name(gerber_folder)
        top_copper = glob(f"{gerber_folder}/copper_top.gbr").pop()
        bottom_copper = glob(f"{gerber_folder}/copper_bottom.gbr").pop()
        out_path_fl = f"./assets/output/gerber/{module}"
        create_dir(out_path_fl)

        bottom_copper_layer = load_layer(bottom_copper)
        top_copper_layer = load_layer(top_copper)

        ctx.render_layer(bottom_copper_layer,
                         bgsettings=Colors.transparent,
                         settings=color_for_layer2(1, 2))
        ctx.render_layer(top_copper_layer,
                         bgsettings=Colors.transparent,
                         settings=color_for_layer2(2, 2))

        top_file_path = f"{out_path_fl}/{folder_name}.png"
        ctx.dump(top_file_path)
        ctx.clear()


def single_gerbers():
    MODULE = "default2"
    GERBER_FOLDER = f"./assets/original/gerbers/{MODULE}/*"
    OUTPUT = f"./assets/output/gerber/{MODULE}"
    create_dir(OUTPUT)
    gerber_folders = glob(GERBER_FOLDER)
    for idx, gerber_folder in enumerate(gerber_folders):
        ctx = GerberCairoContext(1000)
        folder_name = get_folder_name(gerber_folder)
        print(f"{(idx / gerber_folders.__len__()):.0%}")

        top_copper = glob(f"{gerber_folder}/*.GTL").pop()
        bottom_copper = glob(f"{gerber_folder}/*.GBL").pop()
        #top_copper = glob(f"{gerber_folder}/copper_top.gbr").pop()
        #bottom_copper = glob(f"{gerber_folder}/copper_bottom.gbr").pop()

        top = load_layer(top_copper)
        bottom = load_layer(bottom_copper)

        ctx.render_layer(top,
                         bgsettings=Colors.black,
                         settings=color_for_layer(1, 2))
        #ctx.render_layer(bottom, bgsettings=Colors.transparent, settings=color_for_layer(1, 2))
        ctx.render_layer(bottom,
                         bgsettings=Colors.transparent,
                         settings=color_for_layer(2, 2))
        #ctx.render_layer(bottom, bgsettings=Colors.transparent, settings=Colors.green)

        file_path = f"{OUTPUT}/{folder_name}.png"
        ctx.dump(file_path)
        ctx.clear()


# Gerbers for line width structure
def gen_mpls_line_only():
    MODULE = "wire_only_mpls"
    GERBER_FOLDER = f"./assets/original/gerbers/{MODULE}/*"
    OUTPUT = f"./assets/output/gerber/{MODULE}"
    create_dir(OUTPUT)
    gerber_folders = glob(GERBER_FOLDER)

    for gerber_folder2 in gerber_folders:
        folder_name = get_folder_name(gerber_folder2)
        print("####################################")
        print("Folder:", folder_name)
        print("####################################")
        for gerber_folder in glob(f"{gerber_folder2}/*"):
            ctx = GerberCairoContext(100)
            mod_type = get_folder_name(gerber_folder)

            top_copper = glob(f"{gerber_folder}/copper_top.gbr").pop()
            bottom_copper = glob(f"{gerber_folder}/copper_bottom.gbr").pop()

            top = load_layer(top_copper)
            bottom = load_layer(bottom_copper)

            ctx.render_layer(bottom,
                             bgsettings=Colors.transparent,
                             settings=color_for_layer2(1, 2))
            ctx.render_layer(top,
                             bgsettings=Colors.transparent,
                             settings=color_for_layer2(2, 2))

            out_path = f"{OUTPUT}/{folder_name}"
            create_dir(out_path)
            file_path = f"{out_path}/{mod_type}-{folder_name}.png"
            ctx.dump(file_path)
            ctx.clear()


#gen_mpls_line_only()
#single_gerbers()
#layers_only()
