import os
from pylons import app_globals

def delete_image(image):
    paths = image.path.split(';')
    for p in paths:
        path = os.path.join(app_globals.image_storage, p)
        os.remove(path)

