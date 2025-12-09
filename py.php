<?php
header("Content-type: text/html; charset=utf-8");

$timeVar = $_POST['time'];
$email = $_POST['email'];

// 记录日志
$log_file = "logs/py_php_debug.log";
if (!file_exists("logs")) {
    mkdir("logs", 0777, true);
}

file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "py.php called with email=$email, timeVar=$timeVar\n", FILE_APPEND);

// 执行命令并捕获输出
// 使用引号包裹参数，确保空字符串也能正确传递
$command = "bash EDM.sh '".$email."' '".$timeVar."' 2>&1";
exec($command, $output, $return_code);

// 记录执行结果
file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Command: $command\n", FILE_APPEND);
file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Return code: $return_code\n", FILE_APPEND);
file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Output: " . implode("\n", $output) . "\n", FILE_APPEND);
file_put_contents($log_file, str_repeat("=", 60) . "\n", FILE_APPEND);

// 返回响应给AJAX
if ($return_code === 0) {
    echo "SUCCESS: Task $timeVar started";
} else {
    echo "ERROR: Failed to start task $timeVar (return code: $return_code)";
}
?>
