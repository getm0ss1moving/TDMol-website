# EDM.php 自动检测功能测试指南

## 修复内容总结

### 问题诊断
原来的代码存在以下问题：
1. **同步AJAX** (`async: false`) - 现代浏览器已弃用，会导致页面卡顿
2. **错误处理不足** - 没有详细的调试信息
3. **逻辑混乱** - `send()`函数返回值没有被正确使用
4. **用户体验差** - 没有实时反馈检查进度

### 改进方案

#### 1. 使用异步AJAX (EDM.php:117-129)
```javascript
$.ajax({
    url: url,
    type: 'HEAD',
    timeout: 5000,
    success: function(data, textStatus, xhr) {
        console.log("✓ File found!");
        callback(true);
    },
    error: function(xhr, textStatus, error) {
        console.log("✗ File not found yet.");
        callback(false);
    }
});
```

#### 2. 添加详细的控制台日志 (EDM.php:102,109,115,122,126)
- 每次检查都输出日志
- 显示检查次数和时间
- 成功/失败状态清晰

#### 3. 改进用户反馈 (EDM.php:139)
```javascript
// 每分钟更新一次状态显示
if(!fileExists && checkCount % 4 == 0) {
    document.getElementById("para1").innerHTML =
        "Still generating... (Checked " + checkCount + " times, last check: " +
        new Date().toLocaleTimeString() + ")"
}
```

#### 4. 超时处理 (EDM.php:158-164)
60分钟后如果还没有结果，显示友好的错误信息和手动链接

## 测试步骤

### 测试1: 正常流程测试

1. **提交一个任务**
   - 打开 EDM 首页
   - 输入分子描述（例如: "aspirin-like molecule"）
   - 提交任务

2. **打开浏览器控制台**
   - 按 F12 打开开发者工具
   - 切换到 "Console" 标签

3. **观察控制台输出**
   应该看到类似以下的日志：
   ```
   Task ID: 202511301510533
   Starting to check for: result/202511301510533/brief.html
   Check #1: result/202511301510533/brief.html
   ✗ File not found yet. Status: 404, Error: error
   Check #2: result/202511301510533/brief.html
   ✗ File not found yet. Status: 404, Error: error
   ...
   Check #8: result/202511301510533/brief.html
   ✓ File found! Status: 200
   Results are ready!
   ```

4. **观察页面变化**
   - 初始显示: "Checking for results... (This may take several minutes)"
   - 每分钟更新: "Still generating... (Checked 4 times, last check: 14:25:30)"
   - 完成时显示: "✓ Click here to view results (Ready!)" - 可点击链接

5. **点击链接**
   - 应该正确跳转到 brief.html 结果页面

### 测试2: 手动创建测试文件

如果想快速测试检测功能（不等待实际生成），可以：

1. **手动创建测试结果目录**
   ```bash
   mkdir -p /var/www/bioinf2/edm_web/result/TEST123456/
   touch /var/www/bioinf2/edm_web/result/TEST123456/brief.html
   ```

2. **修改 EDM.php 中的 timeVar**
   临时在第8行后添加：
   ```php
   $timeVar = "TEST123456"; // 测试用
   ```

3. **提交任务并观察**
   - 应该在15秒内检测到文件
   - 立即显示可点击链接

### 测试3: 超时测试

1. **停止后端生成进程**（模拟任务失败）
2. **观察60分钟后的行为**
   - 应该停止检查
   - 显示错误信息和手动链接

## 调试技巧

### 如果检测不到文件

1. **检查文件路径**
   在控制台输入：
   ```javascript
   console.log("Full URL: " + window.location.origin + "/bioinf2/edm_web/result/" + timeVar + "/brief.html")
   ```

2. **手动测试AJAX请求**
   在控制台输入：
   ```javascript
   $.ajax({
       url: "result/" + timeVar + "/brief.html",
       type: 'HEAD',
       success: function(){ console.log("SUCCESS!") },
       error: function(xhr){ console.log("FAILED: " + xhr.status) }
   });
   ```

3. **检查文件权限**
   ```bash
   ls -la /var/www/bioinf2/edm_web/result/{task_id}/
   chmod 644 /var/www/bioinf2/edm_web/result/{task_id}/brief.html
   ```

4. **检查Web服务器配置**
   - 确保 Apache/Nginx 可以访问 result 目录
   - 检查 .htaccess 是否阻止访问

### 如果看不到控制台日志

1. **确认jQuery已加载**
   在控制台输入：
   ```javascript
   typeof jQuery
   ```
   应该返回 "function"

2. **检查JavaScript错误**
   查看控制台是否有红色错误信息

## 预期行为总结

| 场景 | 预期行为 | 时间 |
|------|---------|------|
| 任务刚提交 | 显示 "Checking for results..." | 立即 |
| 检查中 | 控制台每15秒输出一次日志 | 每15秒 |
| 检查中（每分钟） | 页面更新检查次数和时间 | 每分钟 |
| 检测到文件 | 显示可点击链接 "✓ Click here to view results" | 检测到后立即 |
| 60分钟未检测到 | 显示错误信息和手动链接 | 60分钟后 |

## 可能的问题和解决方案

### 问题1: 一直显示 "Checking for results..."
**原因**: 后端生成失败或文件路径错误
**解决**:
- 检查 EDM_server.py 日志
- 手动检查文件是否生成
- 验证路径是否正确

### 问题2: 控制台显示 404 错误但文件确实存在
**原因**: Web服务器配置问题
**解决**:
- 检查 Apache/Nginx 配置
- 确认文件权限正确
- 测试直接访问URL

### 问题3: CORS 错误
**原因**: 跨域请求被阻止
**解决**:
- EDM.php 和 brief.html 应该在同一域名下
- 检查 Web 服务器 CORS 配置

## 成功标准

✓ 控制台能看到检查日志
✓ 页面状态实时更新
✓ 检测到文件后自动显示链接
✓ 点击链接能正确跳转
✓ 60分钟后正确超时处理
