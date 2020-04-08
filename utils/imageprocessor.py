import os
import cv2
import numpy as np


class ImageProcessor():
    
    def __init__(self, config):
        self.path = os.path.join(os.getcwd(), config['image_dir'])
        self.thumbnail_path = os.path.join(self.path, "thumbnails")
        self.original_path = os.path.join(self.path, "originals")
        self.image_queue = []
        self.thumb_factor = config['resize_factor']
        
        # Ensure our directories exist
        try: os.makedirs(self.path)
        except FileExistsError: pass
        try: os.makedirs(self.thumbnail_path)
        except FileExistsError: pass
        try: os.makedirs(self.original_path)
        except FileExistsError: pass

    def queue_image(self, name, data):
        self.image_queue.append({"name": name, "data": data})
    
    def thumbnail_location(self, name):
        return os.path.join(self.thumbnail_path, name + ".jpg")
    
    def original_location(self, name):
        return os.path.join(self.original_path, name + ".jpg")
    
    def conversion_thread(self):
        while True:
            if len(self.image_queue) > 0:
                for image in self.image_queue:
                    name = image['name']
                    data = image['data']
                    # convert string of image data to uint8
                    nparr = np.fromstring(data, np.uint8)
                    # decode image
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    # Save our original image
                    cv2.imwrite(os.path.join(self.original_path, name + ".jpg"), img)
                    # Resize to thumbnail
                    thumb = cv2.resize(img, 
                                       None, 
                                       fx=self.thumb_factor, 
                                       fy=self.thumb_factor, 
                                       interpolation=cv2.INTER_CUBIC
                                       )
                    # Save our thumbnail
                    cv2.imwrite(os.path.join(self.thumbnail_path, name + ".jpg"), thumb)
                    # Remove from queue
                    del self.image_queue[self.image_queue.index(image)]
                    

                    
    