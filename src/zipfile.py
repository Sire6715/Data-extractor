import zipfile
import logging

logger = logging.getLogger(__name__)

class ZipFile(zipfile.ZipFile):
    """
    Extended ZIP archive handler for CSV extraction.
    """
    
    def infolist(self):
        """
        Return all members inside the ZIP archive.
        
        Used to locate the CSV member dynamically.
        
        Args:
            None
        
        Returns:
            list: List of ZipInfo objects for all members in the archive.
        
        Raises:
            zipfile.BadZipFile: If the ZIP archive is corrupt or unreadable.
        """
        try:
            return [info for info in super().infolist()]
        
        except zipfile.BadZipFile:
            logger.exception("Zip archive is corrupt or unreadable.")
            raise


    def open(self, member, mode="r", pwd=None):
        """
        Open a member file within the ZIP archive.
        
        Args:
            member: Name or ZipInfo object of the member to open.
            mode: Mode to open the file ('r' for read, default: 'r').
            pwd: Password for encrypted ZIP files (default: None).
        
        Returns:
            file-like object: Opened member file.
        
        Raises:
            KeyError: If the specified member is not found in the archive.
            zipfile.BadZipFile: If the ZIP archive is corrupt while opening.
        """
        try:
            return super().open(member, mode=mode, pwd=pwd)
        
        except KeyError:
            logger.exception("Zip member not found: %s", member)
            raise
        
        except zipfile.BadZipFile:
            logger.exception(
                "Zip archive is corrupt while opening member."
            )
            raise