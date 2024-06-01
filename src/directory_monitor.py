import cmd
import datetime
import os
import threading
from watchdog.observers import Observer
from tdms_handler import TDMSHandler
from utils import preprocess_logger

ascii_art = """
    +----------------------------------------------------------------+
    |   _   __              _                          _         _   |
    |  | | / /             | |                        (_)       | |  |
    |  | |/ /   ___    ___ | |__    __ _  _ __ ___     _   __ _ | |  |
    |  |    \  / _ \  / __|| '_ \  / _` || '_ ` _ \   | | / _` || |  |
    |  | |\  \| (_) || (__ | | | || (_| || | | | | |  | || (_| || |  |
    |  \_| \_/ \___/  \___||_| |_| \__,_||_| |_| |_|  | | \__,_||_|  |
    |                                               _/ |             |
    |                                              |__/              |
    +----------------------------------------------------------------+
"""


class DirectoryMonitor(cmd.Cmd):
    intro = ascii_art + (
        """
    Welcome to the CNC Data Analysis Monitor.
    collects real-time data and provides predictions through machine learning models.
    Type help or ? to list commands.
        """
    )
    prompt = '(command): '
    observer = None

    def __init__(self):
        super().__init__()
        self.path = None
        self.event_handler = TDMSHandler()
        self.observer_thread = None

    def do_help(self, arg):
        if arg:
            try:
                func = getattr(self, 'do_' + arg)
                print(func.__doc__)
            except AttributeError:
                print(f'No help available for {arg}')
        else:
            print(
                """
    This program monitors and analyzes TDMS data generated during CNC machine operations.
    Utilizing PyTorch, it enables users to implement custom datasets, models, and preprocessing steps.
    After machining operations, users can view real-time predictions based on the data processed by their models.
    
    Commands:
      setdir <path>  : Set the directory to monitor for new TDMS files.
      start          : Start monitoring the set directory.
      stop           : Stop monitoring the directory.
      clr            : Clear the screen and display the logo and welcome message.
      exit           : Stop monitoring (if active) and exit the program.
      help or ?      : Show this help message.
      
    For detailed information about a command, type ?<command>
                """
            )

    def do_setdir(self, arg):
        """
    Set the directory that will be monitored for new TDMS files.
    You must specify a valid directory path. If the directory is not valid
    or does not exist, an error message will be displayed.
    If no path is provided, the current working directory will be set as the monitoring directory.
    Use the 'ls' command to list the contents of the current directory for reference.

    Example usage:
        setdir C:\\Users\\User\\Documents\\CNCData
        setdir  # This will set the current working directory
        """
        path = arg.strip() if arg else os.getcwd()
        if not os.path.isdir(path):
            preprocess_logger.error(f'Invalid directory: {path}')
        else:
            self.path = path
            preprocess_logger.info(f'Set directory to {path}')
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None

    def do_start(self, arg):
        """
    Start monitoring the directory that was set using the 'setdir' command.
    You must set the directory to monitor first before using this command.

    Example usage:
        start
        """
        if not self.path:
            preprocess_logger.error('No directory set. Use set_dir to set the directory to monitor.')
            return None
        if self.observer:
            preprocess_logger.error('Observer is already running.')
            return None
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        self.observer_thread = threading.Thread(target=self.observer.start, daemon=True)
        self.observer_thread.start()
        preprocess_logger.info(f'Starting directory monitoring on: {self.path}')

    def do_stop(self, arg):
        """
    Stop monitoring the directory if monitoring is currently active.
    If no monitoring is active, an error message will be displayed.

    Example usage:
        stop
        """
        if not self.observer:
            preprocess_logger.error('Observer is not running.')
            return None
        self.observer.stop()
        preprocess_logger.warning('Stopped directory monitoring')
        self.observer.join()
        preprocess_logger.info('Observer has been successfully stopped and joined')
        self.observer = None

    def do_exit(self, arg):
        """
    Stop the directory monitoring (if active) and exit the program.

    Example usage:
        exit
        """
        if self.observer:
            self.observer.stop()
            preprocess_logger.warning('Stopped directory monitoring')
            self.observer.join()
            preprocess_logger.info('Observer has been successfully stopped and joined')
        preprocess_logger.info('Exiting the CNC Data Analysis Monitor')
        return True

    def do_clr(self, arg):
        """
    Clear the terminal screen and redisplay the logo and welcome message.

    Example usage:
        clr
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.intro)

    def do_ls(self, arg):
        """
    List the contents of the current directory with details.
    If a path is specified, list the contents of the specified directory.
    The current directory is displayed at the top.

    Example usage:
        ls
        ls C:\\Users\\User\\Documents
        """
        path = arg.strip() if arg else os.getcwd()
        if os.path.isdir(path):
            print(f'Directory: {os.path.abspath(path)}')
            try:
                with os.scandir(path) as entries:
                    for entry in entries:
                        info = entry.stat()
                        size = info.st_size
                        mtime = datetime.datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        is_dir = '<DIR>' if entry.is_dir() else ''
                        print(f'{mtime} {is_dir:5} {size:10} {entry.name}')
            except PermissionError:
                preprocess_logger.error(f'Access denied: {path}')
        else:
            preprocess_logger.error(f'Invalid directory: {path}')

    def do_cd(self, arg):
        """
    Change the current directory.

    Example usage:
        cd C:\\Users\\User\\Documents
        """
        path = arg.strip()
        if os.path.isdir(path):
            os.chdir(path)
            print(f'Changed directory to {path}')
        else:
            preprocess_logger.error(f'Invalid directory: {path}')
