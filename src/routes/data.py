from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import Settings, get_settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
import aiofiles
import os
from .schemes.data import ProcessRequest
from helpers.logger import app_logger  # Import the logger
import time
import traceback

data_route = APIRouter(
    prefix="/data/v1",
    tags=["api_v1", "data"]
)

@data_route.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    
    app_logger.info(f"=== File Upload Started ===")
    app_logger.info(f"Project ID: {project_id}")
    app_logger.info(f"File name: {file.filename}")
    app_logger.info(f"File content type: {file.content_type}")
    
    start_time = time.time()
    
    data_controller = DataController()
    
    # Validate file
    app_logger.debug(f"Validating file: {file.filename}")
    is_valid, signal = data_controller.validate_file(file=file)
    
    if not is_valid:
        app_logger.warning(f"File validation failed: {signal}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": signal
            }
        )
    
    app_logger.debug(f"File validation successful")
    
    # Generate file path
    file_path, file_id = data_controller.generate_file_name(
        org_file_name=file.filename, 
        project_id=project_id
    )
    app_logger.info(f"Generated file_id: {file_id}")
    app_logger.debug(f"File will be saved to: {file_path}")
    
    # Save file
    try:
        file_size = 0
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
                await f.write(chunk)
                file_size += len(chunk)
        
        app_logger.info(f"File uploaded successfully - Size: {file_size} bytes")
        app_logger.info(f"Upload completed in {time.time() - start_time:.2f} seconds")
        
    except Exception as e:
        app_logger.error(f"File upload failed: {str(e)}")
        app_logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOADED_FAILED.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESSFULY.value,
            "file_path": file_path,
            "file_id": file_id,
            "size_bytes": file_size
        }
    )

@data_route.post("/process/{project_id}")
async def process_file(project_id: str, process_request: ProcessRequest, request: Request):
    
    app_logger.info(f"=== File Processing Started ===")
    app_logger.info(f"Project ID: {project_id}")
    app_logger.info(f"Request data: {process_request}")
    app_logger.info(f"Client host: {request.client.host}")
    
    start_time = time.time()
    
    file_id = process_request.file_id
    chunk_size = process_request.chunck_size  # Fixed typo: chunck_size -> chunk_size
    overlap_size = process_request.overlap_size
    
    app_logger.info(f"Processing parameters:")
    app_logger.info(f"  - File ID: {file_id}")
    app_logger.info(f"  - Chunk Size: {chunk_size}")
    app_logger.info(f"  - Overlap Size: {overlap_size}")
    
    # Initialize controller
    app_logger.debug(f"Initializing ProcessController for project {project_id}")
    process_controller = ProcessController(project_id=project_id)
    
    # Get file content
    try:
        app_logger.info(f"Attempting to get content for file: {file_id}")
        file_content = process_controller.get_file_content(file_id=file_id)
        app_logger.info(f"Successfully retrieved file content")
        app_logger.debug(f"Content type: {type(file_content)}")
        app_logger.debug(f"Content length: {len(file_content) if file_content else 0}")
        
    except FileNotFoundError as e:
        app_logger.error(f"File not found: {file_id}")
        app_logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignal.FILE_NOT_FOUND.value,
                "error": str(e)
            }
        )
    except ValueError as e:
        app_logger.error(f"Invalid file type: {str(e)}")
        app_logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.INVALID_FILE_TYPE.value,
                "error": str(e)
            }
        )
    except Exception as e:
        app_logger.error(f"Unexpected error getting file content: {str(e)}")
        app_logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_PROCESSED_FAILED.value,
                "error": str(e)
            }
        )
    
    # Process file into chunks
    try:
        app_logger.info(f"Processing file into chunks...")
        app_logger.info(f"Chunk size: {chunk_size}, Overlap: {overlap_size}")
        
        file_chunks = process_controller.process_file(
            file_id=file_id,
            file_content=file_content,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )
        
        processing_time = time.time() - start_time
        app_logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        if file_chunks is None:
            app_logger.warning(f"Process file returned None")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_PROCESSED_FAILED.value,
                    "error": "Processing returned no chunks"
                }
            )
        
        chunks_count = len(file_chunks)
        app_logger.info(f"Generated {chunks_count} chunks")
        
        # Log sample of first chunk for debugging
        if chunks_count > 0:
            first_chunk = file_chunks[0]
            app_logger.debug(f"First chunk preview: {str(first_chunk.page_content)[:100]}...")
            if hasattr(first_chunk, 'metadata'):
                app_logger.debug(f"First chunk metadata: {first_chunk.metadata}")
        
        # Return response with metadata
        return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_PROCESSED_SUCCESSFULLY.value,
                "project_id": project_id,
                "file_id": file_id,
                "chunks_count": chunks_count,
                "chunk_size": chunk_size,
                "overlap_size": overlap_size,
                "processing_time_seconds": round(processing_time, 2),
                "chunks": [
                    {
                        "page_content": chunk.page_content,
                        "metadata": chunk.metadata
                    } for chunk in file_chunks
                ]
            }
        )
        
    except Exception as e:
        app_logger.error(f"Error processing file: {str(e)}")
        app_logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_PROCESSED_FAILED.value,
                "error": str(e)
            }
        )