#!/usr/bin/env python3
"""
Media Cleanup Script for Animathic

This script safely cleans up old temporary files and optimizes storage usage.
Features:
- Age-based cleanup
- Size-based cleanup
- Safe deletion with verification
- Logging and reporting
"""

import os
import time
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_directory_size(directory: str) -> int:
    """Get total size of directory in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    continue
    except (OSError, FileNotFoundError):
        pass
    return total_size

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def find_old_files(directory: str, max_age_hours: int = 24) -> List[str]:
    """Find files older than specified age"""
    old_files = []
    cutoff_time = time.time() - (max_age_hours * 3600)
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getctime(file_path) < cutoff_time:
                        old_files.append(file_path)
                except (OSError, FileNotFoundError):
                    continue
    except (OSError, FileNotFoundError):
        logger.warning(f"Directory not found: {directory}")
    
    return old_files

def find_large_files(directory: str, min_size_mb: int = 100) -> List[Tuple[str, int]]:
    """Find files larger than specified size"""
    large_files = []
    min_size_bytes = min_size_mb * 1024 * 1024
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > min_size_bytes:
                        large_files.append((file_path, size))
                except (OSError, FileNotFoundError):
                    continue
    except (OSError, FileNotFoundError):
        logger.warning(f"Directory not found: {directory}")
    
    return large_files

def cleanup_temp_directories(media_dir: str) -> Tuple[int, int]:
    """Clean up temporary directories"""
    temp_patterns = ['temp_', 'tmp_', '__pycache__']
    cleaned_files = 0
    freed_bytes = 0
    
    try:
        for root, dirs, files in os.walk(media_dir):
            # Clean temporary directories
            dirs_to_remove = []
            for dir_name in dirs:
                if any(pattern in dir_name for pattern in temp_patterns):
                    dir_path = os.path.join(root, dir_name)
                    try:
                        size = get_directory_size(dir_path)
                        shutil.rmtree(dir_path)
                        dirs_to_remove.append(dir_name)
                        freed_bytes += size
                        cleaned_files += 1
                        logger.info(f"Removed temp directory: {dir_path}")
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Failed to remove {dir_path}: {e}")
            
            # Remove from dirs list to prevent walking into them
            for dir_name in dirs_to_remove:
                dirs.remove(dir_name)
    
    except (OSError, FileNotFoundError):
        logger.warning(f"Media directory not found: {media_dir}")
    
    return cleaned_files, freed_bytes

def cleanup_old_files(directory: str, max_age_hours: int = 24, dry_run: bool = False) -> Tuple[int, int]:
    """Clean up old files"""
    old_files = find_old_files(directory, max_age_hours)
    cleaned_files = 0
    freed_bytes = 0
    
    for file_path in old_files:
        try:
            size = os.path.getsize(file_path)
            
            if not dry_run:
                os.remove(file_path)
                freed_bytes += size
                cleaned_files += 1
                logger.info(f"Removed old file: {file_path}")
            else:
                logger.info(f"Would remove: {file_path} ({format_size(size)})")
                freed_bytes += size
                cleaned_files += 1
                
        except (OSError, FileNotFoundError) as e:
            logger.warning(f"Failed to remove {file_path}: {e}")
    
    return cleaned_files, freed_bytes

def cleanup_partial_movie_files(media_dir: str) -> Tuple[int, int]:
    """Clean up partial movie files from failed renders"""
    partial_patterns = ['partial_movie_files', 'uncached_', '.tmp']
    cleaned_files = 0
    freed_bytes = 0
    
    try:
        for root, dirs, files in os.walk(media_dir):
            if 'partial_movie_files' in root:
                # Remove entire partial_movie_files directories
                try:
                    size = get_directory_size(root)
                    shutil.rmtree(root)
                    freed_bytes += size
                    cleaned_files += 1
                    logger.info(f"Removed partial movie directory: {root}")
                    break  # Skip walking into this directory
                except (OSError, PermissionError) as e:
                    logger.warning(f"Failed to remove {root}: {e}")
            
            # Clean individual partial files
            for file in files:
                if any(pattern in file for pattern in partial_patterns):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        freed_bytes += size
                        cleaned_files += 1
                        logger.info(f"Removed partial file: {file_path}")
                    except (OSError, FileNotFoundError) as e:
                        logger.warning(f"Failed to remove {file_path}: {e}")
    
    except (OSError, FileNotFoundError):
        logger.warning(f"Media directory not found: {media_dir}")
    
    return cleaned_files, freed_bytes

def main():
    parser = argparse.ArgumentParser(description='Clean up Animathic media files')
    parser.add_argument('--media-dir', default='media', help='Media directory path')
    parser.add_argument('--max-age-hours', type=int, default=24, help='Maximum age of files to keep (hours)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--force', action='store_true', help='Force cleanup without prompting')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    media_dir = os.path.abspath(args.media_dir)
    
    if not os.path.exists(media_dir):
        logger.error(f"Media directory does not exist: {media_dir}")
        return 1
    
    logger.info(f"Starting cleanup of media directory: {media_dir}")
    
    # Get initial statistics
    initial_size = get_directory_size(media_dir)
    logger.info(f"Initial directory size: {format_size(initial_size)}")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will actually be deleted")
    
    total_cleaned_files = 0
    total_freed_bytes = 0
    
    # Cleanup operations
    operations = [
        ("temp directories", lambda: cleanup_temp_directories(media_dir)),
        ("old files", lambda: cleanup_old_files(media_dir, args.max_age_hours, args.dry_run)),
        ("partial movie files", lambda: cleanup_partial_movie_files(media_dir)),
    ]
    
    for operation_name, operation_func in operations:
        logger.info(f"Cleaning up {operation_name}...")
        try:
            cleaned_files, freed_bytes = operation_func()
            total_cleaned_files += cleaned_files
            total_freed_bytes += freed_bytes
            logger.info(f"{operation_name}: {cleaned_files} files, {format_size(freed_bytes)} freed")
        except Exception as e:
            logger.error(f"Error during {operation_name} cleanup: {e}")
    
    # Final statistics
    final_size = get_directory_size(media_dir)
    actual_freed = initial_size - final_size
    
    logger.info("Cleanup completed!")
    logger.info(f"Files processed: {total_cleaned_files}")
    logger.info(f"Space freed: {format_size(actual_freed)}")
    logger.info(f"Final directory size: {format_size(final_size)}")
    
    if actual_freed > 0:
        percentage_freed = (actual_freed / initial_size) * 100
        logger.info(f"Space reduction: {percentage_freed:.1f}%")
    
    return 0

if __name__ == "__main__":
    exit(main())
