from enum import Enum


class ResponseSignal(Enum):
    
        FILE_VALIDATED_SUCCESSFULY = "the file is validated succefuly"
        FILE_UPLOADED_SUCCESSFULY = "the file is uploaded successfuly"
        FILE_UPLOADED_FAILED = "the file failed to be uploaded"
        FILE_TYPE_NOT_ACCEPTED = "the file upload has not supported format"
        FILE_MAX_SIZE_EXCEPTION = "file size has been exceeded"