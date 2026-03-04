from enum import Enum


class ResponseSignal(Enum):
    
        FILE_VALIDATED_SUCCESSFULLY = "the file is validated succefuly"
        FILE_UPLOADED_SUCCESSFULLY = "the file is uploaded successfuly"
        FILE_UPLOADED_FAILED = "the file failed to be uploaded"
        FILE_TYPE_NOT_ACCEPTED = "the file upload has not supported format"
        FILE_MAX_SIZE_EXCEPTION = "file size has been exceeded"
        FILE_PROCESSED_SUCCESSFULLY = "the file has been successfuly done"
        FILE_PROCESSED_FAILED = "the processing of the file has failed  "