#!/usr/bin/env python3
"""
cleanup_old_tasks.py - Automatically clean up old task files
Removes files from upload and result directories that are older than 3 days
"""

import os
import time
import shutil
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cleanup.log'),
        logging.StreamHandler()
    ]
)

# Directories to clean
UPLOAD_DIR = "/var/www/bioinf/TDMol/upload/"
RESULT_DIR = "/var/www/bioinf/TDMol/result/"

# Maximum age in days
MAX_AGE_DAYS = 3
MAX_AGE_SECONDS = MAX_AGE_DAYS * 24 * 60 * 60

def cleanup_directory(directory, max_age_seconds):
    """
    Clean up files and directories older than max_age_seconds

    Args:
        directory: Path to directory to clean
        max_age_seconds: Maximum age in seconds

    Returns:
        Tuple of (files_deleted, dirs_deleted, space_freed)
    """
    if not os.path.exists(directory):
        logging.warning(f"Directory does not exist: {directory}")
        return 0, 0, 0

    current_time = time.time()
    cutoff_time = current_time - max_age_seconds

    files_deleted = 0
    dirs_deleted = 0
    space_freed = 0

    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            try:
                # Get modification time
                mtime = os.path.getmtime(item_path)

                # Check if older than cutoff
                if mtime < cutoff_time:
                    item_age_days = (current_time - mtime) / (24 * 60 * 60)

                    if os.path.isfile(item_path):
                        # Delete file
                        file_size = os.path.getsize(item_path)
                        os.remove(item_path)
                        files_deleted += 1
                        space_freed += file_size
                        logging.info(f"Deleted file: {item_path} (age: {item_age_days:.1f} days, size: {file_size} bytes)")

                    elif os.path.isdir(item_path):
                        # Delete directory and all contents
                        dir_size = get_directory_size(item_path)
                        shutil.rmtree(item_path)
                        dirs_deleted += 1
                        space_freed += dir_size
                        logging.info(f"Deleted directory: {item_path} (age: {item_age_days:.1f} days, size: {dir_size} bytes)")

            except Exception as e:
                logging.error(f"Error processing {item_path}: {e}")
                continue

    except Exception as e:
        logging.error(f"Error scanning directory {directory}: {e}")

    return files_deleted, dirs_deleted, space_freed

def get_directory_size(directory):
    """Calculate total size of directory and all its contents"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total_size

def format_bytes(bytes):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def main():
    logging.info("="*60)
    logging.info("Starting cleanup process")
    logging.info(f"Maximum file age: {MAX_AGE_DAYS} days")
    logging.info("="*60)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    total_files = 0
    total_dirs = 0
    total_space = 0

    # Clean upload directory
    logging.info(f"\nCleaning upload directory: {UPLOAD_DIR}")
    files, dirs, space = cleanup_directory(UPLOAD_DIR, MAX_AGE_SECONDS)
    total_files += files
    total_dirs += dirs
    total_space += space
    logging.info(f"Upload cleanup: {files} files, {dirs} directories, {format_bytes(space)} freed")

    # Clean result directory
    logging.info(f"\nCleaning result directory: {RESULT_DIR}")
    files, dirs, space = cleanup_directory(RESULT_DIR, MAX_AGE_SECONDS)
    total_files += files
    total_dirs += dirs
    total_space += space
    logging.info(f"Result cleanup: {files} files, {dirs} directories, {format_bytes(space)} freed")

    # Summary
    logging.info("\n" + "="*60)
    logging.info("Cleanup completed")
    logging.info(f"Total files deleted: {total_files}")
    logging.info(f"Total directories deleted: {total_dirs}")
    logging.info(f"Total space freed: {format_bytes(total_space)}")
    logging.info("="*60)

if __name__ == "__main__":
    main()
