<?php
/**
 * cleanup_trigger.php - Web-based cleanup trigger
 * This can be called periodically by a cron job or accessed via web
 * to trigger cleanup of old files
 */

// Security: Only allow access from localhost or add authentication here
$allowed_ips = array('127.0.0.1', '::1');
if (!in_array($_SERVER['REMOTE_ADDR'], $allowed_ips)) {
    // For production, you may want to add token-based authentication
    // Uncomment the lines below to enable token authentication
    // $valid_token = "your_secret_token_here";
    // if (!isset($_GET['token']) || $_GET['token'] !== $valid_token) {
    //     die("Access denied");
    // }
}

header('Content-Type: text/plain');

echo "EDM Task Cleanup Script\n";
echo "======================\n\n";

// Configuration
$max_age_days = 3;
$max_age_seconds = $max_age_days * 24 * 60 * 60;

$upload_dir = "/var/www/bioinf/TDMol/upload/";
$result_dir = "/var/www/bioinf/TDMol/result/";

// Function to cleanup directory
function cleanup_directory($directory, $max_age_seconds) {
    if (!is_dir($directory)) {
        echo "Warning: Directory does not exist: $directory\n";
        return array('files' => 0, 'dirs' => 0, 'space' => 0);
    }

    $current_time = time();
    $cutoff_time = $current_time - $max_age_seconds;

    $files_deleted = 0;
    $dirs_deleted = 0;
    $space_freed = 0;

    $items = scandir($directory);
    foreach ($items as $item) {
        if ($item == '.' || $item == '..') {
            continue;
        }

        $item_path = $directory . $item;

        // Get modification time
        $mtime = filemtime($item_path);

        // Check if older than cutoff
        if ($mtime < $cutoff_time) {
            $age_days = ($current_time - $mtime) / (24 * 60 * 60);

            if (is_file($item_path)) {
                // Delete file
                $file_size = filesize($item_path);
                if (unlink($item_path)) {
                    $files_deleted++;
                    $space_freed += $file_size;
                    echo "Deleted file: $item_path (age: " . number_format($age_days, 1) . " days)\n";
                }
            } elseif (is_dir($item_path)) {
                // Delete directory
                $dir_size = get_directory_size($item_path);
                if (delete_directory($item_path)) {
                    $dirs_deleted++;
                    $space_freed += $dir_size;
                    echo "Deleted directory: $item_path (age: " . number_format($age_days, 1) . " days)\n";
                }
            }
        }
    }

    return array(
        'files' => $files_deleted,
        'dirs' => $dirs_deleted,
        'space' => $space_freed
    );
}

// Function to get directory size
function get_directory_size($directory) {
    $size = 0;
    if (is_dir($directory)) {
        foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($directory, FilesystemIterator::SKIP_DOTS)) as $file) {
            $size += $file->getSize();
        }
    }
    return $size;
}

// Function to delete directory recursively
function delete_directory($directory) {
    if (!is_dir($directory)) {
        return false;
    }

    $items = scandir($directory);
    foreach ($items as $item) {
        if ($item == '.' || $item == '..') {
            continue;
        }

        $item_path = $directory . '/' . $item;

        if (is_dir($item_path)) {
            delete_directory($item_path);
        } else {
            unlink($item_path);
        }
    }

    return rmdir($directory);
}

// Function to format bytes
function format_bytes($bytes) {
    $units = array('B', 'KB', 'MB', 'GB', 'TB');
    $bytes = max($bytes, 0);
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
    $pow = min($pow, count($units) - 1);
    $bytes /= pow(1024, $pow);
    return round($bytes, 2) . ' ' . $units[$pow];
}

// Main cleanup process
echo "Starting cleanup process at " . date('Y-m-d H:i:s') . "\n";
echo "Maximum file age: $max_age_days days\n\n";

$total_files = 0;
$total_dirs = 0;
$total_space = 0;

// Clean upload directory
echo "Cleaning upload directory: $upload_dir\n";
$result = cleanup_directory($upload_dir, $max_age_seconds);
$total_files += $result['files'];
$total_dirs += $result['dirs'];
$total_space += $result['space'];
echo "Upload cleanup: {$result['files']} files, {$result['dirs']} directories, " . format_bytes($result['space']) . " freed\n\n";

// Clean result directory
echo "Cleaning result directory: $result_dir\n";
$result = cleanup_directory($result_dir, $max_age_seconds);
$total_files += $result['files'];
$total_dirs += $result['dirs'];
$total_space += $result['space'];
echo "Result cleanup: {$result['files']} files, {$result['dirs']} directories, " . format_bytes($result['space']) . " freed\n\n";

// Summary
echo "======================\n";
echo "Cleanup completed at " . date('Y-m-d H:i:s') . "\n";
echo "Total files deleted: $total_files\n";
echo "Total directories deleted: $total_dirs\n";
echo "Total space freed: " . format_bytes($total_space) . "\n";
echo "======================\n";
?>
