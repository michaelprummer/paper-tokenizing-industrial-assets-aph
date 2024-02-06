from PIL import Image, ImageEnhance
from glob import glob
import os


class pImageController:
    verbose = False

    def __init__(self, config: dict):
        self.config = config

    def get_config(self, key: str):
        return self.config[key]

    def get_output_path(self, suffix=""):
        return f"./assets/output/{suffix}"

    def resize_image(self, img: Image.Image, file_path: str, scale_width: float, folder: str):
        """
            Resize image based on width
        """
        target_width = int(img.size[0] * scale_width)
        w_percent = (target_width/float(img.size[0]))
        h_size = int((float(img.size[1])*float(w_percent)))
        resized_img = img.resize(
            (target_width, h_size), Image.Resampling.LANCZOS)
        
        if resized_img.width < 32:
            print("=== Warning - low width: ", resized_img.width, file_path)
        
        if resized_img.height < 32:
            print("=== Warning - low height: ", resized_img.height, file_path)

        self.save_image(resized_img, file_path, folder, f"res-{scale_width}-")

    def save_image(self, img: Image.Image, file_path: str, folder: str, prefix=""):
        filename = os.path.basename(file_path).replace(
            "-", "_").lower().replace(".brd", "")
        os_path = os.path.join(
            self.get_output_path(self.output_folder), folder)
        if not os.path.exists(os_path):
            os.makedirs(os_path)

        img.save(os.path.join(
            os_path, f"{prefix}{filename}"))

    def crop_image(self, img: Image.Image, crop_scale: float):
        """
            Center crop image
            crop_scale: Percent of the remaining image
        """
        if crop_scale > 1 or crop_scale < 0:
            raise Exception("crop_scale has to be 0 > scale < 1")
        w, h = img.size
        w2 = w/2
        h2 = h/2
        crop_width2 = (w * crop_scale)/2
        crop_hight2 = (h * crop_scale)/2
        rect = (int(w2 - crop_width2), int(h2 - crop_hight2),
                int(w2 + crop_width2), int(h2 + crop_hight2))
        return img.crop(rect)

    def manipulate_image(self, img: Image.Image, file_path: str, folder: str):
        """
            Distributes random image tiles through the image
        """
        w, h = img.size
        t_size = self.get_config("mpl_tile_sizes")
        t_angel = self.get_config("mpl_tile_angle")
        for idx, mpl_tile_size in enumerate(t_size):
            angle = t_angel[idx]
            tile_size2 = int(h * mpl_tile_size / 2)
            w2 = int(w/2)
            h2 = int(h/2)
            crop_rect = (w2 - tile_size2, h2 - tile_size2,
                         w2 + tile_size2, h2 + tile_size2)
            cropped_img = img.crop(crop_rect).rotate(angle)
            cropped_img.copy()

            img.paste(cropped_img, (crop_rect[0], crop_rect[1]))
            self.save_image(img, file_path, folder,
                            f"mpl-rotate_{angle}_{mpl_tile_size}-")

    def __create_images_colorize(self, img: Image.Image, file_path: str, folder: str):
        try:
            enhancer = ImageEnhance.Brightness(img)
            lighter = enhancer.enhance(1.5)
            darker = enhancer.enhance(0.5)
            self.save_image(lighter, file_path, folder, "mpl-color_lighter-")
            self.save_image(darker, file_path, folder, "mpl-color_darker-")

        except Exception as e:
            print(f"An error occurred: {e}")

    def __create_image_set(self, file_path: str, module_name: str, res_only: bool):
        try:
            with Image.open(file_path) as img:
                img = img.convert('RGB')

                # Normal image
                self.save_image(img, file_path, module_name, "res-na-")
                
                # Resolutions
                for scale in self.get_config("resolution_scale_width"):
                    self.resize_image(img, file_path, scale, module_name)
                
                # Colored
                if res_only == False:
                    self.__create_images_colorize(img, file_path, module_name)
                # Manipulations
                if res_only == False:
                    self.manipulate_image(img, file_path, module_name)

        except Exception as e:
            print(f"An error occurred: {e}")

    def __create_grid_set(self, file_path: str, module_name: str):
        try:
            with Image.open(file_path) as img:
                img = img.convert('RGB')

                # Normal image
                self.save_image(img, file_path, module_name, "res-na-")
                
                # TODO: Build grids 2,4,8,16

                

        except Exception as e:
            print(f"An error occurred: {e}")


    def __create_copped_image_set(self, file_path: str, module_name: str, pre_crop_frame: float):
        """
        Crops image with percents of size
        85% of the image are used as reference to avoid black frames etc.
        """
        self.output_folder = "cropped"
        with Image.open(file_path) as img:
            if pre_crop_frame != None and pre_crop_frame > 0:
                img = self.crop_image(img, pre_crop_frame)
            self.save_image(img, file_path, module_name, "res-na-")

            for crop_size in self.get_config("crop_sizes"):
                cropped_img = self.crop_image(img, crop_size)
                self.save_image(cropped_img, file_path, module_name,
                                f"cropped-{crop_size*100}-")

    def __create_version_image_set(self, file_path: str, module_name: str):
        files = glob(f"{file_path}*")
        for file in files:
            self.__create_image_set(file, module_name, True)

    def __create_gerbers_image_set(self, file_path: str, module_name: str):
        files = glob(f"{file_path}*/*")
        for file in files:
            self.__create_image_set(file, module_name, False)

    def get_module_name(self, files: list) -> str:
        """
            Generates a module name for a file or folder
        """                    
        if files.__len__() > 1 and "versions/" in files[0]:
            return files[0].split("/")[:-1].pop()
        if "gerbers_png/" in files[0]:
            return files[0].split("/").pop()
        elif files.__len__() == 1:
            return os.path.basename(files.pop()[:-4])
        else:
            return "error"

    def get_metadata(self, hashes: list, image_set_type: str) -> dict:
        metadata = dict({"value": [], "modifier": [],
                        "names": [], "image_set_type": []})
        for file in hashes:                        
            splitted = self.get_module_name([file]).split("-")            
            metadata["modifier"].append(splitted[0])
            metadata["value"].append(splitted[1])
            metadata["names"].append(splitted[2])
            metadata["image_set_type"].append(image_set_type)
        return metadata

    def generate_single_images(self, output_folder: str, input: str, stop_after=None):
        self.output_folder = output_folder
        files = glob(input)
        for idx, file in enumerate(files):
            module_name = self.get_module_name(glob(file))
            self.__create_image_set(file, module_name, False)
            if stop_after != None and idx > stop_after - 2:
                break

    def generate_grid_images(self, output_folder: str, input: str, stop_after=None):
        self.output_folder = output_folder
        files = glob(input)
        print("GRID-files")
        print(files.__len__())
        for idx, file in enumerate(files):
             module_name = self.get_module_name(glob(file))
             self.__create_grid_set(file, module_name)
             if stop_after != None and idx > stop_after - 2:
                 break

    def generate_images_versions(self, stop_after=None):
        self.output_folder = "versions/"
        version_folders = glob("./assets/original/versions/*/", recursive=True)

        for idx, folder in enumerate(version_folders):
            module_name = self.get_module_name(glob(f"{folder}*"))
            files = glob(folder)

            # print(f"Created: {module_name}")
            for file in files:
                self.__create_version_image_set(file, module_name)
            if stop_after != None and idx > stop_after - 2:
                break


    def generate_images_gerbers(self, stop_after=None):                        
        self.output_folder = "gerbers/"
        version_folders = glob("./assets/original/gerbers_png/*", recursive=True)

        for idx, folder in enumerate(version_folders):
            module_name = self.get_module_name(glob(f"{folder}*"))
            files = glob(folder)

            #print(f"Created: {module_name}")
            for file in files:                
                self.__create_gerbers_image_set(file, module_name)
            if stop_after != None and idx > stop_after - 2:
                break

    def generate_images_cropped(self, pre_crop_frame: float, stop_after=None):
        self.output_folder = "cropped/"
        files = glob("./assets/original/single/*")

        for idx, file in enumerate(files):
            module_name = self.get_module_name(glob(file))
            self.__create_copped_image_set(file, module_name, pre_crop_frame)
            if stop_after != None and idx > stop_after - 2:
                break
