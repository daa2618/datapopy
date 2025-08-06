
import zipfile, tempfile
from response import Response
from typing import Union, Optional,Tuple
from pathlib import Path

class ExtractZipFile:
    """
    Extracts a zip file from a given URL to a specified folder.

    Args:
        url (str): The URL of the zip file to be extracted.
        extract_to_folder (str): The path to the folder where the zip file 
                               should be extracted.  The folder should exist.

    Attributes:
        url (str): The URL of the zip file.
        extract_to_folder (str): The extraction destination folder.
        _file_name (str):  Internal attribute;  The name of the extracted file 
                          (currently set to a placeholder "randomFileName").  This 
                          might be updated in a more complete implementation.

    Note:
        This class currently only initializes attributes.  The actual extraction 
        logic is missing and needs to be implemented.  The `_file_name` attribute 
        suggests future functionality to handle file_name determination.
    """
    def __init__(self, url:str, extract_to_folder:Union[str|Path]):
        self.url = url
        self.extract_to_folder = Path(extract_to_folder) if isinstance(extract_to_folder, str) else extract_to_folder
        self._file_name = "randomFileName"
        
    @property
    def _temp_dir(self):
        """Creates and returns a temporary directory.

        This property creates a temporary directory using `tempfile.mkdtemp()` and 
        returns its path.  

        Returns:
            str: The path to the newly created temporary directory.
        """
        temp_dir = tempfile.mkdtemp()
        return Path(temp_dir)
    
    @property
    def _temp_file_path(self):
        """
        Returns the full path to a temporary file.

        This property combines the temporary directory path (self._temp_dir) 
        with the file_name (self._file_name) to create the complete path to a 
        temporary file.  

        Returns:
            str: The full path to the temporary file.
        """
        #return os.path.join(self._temp_dir, self._file_name)
        return self._temp_dir.joinpath(self._file_name)
    
    @property
    def _get_zip_file(self)->Optional[str]:
        """
        Retrieves the content of a zip file from a URL.

        This property method fetches the content of a zip file located at the URL 
        specified by the `self.url` attribute.  It uses a Response object (presumably 
        from a library like `requests`) to make the request and asserts that the response 
        is successful before returning the content.

        Returns:
            bytes: The raw content of the zip file as bytes.  Returns None if there is an error during the request or assertion.

        Raises:
            AssertionError: If the HTTP request does not return a successful status code.  (The specific exception raised depends on the `assertResponse()` method used).

        Notes:
            This is a private method (indicated by the leading underscore), suggesting it's intended for internal use within the class.  The specifics of `Response` and `assertResponse` depend on the external libraries in use.
        """
        response = None
        try:
            response = Response(self.url).assert_response()
        except Exception as e:
            print(f"Failed to get response from url: {self.url}", e)
            response = None
            return
        
        response_content = response.content if response.content else None

        if not response_content:
            raise ValueError("Response content is empty")
        return response_content
    
    def _write_zip_file_to_temp_dir(self)->Tuple[Path, Path, zipfile.ZipFile]:
        """Writes the internal zip file data to a temporary directory.

        Creates a temporary directory, writes the zip file data (held internally 
        by the object) to a file within that directory, and then opens the 
        created zip file using the zipfile library.

        Returns:
            tuple: A tuple containing:
                - temp_dir (str): The path to the temporary directory.
                - temp_file_path (str): The path to the temporary zip file.
                - zipFile (zipfile.ZipFile): An open zipfile.ZipFile object 
                representing the created zip file.  This should be closed by the 
                caller after use.

        Raises:
            Exception: Any exceptions encountered during temporary directory creation,
                    file writing, or zip file opening will be propagated.  
                    Consider adding more specific exception handling if needed.
        """
        #temp_dir = self._temp_dir
        #temp_file_path = os.path.join(temp_dir, self._file_name)
        temp_file_path  = self._temp_file_path
        #temp_file_path_parent = temp_file_path.parent

        try:
            with open(temp_file_path, "wb") as f:
                f.write(self._get_zip_file)
        except Exception as e:
            print(f"Failed to write zip file at {temp_file_path}", e)
             
        
        return temp_file_path.parent, temp_file_path, zipfile.ZipFile(temp_file_path)
    
    @property
    def extract_zip_file_to_folder(self)->Optional[Path]:
        """
        Extracts a zip file to a specified folder.

        This property method extracts the contents of the zip file associated with the object 
        to a designated folder. It first writes the zip file to a temporary directory, 
        extracts its contents, and then cleans up the temporary files and directory.  The 
        path to the extracted file is returned.

        Returns:
            str: The absolute path to the extracted file within the specified folder.  Returns None if extraction fails.

        Raises:
            Exception: If any error occurs during file extraction or cleanup.  (Consider more specific exceptions if appropriate).
        """
        temp_dir, temp_file_path, file = self._write_zip_file_to_temp_dir()
        print(f"Temporary Directory: {temp_dir}")
        
        with file as f:
            #print(f"File Names: {f.namelist()}")
            file_name = f.namelist()[0]
            f.extractall(self.extract_to_folder)
        #file.extractall(extract_to_folder)
        #os.remove(temp_file_path)
        #os.rmdir(temp_dir)
        try:
            print("Trying to remove the temporary zipfile and folder")
            temp_file_path.unlink()
            temp_dir.unlink()
        except Exception as e:
            print("Failed to remove the temporary content", e)

        zip_file_path = self.extract_to_folder.joinpath(file_name)#os.path.abspath(os.path.join(self.extract_to_folder, file_name))
        print(f"The file was successfully extracted to {zip_file_path}")
        
        return zip_file_path


