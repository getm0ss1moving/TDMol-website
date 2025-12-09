<?php

if($_POST["email"]==""){
    $_POST["email"]="";
}

// 生成唯一的任务ID (类似RNAJog的timeVar)
$timeVar = date('YmdHis').rand(0,9);
$email = $_POST["email"];

// 获取用户输入
$user_text = $_POST['user_text'];

// 验证输入
if (empty($user_text)) {
    echo "<script>alert('Please input molecule description!'); history.back();</script>";
    exit;
}

// 将用户输入保存到文本文件
// 使用绝对路径确保文件保存在正确位置
$upload_dir = "/var/www/bioinf/TDMol/upload/";

// 如果目录不存在则创建
if (!file_exists($upload_dir)) {
    mkdir($upload_dir, 0777, true);
}

$tempName = $upload_dir.$timeVar.".txt";
$textFile = fopen($tempName, "w");
fwrite($textFile, $user_text);
fclose($textFile);

// 记录日志用于调试
$log_file = "logs/edm_php_debug.log";
if (!file_exists("logs")) {
    mkdir("logs", 0777, true);
}
file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Saved file: $tempName, size: " . filesize($tempName) . " bytes\n", FILE_APPEND);

// 通过排队系统启动后端处理（防止过载）
// 将输出重定向到日志文件以便调试
// 使用引号包裹参数，确保空字符串也能正确传递
$command = "bash queue_edm.sh '".$email."' '".$timeVar."' >> logs/queue.log 2>&1 &";
file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Submitting to queue: $command\n", FILE_APPEND);
exec($command, $output, $return_code);
file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Task submitted to queue, return code: $return_code\n", FILE_APPEND);
if (!empty($output)) {
    file_put_contents($log_file, date('[Y-m-d H:i:s] ') . "Output: " . implode("\n", $output) . "\n", FILE_APPEND);
}

// 从PHP传递参数给JS，用于异步读取结果文件
echo "<script>var timeVar=\"$timeVar\";</script> ";
echo "<script>var email=\"$email\";</script> ";
?>

<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDM Molecule Generator - Processing</title>
    <link rel="stylesheet" href="./css/bootstrap.css">
    <link rel="stylesheet" href="./css/unified-style.css">
    <style>
      .result-link {
        display: inline-block;
        padding: 12px 24px;
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      .result-link:hover {
        background: linear-gradient(135deg, #229954 0%, #1e8449 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
      }
      .result-link.disabled {
        background-color: #95a5a6;
        color: #ecf0f1;
        cursor: not-allowed;
        pointer-events: none;
        box-shadow: none;
        transform: none;
      }
      .info { color: #1976d2; }
      .success { color: #27ae60; }
      .error { color: #e74c3c; }
    </style>
  </head>

  <script>
    window.onbeforeunload = function(e) {
        var dialogText = 'Please do not refresh here';
        e.returnValue = dialogText;
        return dialogText;
    };
  </script>

  <body>
  <div class="main-header">
    <h1>EDM: Equivariant Diffusion Model for Molecule Generation</h1>
  </div>

  <div class="page-container">

    <h2 style="text-align:center;margin-bottom:20px;">Thank you for using EDM Molecule Generator!</h2>

    <p><strong>Your molecule generation task has been submitted successfully.</strong></p>
    <p>The program is generating molecules based on your description. This typically takes several minutes depending on the number of molecules requested.</p>

    <p><strong class="info">Note: Your task is now in the queue system.</strong> If there are other tasks running, your task will wait until resources become available.</p>

    <div class="info-box" style="background-color: #fff9e6; border: 2px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
      <p><strong>Your Result URL:</strong></p>
      <p style="font-size: 16px; color: #d35400; font-weight: bold; word-break: break-all; font-family: 'Courier New', monospace;">
        <?php echo "http://" . $_SERVER['HTTP_HOST'] . "/bioinf/TDMol/result/" . $timeVar . "/brief.html"; ?>
      </p>
      <p style="font-size: 13px; color: #666; margin-top: 10px;">
        <em>You can bookmark this URL and access your results directly once they are ready.</em>
      </p>
    </div>

    <p><strong class="info">This page will automatically check for results every 15 seconds.</strong></p>
    <p>When generation is complete, the link below will become clickable:</p>

    <div class="status-box">
      <div id="statusText" class="info">Checking for results...</div>
      <div style="margin-top:15px;text-align:center;">
        <a href="result/" id="resultLink" class="result-link disabled">View Results (Waiting...)</a>
      </div>
    </div>

    <p style="font-size:14px;color:#666;"><em>Tip: You can open the browser console (F12) to see detailed checking status.</em></p>
    <p>You can also bookmark this page and come back later to check the results.</p>
    <p>If you provided an email address, the result link will also be sent to your email.</p>

    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
      <a href="index.html" class="btn btn-primary">← Back to Home Page</a>
    </div>

    <div class="alert alert-warning" style="margin-top: 20px;">
      <strong>⚠️ NOTE:</strong> Please do not refresh this page, otherwise it will submit a new task.
    </div>
  </div>

  <script>
    var resultFound = false;
    var checkCount = 0;
    var statusText, resultLink;

    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        statusText = document.getElementById('statusText');
        resultLink = document.getElementById('resultLink');

        console.log("Task ID: " + timeVar);
        console.log("Starting to check for: result/" + timeVar + "/brief.html");

        // 立即检查一次
        checkResultFile("result/" + timeVar + "/brief.html", handleCheckResult);

        // 每15秒检查一次
        var checkInterval = setInterval(function(){
            if(!resultFound) {
                checkResultFile("result/" + timeVar + "/brief.html", handleCheckResult);
            }
        }, 15000);

        // 60分钟后停止检查
        setTimeout(function() {
            if (!resultFound) {
                clearInterval(checkInterval);
                console.log("Stopped checking after 60 minutes");
                updateStatus("Generation is taking longer than expected. Please check back later.", "error");
                // 即使超时也提供链接
                var resultURL = "result/" + timeVar + "/brief.html";
                resultLink.href = resultURL;
                resultLink.classList.remove('disabled');
                resultLink.innerHTML = "Try to View Results Anyway";
            }
        }, 3600000);
    });

    // 使用原生JavaScript的XMLHttpRequest检测文件
    function checkResultFile(url, callback){
        checkCount++;
        console.log("Check #" + checkCount + ": " + url);

        var xhr = new XMLHttpRequest();
        xhr.timeout = 5000; // 5秒超时

        xhr.onload = function() {
            if (xhr.status === 200) {
                console.log("✓ File found! Status: " + xhr.status);
                callback(true);
            } else {
                console.log("✗ File not found. Status: " + xhr.status);
                callback(false);
            }
        };

        xhr.onerror = function() {
            console.log("✗ Request failed");
            callback(false);
        };

        xhr.ontimeout = function() {
            console.log("✗ Request timeout");
            callback(false);
        };

        xhr.open('HEAD', url, true);
        xhr.send();
    }

    function updateStatus(message, className) {
        statusText.innerHTML = message;
        statusText.className = className || 'info';
    }

    function enableResultLink() {
        var fullURL = "result/" + timeVar + "/brief.html";
        resultLink.href = fullURL;
        resultLink.classList.remove('disabled');
        resultLink.innerHTML = "✓ Click Here to View Results";
        updateStatus("Results are ready!", "success");
        console.log("Results ready! Link: " + fullURL);
    }

    function handleCheckResult(fileExists){
        if(fileExists && !resultFound){
            resultFound = true;
            enableResultLink();
        } else if(!fileExists) {
            // 每4次检查（每分钟）更新一次状态
            if(checkCount % 4 == 0) {
                var timeStr = new Date().toLocaleTimeString();
                updateStatus("Still generating... (Checked " + checkCount + " times, last: " + timeStr + ")", "info");
            }
        }
    }

    // 注意：任务已经通过排队系统提交（第44行调用queue_edm.sh），不需要再通过AJAX重复启动

  </script>

  </body>
</html>
