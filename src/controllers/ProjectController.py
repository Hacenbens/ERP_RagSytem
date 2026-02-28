from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
        
    def get_project_folder (self,project_id:str):
        project_folder = os.path.join(
            self.files_dir,
            project_id
        )    
        
        if not os.path.exists(project_folder):
            os.mkdir(project_folder)
        
        return project_folder    