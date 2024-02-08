from __future__ import absolute_import, division, print_function
import numpy as np
from PIL import Image
import imagehash
import pandas as pd
import utils
import os
from glob import glob
import scipy.fftpack
from mconfig import config
from math import floor


class pHashBaseController:

    def __init__(self):
        self.hash_size = config["hash_size"]

    def compare(self, a_path: str, b_path: str):
        a_img = Image.open(a_path)
        b_img = Image.open(b_path)
        a = self.get_phash(a_img)
        b = self.get_phash(b_img)
        print("lib:", a - b)
        r = utils.get_phash_distance(str(a), str(b))
        return r

    def compare_crop_resistant(self, a_path: str, b_path: str):
        a_img = Image.open(a_path)
        b_img = Image.open(b_path)
        a = imagehash.crop_resistant_hash(a_img,
                                          imagehash.phash,
                                          min_segment_size=1024)
        b = imagehash.crop_resistant_hash(b_img,
                                          imagehash.phash,
                                          min_segment_size=1024)
        diff = a.hash_diff(b)
        return diff

    def get_phash(self, image: Image.Image):
        fn = image.filename
        image = image.convert('L')
        high_freq_factor = config["high_freq_factor"]
        hash_img_size = int(self.hash_size * high_freq_factor)
        size = (hash_img_size, hash_img_size)

        if config.get("phash_resize_mode") == "fit":
            scaled_size = self.get_scaled_size(hash_img_size, image.width,
                                               image.height)
            resized_img = image.resize(scaled_size, Image.Resampling.LANCZOS)
            black_square = Image.new(mode="L", size=size)
            black_square.paste(resized_img)
            image = black_square

            image.save("./assets/output/phash/" + os.path.basename(fn))
        else:
            image = image.resize(size, Image.Resampling.LANCZOS)

        # phash with FFT
        pixels = np.asarray(image)
        axis0 = scipy.fftpack.dct(pixels, axis=0)
        dct = scipy.fftpack.dct(axis0, axis=1)

        # Extracts a square submatrix from the dct matrix
        # This submatrix contains the low-frequency DCT coefficients
        # which are often more important for perceptual hashing.
        dctlowfreq = dct[:self.hash_size, :self.hash_size]

        binary_array_diff = dctlowfreq > np.median(dctlowfreq)
        return imagehash.ImageHash(binary_array_diff)

    def get_scaled_size(self, h_size, imgW, imgH) -> (int, int):
        if imgW > imgH:
            s_height = h_size / float(imgW)
            s_width = int(imgH * s_height)
            return (h_size, s_width)
        else:
            s_height = h_size / float(imgH)
            s_width = int(imgW * s_height)
            return (s_width, h_size)


class pHashController(pHashBaseController):
    metadata: dict

    def __init__(self, files: list, config: dict, is_version_set: bool,
                 calc_ave_hash: bool):
        super().__init__()
        self.ave_threshold = config[
            "ave_threshold_versions" if is_version_set else "ave_threshold"]
        self.files = files
        if files.__len__() > 0:
            self.phashes = self.create_phash_list()

            if calc_ave_hash:
                self.get_average_hash(self.phashes)

    def create_phash_list(self):
        """
        Generate perceptual hashes
        """

        self.baseline_a_hash = []
        self.baseline_d_hash = []
        self.baseline_w_hash = []

        self.phashes = []
        for file in self.files:
            img = Image.open(file)
            # average_hash and dhash, hash performs slightly worse in most cases

            self.baseline_d_hash.append(imagehash.dhash(img))
            self.baseline_a_hash.append(imagehash.average_hash(img))
            self.baseline_w_hash.append(imagehash.whash(img))

            hash = self.get_phash(img)
            self.phashes.append(hash)
            self.metadata = {}

        return self.phashes

    def get_average_hash(self, hash_list: list):
        """
        Takes the average of all bits of all hashes to create a new hash

        :param hash_list: List containing all hashes as type ImageHash
        """
        aph = []
        for i in range(self.hash_size):
            byte_list: list = [[] for _ in range(self.hash_size)]
            for hash_idx in range(hash_list.__len__()):
                for k in range(self.hash_size):
                    byte_list[k].append(hash_list[hash_idx].hash[i][k])
            for k in range(byte_list.__len__()):
                val = np.median(byte_list[k])
                byte_list[k] = floor(val)
            aph.append(byte_list)

        h = imagehash.ImageHash(np.array(aph))
        self.average_phash = str(h)
        return h

    def get_table_data(self, hashes: list, metadata: dict,
                       folder: str) -> pd.DataFrame:
        """
            Create table:
            Folder / Hamming (to ave) / Normalized (to ave) / Manipulator
        """
        table = []
        for idx, hash_binary in enumerate(hashes):
            hash = str(hash_binary)
            hamming, normalized = utils.get_phash_distance(
                hash, self.average_phash)
            name = metadata["names"][idx]
            module = folder.split("/")[-2]  # := Folder name for versions

            table.append([
                name,
                hash,
                self.average_phash,
                hamming,
                str(hash).__len__(),
                normalized,
                metadata["modifier"][idx],
                metadata["value"][idx],
                metadata["image_set_type"][idx],
                module,
                normalized >= self.ave_threshold,
            ])

        df = pd.DataFrame(table,
                          columns=[
                              'name', 'phash', 'ave-hash', 'ham', "ham-max",
                              'norm', 'mod', 'value', 'image_set', "module",
                              'valid'
                          ])
        return df.sort_values(by=['name', 'value'])

    def get_table_data_versions(self, hashes: list, metadata: dict,
                                folder: str) -> pd.DataFrame:
        """
            Create table:
            Folder / Hamming (to ave) / Normalized (to ave) / Manipulator
        """
        table = []

        for i, hash_binary in enumerate(hashes):
            p_hash_1 = str(hash_binary)
            hamming, normalized = utils.get_phash_distance(
                p_hash_1, self.average_phash)

            name = metadata["names"][i]
            module = folder.split("/")[-2]  # := Folder name for versions
            sum_phash = 0

            for k, hash_binary_k in enumerate(hashes):
                if k == i:
                    continue  # Skip same image

                p_hash_2 = str(hash_binary_k)

                _, default_hash_norm = utils.get_phash_distance(
                    p_hash_1, p_hash_2)
                sum_phash += default_hash_norm

            sum_phash = sum_phash / (len(hashes) - 1)

            table.append([
                name,
                p_hash_1,
                self.average_phash,
                hamming,
                str(p_hash_1).__len__(),
                metadata["modifier"][i],
                metadata["value"][i],
                metadata["image_set_type"][i],
                module,
                normalized >= self.ave_threshold,
                normalized,
                sum_phash,
            ])

        df = pd.DataFrame(table,
                          columns=[
                              'name', 'phash', 'ave-hash', 'ham', "ham-max",
                              'mod', 'value', 'image_set', "module", 'valid',
                              'norm', 'phash-n'
                          ])

        return df.sort_values(by=['name', 'value'])

    def get_manual_mpls(self, file_list: list, label: str):
        hash_list = []
        for mpls_folder in file_list:
            folders = glob(f"{mpls_folder}/*")
            na_phash = self.__get_na_phash(folders)
            for file in folders:
                file_split = file.split("-")
                mod = file_split[file_split.__len__() - 1][:-4]

                if mod == "na":
                    continue
                elif os.path.basename(file_split[0]) == "na":
                    continue

                if mod == "na":
                    continue
                if label == "elements":
                    name = f"{mod}"
                elif label == "conduct_width":
                    layer = file.split("/")[-2].split("_")[0]
                    name = f"{mod}_{layer}-{os.path.basename(file_split[0])}"
                elif label == "conduct_layout":
                    name = os.path.basename(file)[:-4]
                elif label == "wire_only_mpls":
                    name = f"{mod}_{os.path.basename(file_split[0])}"

                img = Image.open(file)
                phash = str(self.get_phash(img))
                hamming, normalized = utils.get_phash_distance(phash, na_phash)
                hash_list.append([
                    name,
                    self.hash_size,
                    hamming,
                    normalized,
                    normalized >= self.ave_threshold,
                ])
        return pd.DataFrame(
            hash_list, columns=['name', 'hash_size', 'ham', 'norm', 'valid'])

    def __get_na_phash(self, files: list):
        for file in files:
            if "-na" in file or "na-" in file:
                img = Image.open(file)
                return str(self.get_phash(img))
