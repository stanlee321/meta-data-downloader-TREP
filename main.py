import pandas as pd
import os
import os,sys
from PIL import Image
from PIL.ExifTags import TAGS

import requests
import shutil
from datetime import datetime

class MetaDataDownloader:
    def __init__(self):
        """
        This Downloadd the metadata from TREP images
        """
        self.generic_name = 'generic_image_name.jpg'
        
        self.base_path = "logs/"
        
        # load mesas ids:
        
        self.mesas_ids = self.get_mesa_ids(target_file = "TREP/eleccion-hourly-trep/acta.2019.10.25.10.13.40.xlsx")
        
    def write_log(self, file_name, error, message):
        """
        Write the last results
        """
        os.makedirs(self.base_path, exist_ok=True)
        
        path = f"{self.base_path}/{file_name}.txt"

        with open(path,"a+") as f:
            f.write(f"{file_name},{error},{message}")
            
    def create_meta_list(self, image_name, image_url):
        """
        Create list of dicts that contains the metadata key,value
        """
        print(f"input image: {image_name}")
        
        # Aux list
        meta_list = []
        
        try:
            
            for (k,v) in Image.open(image_name)._getexif().items():
                key = TAGS.get(k)
                try:
                    value = v.decode("utf-8")
                except:
                    value = v

                meta_list.append({TAGS.get(k): str(v)})

            # Add the image source acta_id
            meta_list.append({"current_download_datetime": datetime.now()})
            meta_list.append({"image_src": image_url })
        except Exception as e:
            
            message = f"This image {image_url} does not have exif, loging..."
            print(message)
            self.write_log("error", e, message)
                
        return meta_list
    
    def create_df_from_dicts(self, meta_list):
        """
        Combine all the list of dicts into a row of dataframe
        """
        df_to_combine = []
        for d in meta_list:
            df = pd.DataFrame.from_dict(d,  orient='index').T
            df_to_combine.append(df)
            
        df = pd.concat(df_to_combine, axis=1)
        
        return df

    def download_data(self, mesa_id):
        # Set the current mesa_id
        self.mesa_id = mesa_id
        # This is the image url.
        image_url = f"https://trep.oep.org.bo/resul/imgActa/{mesa_id}.jpg"
        # Open the url image, set stream to True, this will return the stream content.
        resp = requests.get(image_url, stream=True)
        # Open a local file with wb ( write binary ) permission.
        
        # Set a generic name for save the image in disck
        local_file = open(self.generic_name, 'wb')
        
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        resp.raw.decode_content = True
        # Copy the response stream raw data to local image file.
        shutil.copyfileobj(resp.raw, local_file)
        # Remove the image url response object.
        del resp
        
        return self.generic_name, image_url
    
    def save_df_to_csv(self, df, mesa_id):
        
        os.makedirs("outputs/", exist_ok=True)
        
        df.to_csv(f"outputs/{mesa_id}.csv", sep=",")
    
    def get_mesa_ids(self, target_file = "TREP/eleccion-hourly-trep/acta.2019.10.25.10.13.40.xlsx"):
        """
        Return the list of actas ids
        """
        df = pd.read_excel(target_file)
        
        mesa_ids = df["Número Mesa"]
        
        print(f"returing ...{len(mesa_ids)} actas ids")
        
        return list(mesa_ids)
    
    def main(self, mesa_id= "50996"):
        
        mesa_id_p = mesa_id + "1"
        
        image_name, image_url = self.download_data(mesa_id_p)
        
        meta_list = self.create_meta_list(image_name, image_url)
        
        if (len(meta_list) == 0):
            # no meta exif for this image
            pass
        else:
            df = self.create_df_from_dicts(meta_list)
            
            self.save_df_to_csv(df, mesa_id)
            


if __name__ == "__main__":
    meta_handler = MetaDataDownloader()

    # Get the messas ids
    mesas_list = meta_handler.mesas_ids

    for i, mesa in enumerate(mesas_list):

        print(f"{i}/{len(mesas_list)}", end="\n")

        meta_handler.main(mesa_id= "50996")
