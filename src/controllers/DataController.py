from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
from helpers.file_cleaner import FileNameCleaner
import os
import re


class DataController (BaseController):   
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 #convert MB to bytes
        
    def validate_file (self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_EXTENTIONS_ALLOWED :
            return False , ResponseSignal.FILE_TYPE_NOT_ACCEPTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale :
            return False,ResponseSignal.FILE_MAX_SIZE_EXCEPTION.value
        
        return True,ResponseSignal.FILE_VALIDATED_SUCCESSFULY.value
        
    def generate_file_name (self,org_file_name:str,prject_id:str):
        
        clean_filename = FileNameCleaner.with_uuid(org_file_name)
        dir_file_path = ProjectController().get_project_folder(project_id=prject_id)
        
        file_path = os.path.join(
            dir_file_path,
            clean_filename
        )
        return file_path         

