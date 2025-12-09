<?php
/**
 * test_workflow.php - 测试工作流程
 * 访问这个页面可以测试整个系统的各个环节
 */
?>
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>EDM Workflow Test</title>
    <style>
        body { font-family: Arial; padding: 20px; background-color: #f5f5f5; }
        .test-section { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .info { color: blue; }
        pre { background: #f0f0f0; padding: 10px; overflow-x: auto; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>EDM 工作流程测试</h1>

    <div class="test-section">
        <h2>1. 检查前端文件</h2>
        <?php
        $frontend_files = [
            'index.html',
            'EDM.php',
            'py.php',
            'EDM_frontend.sh',
            'EDM_server.py',
            'upload/',
            'result/'
        ];

        foreach ($frontend_files as $file) {
            if (file_exists($file)) {
                echo "<p class='success'>✓ $file 存在</p>";
                if (is_dir($file)) {
                    echo "<p class='info'>  - 目录权限: " . substr(sprintf('%o', fileperms($file)), -4) . "</p>";
                } else {
                    echo "<p class='info'>  - 文件大小: " . filesize($file) . " bytes</p>";
                }
            } else {
                echo "<p class='error'>✗ $file 不存在</p>";
            }
        }
        ?>
    </div>

    <div class="test-section">
        <h2>2. 检查目录权限</h2>
        <?php
        $dirs = ['upload', 'result'];
        foreach ($dirs as $dir) {
            if (is_writable($dir)) {
                echo "<p class='success'>✓ $dir 目录可写</p>";
            } else {
                echo "<p class='error'>✗ $dir 目录不可写</p>";
            }
        }
        ?>
    </div>

    <div class="test-section">
        <h2>3. 测试文件写入</h2>
        <?php
        $test_file = 'upload/test_' . time() . '.txt';
        $test_content = 'This is a test file created at ' . date('Y-m-d H:i:s');

        if (file_put_contents($test_file, $test_content)) {
            echo "<p class='success'>✓ 成功写入测试文件: $test_file</p>";
            echo "<p class='info'>  - 内容: $test_content</p>";

            // 清理测试文件
            unlink($test_file);
            echo "<p class='info'>  - 测试文件已删除</p>";
        } else {
            echo "<p class='error'>✗ 无法写入测试文件</p>";
        }
        ?>
    </div>

    <div class="test-section">
        <h2>4. 检查PHP函数</h2>
        <?php
        $functions = ['exec', 'shell_exec', 'file_get_contents', 'file_put_contents'];
        foreach ($functions as $func) {
            if (function_exists($func)) {
                echo "<p class='success'>✓ $func() 可用</p>";
            } else {
                echo "<p class='error'>✗ $func() 不可用 (可能被disable_functions禁用)</p>";
            }
        }
        ?>
    </div>

    <div class="test-section">
        <h2>5. 测试Python</h2>
        <?php
        $python_test = shell_exec('python3 --version 2>&1');
        if ($python_test) {
            echo "<p class='success'>✓ Python3 可用</p>";
            echo "<pre>$python_test</pre>";
        } else {
            echo "<p class='error'>✗ Python3 不可用</p>";
        }
        ?>
    </div>

    <div class="test-section">
        <h2>6. 测试Bash脚本</h2>
        <?php
        if (file_exists('EDM_frontend.sh')) {
            $perms = substr(sprintf('%o', fileperms('EDM_frontend.sh')), -4);
            echo "<p class='info'>EDM_frontend.sh 权限: $perms</p>";

            if (is_executable('EDM_frontend.sh')) {
                echo "<p class='success'>✓ EDM_frontend.sh 可执行</p>";
            } else {
                echo "<p class='error'>✗ EDM_frontend.sh 不可执行</p>";
                echo "<p class='info'>运行: chmod +x EDM_frontend.sh</p>";
            }
        }
        ?>
    </div>

    <div class="test-section">
        <h2>7. 查看最近的任务</h2>
        <?php
        $upload_files = glob('upload/*.txt');
        $result_files = glob('result/*_brief.html');

        echo "<h3>上传文件 (" . count($upload_files) . "):</h3>";
        if ($upload_files) {
            arsort($upload_files);
            $recent_uploads = array_slice($upload_files, 0, 5);
            echo "<ul>";
            foreach ($recent_uploads as $file) {
                $mtime = filemtime($file);
                echo "<li>" . basename($file) . " - " . date('Y-m-d H:i:s', $mtime) . "</li>";
            }
            echo "</ul>";
        } else {
            echo "<p>没有上传文件</p>";
        }

        echo "<h3>结果文件 (" . count($result_files) . "):</h3>";
        if ($result_files) {
            arsort($result_files);
            $recent_results = array_slice($result_files, 0, 5);
            echo "<ul>";
            foreach ($recent_results as $file) {
                $mtime = filemtime($file);
                echo "<li><a href='$file' target='_blank'>" . basename($file) . "</a> - " . date('Y-m-d H:i:s', $mtime) . "</li>";
            }
            echo "</ul>";
        } else {
            echo "<p>没有结果文件</p>";
        }
        ?>
    </div>

    <div class="test-section">
        <h2>8. 模拟提交测试</h2>
        <button onclick="testSubmit()">模拟提交任务</button>
        <div id="test-result"></div>
    </div>

    <script>
    function testSubmit() {
        var resultDiv = document.getElementById('test-result');
        resultDiv.innerHTML = '<p style="color:blue;">正在测试...</p>';

        var formData = new FormData();
        formData.append('user_text', 'Test molecule: benzene ring with hydroxyl groups');
        formData.append('email', 'test@example.com');

        fetch('EDM.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            resultDiv.innerHTML = '<p style="color:green;">✓ 提交成功！请检查upload目录是否有新文件</p>';
            // 提取task_id
            var match = data.match(/timeVar="(\d+)"/);
            if (match) {
                resultDiv.innerHTML += '<p>Task ID: ' + match[1] + '</p>';
                resultDiv.innerHTML += '<p>预期文件: upload/' + match[1] + '.txt</p>';
            }
        })
        .catch(error => {
            resultDiv.innerHTML = '<p style="color:red;">✗ 提交失败: ' + error + '</p>';
        });
    }
    </script>

    <div class="test-section">
        <h2>9. 查看日志文件</h2>
        <?php
        $log_files = ['logs/edm_debug.log', 'logs/edm_error.log'];
        foreach ($log_files as $log) {
            if (file_exists($log)) {
                echo "<h3>$log</h3>";
                $content = file_get_contents($log);
                $lines = explode("\n", $content);
                $recent = array_slice($lines, -20); // 最后20行
                echo "<pre>" . htmlspecialchars(implode("\n", $recent)) . "</pre>";
            } else {
                echo "<p class='info'>日志文件 $log 不存在</p>";
            }
        }
        ?>
    </div>

</body>
</html>
