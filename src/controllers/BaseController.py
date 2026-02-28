from helpers.config import get_settings
import os
import string
import random

class BaseController :
    
    def __init__ (self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )
    
    def generate_random_string(self,length=8):
        """Generate a random string of fixed length"""
        letters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
        return ''.join(random.choice(letters) for _ in range(length))