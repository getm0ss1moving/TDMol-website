<?php
/**
 * monitor.php - 实时监控页面
 * 查看系统运行状态和日志
 */

// 自动刷新间隔（秒）
$refresh_interval = isset($_GET['refresh']) ? intval($_GET['refresh']) : 10;
?>
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>EDM 系统监控</title>
    <?php if ($refresh_interval > 0): ?>
    <meta http-equiv="refresh" content="<?php echo $refresh_interval; ?>">
    <?php endif; ?>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }
        h2 {
            color: #569cd6;
            margin-top: 30px;
        }
        .section {
            background-color: #252526;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #007acc;
        }
        .log-viewer {
            background-color: #1e1e1e;
            border: 1px solid #3c3c3c;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.5;
        }
        .log-line {
            margin: 2px 0;
            padding: 2px 5px;
        }
        .log-info { color: #4ec9b0; }
        .log-success { color: #4ec9b0; font-weight: bold; }
        .log-warning { color: #dcdcaa; }
        .log-error { color: #f48771; font-weight: bold; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background-color: #252526;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #4ec9b0;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #4ec9b0;
        }
        .stat-label {
            color: #858585;
            font-size: 14px;
        }
        .controls {
            background-color: #252526;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        button {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            cursor: pointer;
            border-radius: 3px;
        }
        button:hover {
            background-color: #1177bb;
        }
        .timestamp {
            color: #858585;
            font-size: 12px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #252526;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #3c3c3c;
        }
        th {
            background-color: #2d2d30;
            color: #4ec9b0;
        }
        a {
            color: #569cd6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 EDM 系统监控面板</h1>

        <div class="controls">
            <span class="timestamp">最后更新: <?php echo date('Y-m-d H:i:s'); ?></span>
            &nbsp;|&nbsp;
            自动刷新:
            <button onclick="location.href='?refresh=5'">5秒</button>
            <button onclick="location.href='?refresh=10'">10秒</button>
            <button onclick="location.href='?refresh=30'">30秒</button>
            <button onclick="location.href='?refresh=0'">关闭</button>
            &nbsp;|&nbsp;
            <button onclick="location.reload()">手动刷新</button>
            <button onclick="location.href='test_workflow.php'">测试工具</button>
        </div>

        <!-- 统计信息 -->
        <h2>📈 系统统计</h2>
        <div class="stats">
            <?php
            $upload_count = count(glob('upload/*.txt'));
            $result_count = count(glob('result/*_brief.html'));
            $log_exists = file_exists('logs/edm_debug.log');
            $log_size = $log_exists ? filesize('logs/edm_debug.log') : 0;
            ?>
            <div class="stat-box">
                <div class="stat-number"><?php echo $upload_count; ?></div>
                <div class="stat-label">上传文件总数</div>
            </div>
            <div class="stat-box">
                <div class="stat-number"><?php echo $result_count; ?></div>
                <div class="stat-label">完成任务数</div>
            </div>
            <div class="stat-box">
                <div class="stat-number"><?php echo round($log_size / 1024, 1); ?> KB</div>
                <div class="stat-label">日志文件大小</div>
            </div>
            <div class="stat-box">
                <div class="stat-number"><?php echo $result_count > 0 ? round(($result_count / $upload_count) * 100, 1) : 0; ?>%</div>
                <div class="stat-label">任务完成率</div>
            </div>
        </div>

        <!-- 最近的任务 -->
        <h2>📝 最近的任务</h2>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>任务ID</th>
                        <th>提交时间</th>
                        <th>输入文件</th>
                        <th>结果</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                    $upload_files = glob('upload/*.txt');
                    arsort($upload_files);
                    $recent = array_slice($upload_files, 0, 10);

                    foreach ($recent as $file) {
                        $task_id = basename($file, '.txt');
                        $mtime = filemtime($file);
                        $result_file = "result/{$task_id}_brief.html";
                        $has_result = file_exists($result_file);

                        echo "<tr>";
                        echo "<td><code>$task_id</code></td>";
                        echo "<td>" . date('Y-m-d H:i:s', $mtime) . "</td>";
                        echo "<td>" . round(filesize($file) / 1024, 2) . " KB</td>";
                        if ($has_result) {
                            echo "<td><a href='$result_file' target='_blank'>查看结果</a></td>";
                            echo "<td style='color:#4ec9b0;'>✓ 完成</td>";
                        } else {
                            echo "<td>-</td>";
                            echo "<td style='color:#dcdcaa;'>⏳ 处理中</td>";
                        }
                        echo "</tr>";
                    }
                    ?>
                </tbody>
            </table>
        </div>

        <!-- 实时日志 -->
        <h2>📜 实时日志 (最后50行)</h2>
        <div class="section">
            <div class="log-viewer">
                <?php
                $log_file = 'logs/edm_debug.log';
                if (file_exists($log_file)) {
                    $content = file_get_contents($log_file);
                    $lines = explode("\n", $content);
                    $recent_lines = array_slice($lines, -50);

                    foreach ($recent_lines as $line) {
                        if (empty(trim($line))) continue;

                        $class = 'log-info';
                        if (strpos($line, '[ERROR]') !== false) {
                            $class = 'log-error';
                        } elseif (strpos($line, '[SUCCESS]') !== false) {
                            $class = 'log-success';
                        } elseif (strpos($line, '[WARNING]') !== false) {
                            $class = 'log-warning';
                        }

                        echo "<div class='log-line $class'>" . htmlspecialchars($line) . "</div>";
                    }
                } else {
                    echo "<div class='log-line log-warning'>日志文件不存在: $log_file</div>";
                }
                ?>
            </div>
        </div>

        <!-- 系统信息 -->
        <h2>ℹ️ 系统信息</h2>
        <div class="section">
            <table>
                <tr>
                    <th>项目</th>
                    <th>值</th>
                </tr>
                <tr>
                    <td>PHP版本</td>
                    <td><?php echo phpversion(); ?></td>
                </tr>
                <tr>
                    <td>Python版本</td>
                    <td><?php echo shell_exec('python3 --version 2>&1'); ?></td>
                </tr>
                <tr>
                    <td>当前时间</td>
                    <td><?php echo date('Y-m-d H:i:s'); ?></td>
                </tr>
                <tr>
                    <td>Upload目录权限</td>
                    <td><?php echo is_writable('upload') ? '<span style="color:#4ec9b0;">✓ 可写</span>' : '<span style="color:#f48771;">✗ 不可写</span>'; ?></td>
                </tr>
                <tr>
                    <td>Result目录权限</td>
                    <td><?php echo is_writable('result') ? '<span style="color:#4ec9b0;">✓ 可写</span>' : '<span style="color:#f48771;">✗ 不可写</span>'; ?></td>
                </tr>
            </table>
        </div>

    </div>

    <script>
    // 自动滚动到日志底部
    window.onload = function() {
        var logViewer = document.querySelector('.log-viewer');
        if (logViewer) {
            logViewer.scrollTop = logViewer.scrollHeight;
        }
    }
    </script>
</body>
</html>
