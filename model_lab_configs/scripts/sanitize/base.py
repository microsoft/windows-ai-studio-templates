"""
Base model classes
"""

from typing import Optional

from pydantic import BaseModel

from .utils import open_ex


class BaseModelClass(BaseModel):
    """Base class for all model classes with file I/O capabilities"""

    _file: Optional[str] = None
    _fileContent: Optional[str] = None

    def writeIfChanged(self):
        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open_ex(self._file, "w") as file:
                file.write(newContent)

    class Config:
        arbitrary_types_allowed = True
