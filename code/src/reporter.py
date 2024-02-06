import pandas as pd
from glob import glob
from mconfig import config
import utils
import plotter

# Export tex files
export_tex = False
export_plots = True
is_verbose = True

# Table captions
crop_caption = "Impact of cropping on the perceptual hash over increasing hash length."
fpos_single_caption = "False positives in the single dataset."
fpos_versions_caption = "False positives in the versions dataset."
ave_single_caption = f"The table shows the validity of the average phash against manipulations of color, tile-rotations and resolution changes. hff: {config.get('high_freq_factor')}, mode: {config.get('phash_resize_mode')}"
ave_versions_caption = "Versions phash verification based on multiple images with minor variations."
mpls_conduct_layout_caption = "Shows matching between the original and modified routing layout without functionality change."
mpls_elements_caption = "Modification by removal of small elements."
mpls_conduct_width_caption = "Comparing the effect of wire thickness changes to the phash."


def get_caption(key: str) -> str:
    if key == "fpos_single_caption":
        return fpos_single_caption
    elif key == "fpos_versions_caption":
        return fpos_versions_caption
    elif key == "ave_single_caption":
        return ave_single_caption
    elif key == "ave_versions_caption":
        return ave_versions_caption
    elif key == "mpls_conduct_layout_caption":
        return mpls_conduct_layout_caption
    elif key == "mpls_elements_caption":
        return mpls_elements_caption
    elif key == "mpls_conduct_width_caption":
        return mpls_conduct_width_caption
    elif key == "ave_wires_only_caption":
        return "Wires only gerber image set"
    elif key == "fpos_wires_only_caption":
        return "False positives in the wires only image set"
    print(f"######################## key not found: {key}")
    return "n/a"


def get_modifier_name(key: str):
    if key == "color_darker":
        return "Darker"
    elif key == "color_lighter":
        return "Brighter"
    elif key == "rotate_180_1":
        return "Flipped"
    elif key == f"rotate_90_{config['mpl_tile_sizes'][0]}":
        return "Tile 90°"
    elif key == f"resolution_{config['resolution_scale_width'][0]}":
        return "Smaller"
    elif key == f"resolution_{config['resolution_scale_width'][1]}":
        return "Bigger"
    elif key == "resolution_original":
        return "Original"
    else:
        return key


def hash_size_from_file(file) -> int:
    return int(file.split("-")[1])


def _config(key: str):
    return config[key]


def create_latex_table(df: pd.DataFrame,
                       column_format: str,
                       label: str,
                       caption: str,
                       mid_rows=None,
                       mid_offset=None,
                       sort=["pHash"]):
    if sort:
        df = df.sort_values(by=sort)  # Sort by first and second column
    tex = df.to_latex(escape=True,
                      index=False,
                      caption=caption,
                      column_format=column_format,
                      label=label)
    if mid_rows != None and mid_offset != None:
        tex = utils.add_tex_mid_rules(tex, mid_rows, mid_offset)

    if is_verbose:
        print(f"Table {label}")
        print(tex)
    return tex


def create_crop_report():
    """
    Crop cuts out the images by the crop sizes e.g.: [0.9, 0.95, 0.99] and 
    compares it to the hash of the 100% image (res-na)
    It is not comparing it to other resolutions due less of impact.
    """
    reports = []
    files = glob(f"{config.get('reports_output')}/hash-*-cropped-output.xlsx")
    ave_threshold_value = config['ave_threshold']

    for file in files:
        print("Crop-file:", file)
        crop_sheet = pd.read_excel(file)
        hash_size = hash_size_from_file(file)

        for crop_size in _config("crop_sizes"):
            # print(crop_sheet)
            df = crop_sheet[crop_sheet["value"] == crop_size * 100]

            if df.__len__() == 0:
                raise Exception(f"Empty df for crop_size: {crop_size * 100}")
            data = get_table_data(df, "valid")

            reports.append([hash_size, f"{(crop_size):.3}"] + data)
    df = pd.DataFrame(reports,
                      columns=[
                          'pHash', 'Crop', 'Hamming', 'Normalized', 'AD',
                          f'Valid ({ave_threshold_value})'
                      ])
    tex = create_latex_table(df,
                             column_format="cccccc",
                             label="table:crop",
                             caption=crop_caption,
                             mid_rows=[4, 4 * 2, 4 * 3],
                             mid_offset=6)
    if export_tex:
        utils.text_to_file(tex, "../paper/res/tex/tables/crop.table.tex")


def get_table_data(df: pd.DataFrame, valid_label: str):
    ham = utils.sum_column_average(df, "ham")
    norm = utils.sum_column_average(df, "norm")
    mAd = int(utils.median_absolute_deviation(df.__getitem__("ham")))
    valid = utils.count_valid_rows(df, valid_label)
    #to_percent
    print(utils.float_to_str(round(ham, 2)), f"{(norm):.2%}", " == ",
          utils.to_percent(norm))
    return [
        utils.float_to_str(round(ham, 2)), f"{(norm):.2%}",
        utils.float_to_str(round(mAd, 3)), f"{valid:.0%}"
    ]


def create_ave_report(file_path: str, label: str):
    """
    Create single report
    """
    reports = []
    files = glob(file_path)
    is_single = label == "single" or label == "wires_only"

    if files.__len__() == 0:
        print("Error: No files found in path - ", file_path)
        return

    for file in files:
        df = pd.read_excel(file)
        hash_size = hash_size_from_file(file)

        # Manipulation - Resolutions
        resolutions = _config("resolution_scale_width")
        res_df = df[df["mod"] == "res"]

        # Wanted order: ["Original", "Smaller", "Bigger", "Darker", "Brighter", "Tile 90°", "Flipped"]
        # Check with original image
        na_data = get_table_data(res_df[res_df["value"] == "na"], "valid")

        reports.append(
            [hash_size, get_modifier_name("resolution_original")] + na_data)

        for idx, res in enumerate(resolutions):
            res_data = get_table_data(res_df[res_df["value"] == str(res)],
                                      "valid")
            reports.append([
                hash_size,
                get_modifier_name(f"resolution_{utils.float_to_str(res)}")
            ] + res_data)

        # Manipulations - Color / Brightness
        if is_single:
            mpl_df = df[df["mod"] == "mpl"]

            for modifier in ["color_darker", "color_lighter"]:
                res_data = get_table_data(mpl_df[mpl_df["value"] == modifier],
                                          "valid")
                reports.append(
                    [hash_size, get_modifier_name(modifier)] + res_data)

            # Manipulation - Rotated tiles
            t_size = _config("mpl_tile_sizes")
            t_angel = _config("mpl_tile_angle")
            for idx, mpl_tile_size in enumerate(t_size):
                query = f"rotate_{t_angel[idx]}_{mpl_tile_size}"
                rotation_data = get_table_data(
                    mpl_df[mpl_df["value"] == query], "valid")
                reports.append([hash_size, get_modifier_name(query)] +
                               rotation_data)

    gs = 8 if is_single else 4
    columns = [
        'pHash', 'Manipulation', 'Hamming', 'Normalized', 'AD',
        f"Valid ({config['ave_threshold' if is_single else 'ave_threshold_versions']})"
    ]

    if export_plots and is_single:
        plotter.plot_single_df(reports, columns)

    df = pd.DataFrame(reports, columns=columns)
    tex = create_latex_table(df,
                             column_format="cccccc",
                             label=f"table:{label}",
                             sort=["pHash", "Manipulation"],
                             caption=get_caption(f"ave_{label}_caption"),
                             mid_rows=[gs, gs * 2, gs * 3],
                             mid_offset=6)
    if export_tex:
        utils.text_to_file(tex,
                           f"../paper/res/tex/tables/ave-{label}.table.tex")


def create_fpos_report(file_path: str, label: str):
    """
    Compares fpos in the single datasets
    """
    reports = []
    fpos_files = glob(file_path)
    # ave_threshold = config['ave_threshold']

    for file in fpos_files:
        df = pd.read_excel(file)
        hash_size = hash_size_from_file(file)
        fpos_data = get_table_data(df, "valid")
        reports.append([hash_size] + fpos_data)
    df = pd.DataFrame(reports,
                      columns=[
                          'pHash', 'Hamming', 'Normalized', 'AD',
                          f"Invalid ({config['ave_threshold']})"
                      ])
    tex = create_latex_table(df,
                             column_format="ccccc",
                             label=f"table:fpos-{label}",
                             caption=get_caption(f"fpos_{label}_caption"))
    if export_tex:
        utils.text_to_file(tex,
                           f"../paper/res/tex/tables/fpos-{label}.table.tex")


def create_mpls_report(file_path: str, label: str):
    reports = []
    sheets = glob(file_path)

    for sheet in sheets:
        df = pd.read_excel(sheet)
        hash_size = hash_size_from_file(sheet)
        data = get_table_data(df, "valid")
        reports.append([hash_size] + data)

    df = pd.DataFrame(reports,
                      columns=[
                          'pHash', 'Hamming', 'Normalized', 'AD',
                          f"Valid ({config['ave_threshold']})"
                      ])
    tex = create_latex_table(df,
                             column_format="ccccc",
                             label=f"table:mpls-{label}",
                             caption=get_caption(f"mpls_{label}_caption"))
    if export_tex:
        utils.text_to_file(tex,
                           f"../paper/res/tex/tables/mpls-{label}.table.tex")


def create_mpls_report_wires(file_path: str, label: str):
    reports = []
    sheets = glob(file_path)
    for sheet in sheets:
        df = pd.read_excel(sheet)
        hash_size = hash_size_from_file(sheet)
        for mod_label in [2, 6, 10, 14]:
            sub_df = df[df['name'].str.contains(f"-{mod_label}")]
            data = get_table_data(sub_df, "valid")
            reports.append([hash_size, mod_label] + data)
    c = 5
    df = pd.DataFrame(reports,
                      columns=[
                          'pHash', "Wire mil", 'Hamming', 'Normalized', 'AD',
                          f"Valid ({config['ave_threshold']})"
                      ])
    tex = create_latex_table(df,
                             column_format="cccccc",
                             sort=["pHash", "Wire mil"],
                             label=f"table:mpls-{label}",
                             mid_rows=[c, c * 2, c * 3],
                             mid_offset=6,
                             caption=get_caption(f"mpls_{label}_caption"))
    if export_tex:
        utils.text_to_file(tex,
                           f"../paper/res/tex/tables/mpls-{label}.table.tex")


def create_mpls_report_wires_only2(file_path: str, label: str):
    df = pd.DataFrame([],
                      columns=["hash_size", "name", "ham", "norm", "valid"])
    sheets = glob(file_path)
    for sheet in sheets:
        df_sheet = pd.read_excel(sheet)
        df = pd.concat([df_sheet, df], ignore_index=True)
        df = df[['hash_size', 'name', 'ham', 'norm', 'valid']]
    tex = create_latex_table(df,
                             column_format="cccccc",
                             label="table:mpls-wires",
                             caption="Wires only manipulations",
                             sort=["hash_size", "name"],
                             mid_rows=[11, 28],
                             mid_offset=12)
    print("table:mpls-wires:", tex)
    if export_tex:
        utils.text_to_file(tex,
                           f"../paper/res/tex/tables/mpls-{label}.table.tex")


# Create reports
out = config.get('reports_output')
#create_mpls_report_wires_only2(f"{out}/hash-*-wire_only_mpls-output.xlsx", "wires_only_mpls")

# create_ave_report(f"{out}/hash-*-single-output.xlsx", "single")
# create_crop_report()
# create_fpos_report(f"{out}/hash-*-single-fpos-output.xlsx", "single")
create_ave_report(f"{out}/hash-*-versions-output.xlsx", "versions")
create_fpos_report(f"{out}/hash-*-versions-fpos-output.xlsx", "versions")
# create_mpls_report(f"{out}/hash-*-mpl_conduct_layout-output.xlsx", "conduct_layout")
# create_mpls_report(f"{out}/hash-*-mpl_elements-output.xlsx", "elements")
#create_mpls_report_wires(f"{out}/hash-*-mpl_conduct_width-output.xlsx", "conduct_width")
#create_ave_report(f"{out}/hash-*-wires_only-output.xlsx", "wires_only")
