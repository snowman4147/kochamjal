import os
from watchdog.events import FileSystemEventHandler
from utils import preprocess_logger


class TDMSHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        detected_file_name = os.path.basename(event.src_path).split('.')[0]
        detected_file_extension = event.src_path.split('.')[-1]
        watch_dir = os.path.dirname(event.src_path)
        if detected_file_extension not in ['tdms', 'tdms_index']:
            preprocess_logger.warning(f'Unnecessary file detected: {detected_file_name}.{detected_file_extension}')
            return None
        preprocess_logger.info(f'File detected: {detected_file_name}.{detected_file_extension}')
        related_file = os.path.join(
            watch_dir,
            f'{detected_file_name}.{"tdms_index" if detected_file_extension == "tdms" else "tdms"}'
        )
        if os.path.exists(related_file):
            preprocess_logger.info(f'Both TDMS and Index files detected for {detected_file_name}')
        else:
            preprocess_logger.warning(
                f'Waiting for {"Index" if detected_file_extension == "tdms" else "TDMS"} file '
                f'for {detected_file_name}.{detected_file_extension}'
            )
            return None
