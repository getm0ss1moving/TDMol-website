# 重复启动任务问题修复报告

## 问题发现

用户发现：**每次检测时都会在后端启动一次代码执行**

## 问题分析

### 原始流程（有问题）

```
1. 用户提交表单
   ↓
2. EDM.php 执行
   - 保存用户输入到文件
   - 第44行：exec("bash EDM.sh '$email' '$timeVar' ...") ← 【第1次启动】
   - 生成HTML等待页面
   ↓
3. 浏览器显示等待页面
   - 页面加载完成
   - JavaScript调用 ajaxf1()
   ↓
4. ajaxf1() 发送POST请求到 py.php
   ↓
5. py.php 执行
   - 第17行：exec("bash EDM.sh '$email' '$timeVar'") ← 【第2次启动！重复！】
   ↓
结果：同一个任务被启动了两次！
```

### 问题代码位置

**EDM.php (第44行)**
```php
$command = "bash EDM.sh '".$email."' '".$timeVar."' >> logs/edm_sh_output.log 2>&1 &";
exec($command, $output, $return_code);
```

**py.php (第17行)**
```php
$command = "bash EDM.sh '".$email."' '".$timeVar."' 2>&1";
exec($command, $output, $return_code);
```

**EDM.php JavaScript (调用py.php)**
```javascript
function ajaxf1(){
    // 发送POST请求到py.php
    // 导致py.php再次执行 bash EDM.sh
}
ajaxf1(); // 页面加载后立即调用
```

### 问题影响

1. **资源浪费**：同一个任务运行两次，浪费计算资源
2. **可能的文件冲突**：两个进程可能同时写入同一个文件
3. **混乱的日志**：难以追踪哪个进程产生的输出
4. **潜在的数据不一致**：两次运行可能产生不同的结果

## 解决方案

### 修复策略

**移除重复调用**：
- 保留 EDM.php 中的任务启动（第44行）
- 删除 py.php 的调用
- 删除 ajaxf1() 函数

### 修复后的流程

```
1. 用户提交表单
   ↓
2. EDM.php 执行
   - 保存用户输入到文件
   - exec("bash EDM.sh ...") ← 【唯一启动点】
   - 生成HTML等待页面
   ↓
3. 浏览器显示等待页面
   - 每15秒使用HEAD请求检测 result/{timeVar}/brief.html
   - 不调用任何后端执行脚本
   ↓
4. 检测到文件存在
   - 激活"View Results"按钮
   - 用户点击跳转到结果页面
```

### 代码修改

**EDM.php (已修改)**
```javascript
// 删除了整个 ajaxf1() 函数
// 删除了 ajaxf1() 的调用

// 只保留文件检测逻辑
function checkResultFile(url, callback){
    var xhr = new XMLHttpRequest();
    xhr.open('HEAD', url, true); // 只检查文件，不执行任何代码
    xhr.onload = function() {
        callback(xhr.status === 200);
    };
    xhr.send();
}
```

**py.php**
- 不再被使用
- 可以保留用于其他用途或删除

## 验证修复

### 如何验证任务只启动一次

**方法1：检查进程**
```bash
# 提交任务后立即检查
ps aux | grep EDM.sh
ps aux | grep python.*EDM

# 应该只看到一组进程，不是两组
```

**方法2：检查日志**
```bash
# 查看EDM.sh的日志
tail -f logs/edm_sh_output.log

# 应该只看到一次任务启动的记录
```

**方法3：检查py.php日志**
```bash
tail -f logs/py_php_debug.log

# 应该看不到新的记录（因为不再调用py.php）
```

**方法4：浏览器控制台**
```
打开浏览器控制台 (F12)
提交一个任务
观察网络请求：
- 应该看到：多次 HEAD 请求到 result/{timeVar}/brief.html
- 不应该看到：POST 请求到 py.php
```

## 测试清单

- [x] 提交任务后只启动一次后端进程
- [x] 页面检测功能正常工作（每15秒检测一次）
- [x] 检测到结果后按钮正常激活
- [x] 点击按钮能正确跳转到结果页面
- [x] 不再有py.php的网络请求
- [x] 日志中没有重复的任务启动记录

## 性能提升

修复后的优势：
- ✅ **减少50%的后端负载**（不再重复执行任务）
- ✅ **避免资源竞争**（只有一个进程操作文件）
- ✅ **更清晰的日志**（不再有混乱的重复记录）
- ✅ **更快的响应**（减少不必要的PHP执行）

## 注意事项

### HEAD请求的工作原理

```javascript
xhr.open('HEAD', url, true);
```

- HEAD请求**只检查文件是否存在**
- **不下载文件内容**
- **不执行任何服务器端代码**（如PHP）
- 只返回HTTP状态码（200表示存在，404表示不存在）

### 为什么HEAD请求是安全的

- 它是HTTP标准方法，专门用于检查资源是否存在
- Web服务器（Apache/Nginx）直接响应，不涉及PHP/Python
- 不会触发任何应用程序逻辑
- 开销极小（不传输文件内容）

## 总结

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 任务启动次数 | 2次（EDM.php + py.php） | 1次（仅EDM.php） |
| 检测方式 | AJAX调用py.php | HEAD请求检查文件 |
| 后端负载 | 高（重复执行） | 正常 |
| 资源使用 | 浪费50% | 优化 |
| 日志清晰度 | 混乱（重复记录） | 清晰 |

**结论**：修复成功，任务现在只在用户提交时启动一次，之后只通过轻量级的HEAD请求检测结果文件是否生成。
