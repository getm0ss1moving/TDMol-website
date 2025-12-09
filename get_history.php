<?php
/**
 * Get history of completed tasks
 * Returns JSON array of task history
 */

header('Content-Type: application/json');

$result_dir = "/var/www/bioinf/TDMol/result/";
$history = array();

// Check if result directory exists
if (!is_dir($result_dir)) {
    echo json_encode(array('success' => false, 'message' => 'Result directory not found', 'data' => array()));
    exit;
}

// Scan result directory for task folders
$task_folders = array_diff(scandir($result_dir), array('.', '..'));

foreach ($task_folders as $task_id) {
    $task_path = $result_dir . $task_id;

    // Check if it's a directory
    if (!is_dir($task_path)) {
        continue;
    }

    // Check if brief.html exists
    $brief_file = $task_path . "/brief.html";
    if (!file_exists($brief_file)) {
        continue;
    }

    // Get task metadata
    $summary_file = $task_path . "/summary.json";
    $user_input = "N/A";
    $num_molecules = 0;

    if (file_exists($summary_file)) {
        $summary_data = json_decode(file_get_contents($summary_file), true);
        if ($summary_data) {
            $user_input = isset($summary_data['user_input']) ? $summary_data['user_input'] : 'N/A';
            $num_molecules = isset($summary_data['results']) ? count($summary_data['results']) : 0;
        }
    }

    // Get creation time
    $created_time = filemtime($task_path);

    $history[] = array(
        'task_id' => $task_id,
        'url' => "/bioinf/TDMol/result/" . $task_id . "/brief.html",
        'user_input' => $user_input,
        'num_molecules' => $num_molecules,
        'created_time' => $created_time,
        'created_date' => date('Y-m-d H:i:s', $created_time)
    );
}

// Sort by creation time (newest first)
usort($history, function($a, $b) {
    return $b['created_time'] - $a['created_time'];
});

echo json_encode(array('success' => true, 'data' => $history));
?>
