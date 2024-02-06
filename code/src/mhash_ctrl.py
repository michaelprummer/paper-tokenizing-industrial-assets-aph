from glob import glob
import pandas as pd
import os
from phash_ctrl import pHashController
from image_ctrl import pImageController
from utils import count_valid_rows
from merkle import pMerkleTree, sha256
import utils
import json
from mconfig import config

pd.set_option('display.max_rows', 100)


class MultiHashController:
    output_path = str(config.get('reports_output'))

    def __init__(self, img_ctrl: pImageController, config: dict):
        self.img_ctrl = img_ctrl
        self.config = config
        utils.create_dir(self.output_path)

    def create_mhash_average_sheet(self,
                                   input_folder: str,
                                   ave_selector: str,
                                   target_selector: str,
                                   image_set_type: str,
                                   include_ave=True) -> pd.DataFrame:
        folders = glob(self.img_ctrl.get_output_path(input_folder),
                       recursive=True)
        table_data: list = []
        row_selector = target_selector[:-2]

        is_versions = input_folder.__contains__("versions")
        for folder in folders:
            ave_files = glob(f"{folder}{ave_selector}")
            ave_hash_ctrl = pHashController(ave_files, self.config,
                                            is_versions, True)

            if include_ave:
                ave_metadata = self.img_ctrl.get_metadata(
                    ave_files, image_set_type)

                if is_versions:
                    ave_df = ave_hash_ctrl.get_table_data_versions(
                        ave_hash_ctrl.phashes, ave_metadata, folder)
                else:
                    ave_df = ave_hash_ctrl.get_table_data(
                        ave_hash_ctrl.phashes, ave_metadata, folder)

                table_data.append(ave_df)

            target_files = glob(f"{folder}{target_selector}")
            target_hash_ctrl = pHashController(target_files, self.config,
                                               is_versions, False)
            target_metadata = self.img_ctrl.get_metadata(
                target_files, image_set_type)

            if is_versions:
                target_df = ave_hash_ctrl.get_table_data_versions(
                    target_hash_ctrl.phashes, target_metadata, folder)
            else:
                target_df = ave_hash_ctrl.get_table_data(
                    target_hash_ctrl.phashes, target_metadata, folder)

            table_data.append(target_df)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        custom_info = ""
        if row_selector == "cropped":
            custom_info = f", crop-rect: {self.config.get('crop_sizes')}"

        if table_data.__len__() > 0:
            df = pd.concat(table_data)

            ave_threshold_value = self.config["ave_threshold"]

            valid_rows = count_valid_rows(df[df["value"] == "na"], "valid")
            # print(
            #     f"Ave-Valid({config['hash_size']}) against all mpls: {valid_rows:.2%} ({ave_threshold_value}) in {input_folder}",
            #     f"| rows: {table_data.__len__()}",
            #     custom_info)

            print(
                f"Ave-Valid({config['hash_size']}): {valid_rows:.2%} ({ave_threshold_value}) in {input_folder}",
                f"| rows: {table_data.__len__()}", custom_info)

            hash_len = self.config["hash_size"]
            df.reset_index(drop=True, inplace=True)
            df.to_excel(
                f"{self.output_path}/hash-{hash_len}-{input_folder[:-3]}-output.xlsx"
            )
            return df
        else:
            print("Error: No image data was generated for tables:",
                  input_folder)
        return pd.DataFrame()

    def create_mhash_false_positive_sheet(self, mhashes: pd.DataFrame,
                                          label: str):
        """
        Compares the ave hash of every image-set with all other normal images for false positives        
        """
        table_data = []

        # print(mhashes.__getitem__("ave-hash"))
        subset_na = mhashes[mhashes["value"] == "na"]
        fpos_threshold = self.config["ave_threshold"]

        idx_a = 0
        for _, rowA in subset_na.iterrows():
            idx_b = 0
            ave_a = str(rowA.get("ave-hash"))
            name_a = str(rowA.get("name"))
            module_a = str(rowA.get("module"))

            for _, rowB in subset_na.iterrows():
                if idx_b > idx_a:
                    continue

                name_b = str(rowB.get("name"))
                module_b = str(rowB.get("module"))

                if name_a != name_b and module_a != module_b:
                    ave_b = str(rowB.get("ave-hash"))

                    hamming, normalized = utils.get_phash_distance(
                        ave_a, ave_b)
                    new_row = [
                        ave_a, ave_b, name_a, name_b, hamming, normalized,
                        normalized >= fpos_threshold
                    ]
                    table_data.append(new_row)
                idx_b += 1
            idx_a += 1

        df = pd.DataFrame(table_data,
                          columns=[
                              'phash_a', 'phash_b', 'name_a', 'name_b', 'ham',
                              'norm', "valid"
                          ])
        hash_len = self.config["hash_size"]
        df.sort_values(by=['norm', 'name_a'], inplace=True, ascending=False)
        df.to_excel(
            f"{self.output_path}/hash-{hash_len}-{label}-fpos-output.xlsx")

        fpos_valid = count_valid_rows(df, "valid")
        print(
            f"NumOf false positives (res-na x res-na images): {fpos_valid:.2%} for < {fpos_threshold:.0%}"
        )

        # print(df.drop(columns=['phash_a', 'phash_b']))

    def create_mpls_sheet(self):
        hash_len = self.config["hash_size"]
        phash_ctrl = pHashController([], self.config, False, False)
        p = "./assets/original/mpls/"

        df_ele = phash_ctrl.get_manual_mpls(glob(f"{p}elements/*"), "elements")
        df_ele.sort_values(by=['name', 'norm'], inplace=True, ascending=False)
        #df_ele = self.group_element_sheet(df_ele)
        df_ele.to_excel(
            f"{self.output_path}/hash-{hash_len}-mpl_elements-output.xlsx")

        df_lw = phash_ctrl.get_manual_mpls(glob(f"{p}conduct_width_2/*/"),
                                           "conduct_width")
        df_lw.sort_values(by=['name'], inplace=True, ascending=False)
        df_lw.to_excel(
            f"{self.output_path}/hash-{hash_len}-mpl_conduct_width-output.xlsx"
        )

        df_cl = phash_ctrl.get_manual_mpls(glob(f"{p}conduct_layout/*"),
                                           "conduct_layout")
        df_cl.to_excel(
            f"{self.output_path}/hash-{hash_len}-mpl_conduct_layout-output.xlsx"
        )

        df_cl = phash_ctrl.get_manual_mpls(glob(f"{p}wire_only_mpls/*"),
                                           "wire_only_mpls")
        df_cl.to_excel(
            f"{self.output_path}/hash-{hash_len}-wire_only_mpls-output.xlsx")

    def group_element_sheet(self, df: pd.DataFrame):
        mpls_1 = []
        mpls_2 = []
        mpls_3 = []

        for _, row in df.iterrows():
            name = row.get("name")
            mpls = name.split("_")[2]

            norm = row.get("norm")

            if mpls == "1":
                mpls_1.append(norm)
            elif mpls == "2":
                mpls_2.append(norm)
            else:
                mpls_3.append(norm)

        new_df = pd.DataFrame(
            dict({
                "hash_size": row.get("hash_size"),
                "sum_1": [sum(mpls_1) / mpls_1.__len__()],
                "sum_2": [sum(mpls_2) / mpls_2.__len__()],
                "sum_3": [sum(mpls_3) / mpls_3.__len__()]
            }))

        print(new_df)

        return new_df

    def create_tree(self, files):
        """
            Generate cryptographic sha256 hashes
        """
        c_hashes = []
        self.tree = pMerkleTree()

        for filename in files:
            with open(filename, "rb") as f:
                bytes = f.read()
                readable_hash = sha256(bytes)
                c_hashes.append(readable_hash)
                self.tree.append_entry(readable_hash)

    def get_merkle_root(self) -> str:
        merkle_root = self.tree.m_get_root()
        # is_proof_valid = self.tree.m_proof(2)
        # print("is_proof_valid:", is_proof_valid)
        return merkle_root

    def toJson(self, average_phash: str, indent=0):
        return json.dumps(
            {
                "merkle_root": self.get_merkle_root(),
                "average_phash:": average_phash
            },
            indent=indent)
