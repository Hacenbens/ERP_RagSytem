from fastapi import APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import Settings,get_settings
from controllers import DataController,ProjectController
from models import ResponseSignal
import aiofiles
import os

data_route = APIRouter(
    prefix ="/data/v1",
    tags = ["api_v1","data"]
)

@data_route.post("/upload/{project_id}")
async def upload_file (project_id:str,file:UploadFile,app_settings:Settings = Depends(get_settings)):
    
    data_controller = DataController()
    
    is_valid,signal = data_controller.validate_file(file=file)
    
    if not is_valid :
        return JSONResponse(
            status=status.HTTP_404_BAD_REQUEST,
            content={
                signal:signal
            }
        )
        
    file_path = data_controller.generate_file_name(org_file_name=file.filename,prject_id=project_id)
    
    try:
        async with aiofiles.open(file_path,"wb") as f:
            while chunk :=await file.read(app_settings.FILE_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        return JSONResponse(
            status=status.HTTP_404_BAD_REQUEST,
            content={
                "signal":ResponseSignal.FILE_UPLOADED_FAILED
            }
        )            
    
    return JSONResponse(
        content={
            "signal":ResponseSignal.FILE_UPLOADED_SUCCESSFULY.value
        }
    )        
    