from .BaseController import BaseController
from .ProjectController import ProjectController
from models import FileExtentions
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from interfaces.IDBClientContext import IDBClientContext
import os
from helpers.logger import app_logger  # Import the logger

class ProcessController(BaseController):
    
    def __init__(self, project_id,db_client:IDBClientContext):
        super().__init__(db_client=db_client)
        self.project_id = project_id
        self.project_path = ProjectController().get_project_folder(project_id=project_id)
        app_logger.info(f"ProcessController initialized for project: {project_id}")
        app_logger.debug(f"Project path: {self.project_path}")
    
    
    def get_file_extention(self, file_id: str):
        ext = os.path.splitext(file_id)[-1]
        app_logger.debug(f"File extension for {file_id}: {ext}")
        return ext   
    
    def get_file_loader(self, file_id: str):
        file_extension = self.get_file_extention(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )
        
        app_logger.debug(f"Attempting to create loader for file: {file_path}")
        
        if file_extension == FileExtentions.TXT.value:
            app_logger.info(f"Creating TextLoader for {file_id}")
            return TextLoader(file_path)
        
        if file_extension == FileExtentions.PDF.value:
            app_logger.info(f"Creating PyMuPDFLoader for {file_id}")
            return PyMuPDFLoader(file_path)
        
        # Log unsupported file types
        app_logger.error(f"Unsupported file extension: {file_extension} for file: {file_id}")
        app_logger.warning(f"Supported extensions: {FileExtentions.TXT}, {FileExtentions.PDF}")
        return None
    
    def get_file_content(self, file_id: str):
        app_logger.info(f"Getting content for file: {file_id}")
        
        loader = self.get_file_loader(file_id=file_id)
        
        # Check if loader is None before trying to load
        if loader is None:
            error_msg = f"Cannot load file {file_id}: Unsupported file type or file not found"
            app_logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            app_logger.debug(f"Loading content from {file_id}")
            content = loader.load()
            app_logger.info(f"Successfully loaded content from {file_id}")
            app_logger.debug(f"Content length: {len(content)} pages/sections")
            return content
        except Exception as e:
            app_logger.error(f"Error loading content from {file_id}: {str(e)}", exc_info=True)
            raise
    
    async def process_file(self, file_id: str, file_content: str, chunk_size: int , overlap_size: int ):
        app_logger.info(f"Processing file: {file_id} with chunk_size={chunk_size}, overlap={overlap_size}")
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap_size,
                length_function=len
            )
            
            app_logger.debug(f"Extracting text content from {len(file_content)} records")
            
            file_content_texts = [
                rec.page_content
                for rec in file_content
            ]
            
            file_metadatas = [
                rec.metadata  # Fixed typo: page_metadata -> metadata
                for rec in file_content
            ]
            
            app_logger.debug(f"Creating chunks from content")
            
            chunks = text_splitter.create_documents(
                texts=file_content_texts,    
                metadatas=file_metadatas
            )
            
            app_logger.info(f"Successfully created {len(chunks)} chunks from {file_id}")
            app_logger.debug(f"First chunk preview: {chunks[0].page_content[:50]}..." if chunks else "No chunks created")
            
            stored_chunks = await self.db_client.store_chunks(
            project_id=self.project_id,
            file_id=file_id,
            langchain_chunks=chunks  # Vos chunks langchain
            )
        
            return {
                "file_id": file_id,
                "chunks_count": len(stored_chunks),
                "chunks": stored_chunks[:3]
            }
            
        except Exception as e:
            app_logger.error(f"Error processing file {file_id}: {str(e)}", exc_info=True)
            raise