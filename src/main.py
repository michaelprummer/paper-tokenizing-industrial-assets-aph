from image_ctrl import pImageController
from mhash_ctrl import MultiHashController
from mconfig import config, All, Some
import reporter
import utils

#######################################
######### Execution config ############
#######################################
run_image_generation = True  # Just need to be done once
run_version = All
run_single = All
run_crop = All
run_grid_mpl = None
run_mpls = All
run_wires_only = All
run_reports = All
#######################################

# Clean outputs (Exclude manual modified gerbers)
if run_image_generation:
    utils.delete_folder("./assets/output/cropped/*/")
    utils.delete_folder("./assets/output/grid/*/")
    utils.delete_folder("./assets/output/single/*/")
    utils.delete_folder("./assets/output/versions/*/")
    utils.delete_folder("./assets/output/wires_only/*/")

if run_reports:
    utils.delete_files("./reports/*.xlsx")

for hash_size in config["hash_sizes"]:
    config["hash_size"] = hash_size
    img_ctrl = pImageController(config)
    mhash_ctrl = MultiHashController(img_ctrl, config)

    # Manual mpls
    if run_mpls != None and run_mpls > 0:
        mhash_ctrl.create_mpls_sheet()

    # Single image-set
    if run_single != None and run_single > 0:
        if run_image_generation:
            img_ctrl.generate_single_images(output_folder="single/",
                                            input="./assets/original/single/*",
                                            stop_after=run_single)
        df_single = mhash_ctrl.create_mhash_average_sheet(
            "single/*/", "res-*", "mpl-*", "single")
        mhash_ctrl.create_mhash_false_positive_sheet(df_single, "single")

    # Wires only set
    if run_wires_only != None and run_wires_only > 0:
        if run_image_generation:
            img_ctrl.generate_single_images(
                output_folder="wires_only/",
                input="./assets/original/gerbers/wires_only/*",
                stop_after=run_wires_only)
        df_wires = mhash_ctrl.create_mhash_average_sheet(
            "wires_only/*/", "res-*", "mpl-*", "wires_only")
        mhash_ctrl.create_mhash_false_positive_sheet(df_wires,
                                                     "run_wires_only")

    # Cropped (on single)
    if run_crop != None and run_crop > 0:
        if run_image_generation:
            img_ctrl.generate_images_cropped(stop_after=run_crop,
                                             pre_crop_frame=0.95)
        df_crop = mhash_ctrl.create_mhash_average_sheet(
            "cropped/*/", "res-*", "cropped-*", "single", False)

    # Versions image-set
    # if run_version != None and run_version > 0:
    #     if run_image_generation:
    #         img_ctrl.generate_images_versions(stop_after=run_version)
    #     df_versions = mhash_ctrl.create_mhash_average_sheet(
    #         input_folder="versions/*/",
    #         ave_selector="res-*",
    #         target_selector="res-*",
    #         image_set_type="versions")
    #     mhash_ctrl.create_mhash_false_positive_sheet(df_versions, "versions")

    # Versions image-set baseline
    if run_version != None and run_version > 0:
        if run_image_generation:
            img_ctrl.generate_images_versions(stop_after=run_version)
        df_versions = mhash_ctrl.create_mhash_average_sheet(
            input_folder="versions/*/",
            ave_selector="res-*",
            target_selector="res-*",
            image_set_type="versions")
        #mhash_ctrl.create_mhash_false_positive_sheet(df_versions, "versions")

if run_reports:
    # Create reports
    out = config.get('reports_output')

    if run_crop != None and run_crop > 0:
        reporter.create_crop_report()

    # Creates the ave hash form res-* images and checks them against the manipulated images
    if run_single != None and run_single > 0:
        reporter.create_ave_report(f"{out}/hash-*-single-output.xlsx",
                                   "single")
        reporter.create_fpos_report(f"{out}/hash-*-single-fpos-output.xlsx",
                                    "single")

    # Creates the ave hash form res-* images of all versions and checks them against the single res-* images
    if run_version != None and run_version > 0:
        reporter.create_ave_report(f"{out}/hash-*-versions-output.xlsx",
                                   "versions")
        reporter.create_fpos_report(f"{out}/hash-*-versions-fpos-output.xlsx",
                                    "versions")

    if run_mpls != None and run_mpls > 0:
        reporter.create_mpls_report(
            f"{out}/hash-*-mpl_conduct_layout-output.xlsx", "conduct_layout")
        reporter.create_mpls_report(f"{out}/hash-*-mpl_elements-output.xlsx",
                                    "elements")
        reporter.create_mpls_report_wires(
            f"{out}/hash-*-mpl_conduct_width-output.xlsx", "conduct_width")
        reporter.create_mpls_report_wires_only2(
            f"{out}/hash-*-wire_only_mpls-output.xlsx", "wires_only_mpls")

    if run_wires_only != None and run_wires_only > 0:
        reporter.create_ave_report(f"{out}/hash-*-wires_only-output.xlsx",
                                   "wires_only")
        reporter.create_fpos_report(
            f"{out}/hash-*-run_wires_only-fpos-output.xlsx", "wires_only")
