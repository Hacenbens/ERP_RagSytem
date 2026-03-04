import re
import os
import uuid
from datetime import datetime
import unicodedata
from pathlib import Path

class FileNameCleaner:
    """Utility class for cleaning and sanitizing filenames"""
    
    @staticmethod
    def clean(filename, max_length=255):
        """
        Clean filename for safe storage
        """
        # Split path and filename
        filename = os.path.basename(filename)  # Remove any path components
        name, ext = os.path.splitext(filename)
        
        # Normalize unicode
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        
        # Convert to lowercase (optional, for consistency)
        name = name.lower()
        
        # Replace invalid characters with underscore
        name = re.sub(r'[^a-z0-9\-_.()\[\] ]', '_', name)
        name = re.sub(r'[\s\-]+', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        # If name is empty after cleaning, generate a random one
        if not name:
            name = f"file_{uuid.uuid4().hex[:8]}"
        
        # Truncate if too long
        max_name_len = max_length - len(ext) - 1
        if len(name) > max_name_len:
            name = name[:max_name_len]
        
        return name + ext.lower()
    
    @staticmethod
    def with_timestamp(filename):
        """Add timestamp to cleaned filename"""
        cleaned = FileNameCleaner.clean(filename)
        name, ext = os.path.splitext(cleaned)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}{ext}"
    
    @staticmethod
    def with_uuid(filename):
        """Add UUID to cleaned filename"""
        cleaned = FileNameCleaner.clean(filename)
        name, ext = os.path.splitext(cleaned)
        unique_id = uuid.uuid4().hex[:8]
        return f"{name}_{unique_id}{ext}",unique_id
    
    @staticmethod
    def secure(filename):
        """
        Generate completely new secure filename (ignore original name)
        Use this for maximum security
        """
        ext = os.path.splitext(filename)[1].lower()
        # Validate extension
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.csv']:
            ext = '.bin'  # Default extension for unknown types
        
        safe_name = f"file_{uuid.uuid4().hex[:16]}"
        return f"{safe_name}{ext}"
    
    @staticmethod
    def validate_extension(filename, allowed_extensions):
        """
        Check if file extension is allowed
        """
        ext = Path(filename).suffix.lower()
        return ext in allowed_extensions

# Create a singleton instance for easy import
file_cleaner = FileNameCleaner()