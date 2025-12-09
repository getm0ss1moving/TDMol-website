# EDM 排队系统快速测试清单

## ⚡ 5分钟快速测试

### 前置条件
- 已部署到服务器：`/var/www/bioinf2/edm_web/`
- 已安装所有依赖
- 后端服务器可通过SSH访问

---

## 测试步骤

### 1️⃣ 初始化（30秒）

```bash
cd /var/www/bioinf2/edm_web
bash init_queue.sh
```

**期望输出：**
```
✓ Queue files created
✓ Permissions set
✓ Queue system initialized successfully!
```

---

### 2️⃣ 检查初始状态（10秒）

```bash
bash check_queue.sh
```

**期望输出：**
```
Running tasks: 0
Waiting tasks: 0
```

---

### 3️⃣ 提交测试任务（1分钟）

**打开两个终端窗口：**

**终端1（监控）：**
```bash
watch -n 2 bash check_queue.sh
```

**终端2（提交任务）：**
```bash
# 创建测试输入
echo "Generate small organic molecules with benzene ring" > upload/TEST001.txt
echo "Generate molecules with amine and carboxyl groups" > upload/TEST002.txt
echo "Generate aromatic compounds with hydroxyl groups" > upload/TEST003.txt

# 快速提交3个任务
bash queue_edm.sh "test@test.com" "TEST001" &
sleep 1
bash queue_edm.sh "test@test.com" "TEST002" &
sleep 1
bash queue_edm.sh "test@test.com" "TEST003" &
```

---

### 4️⃣ 观察队列行为（2分钟）

在**终端1**的监控窗口，您应该看到：

**阶段1（任务刚提交）：**
```
Running tasks: 1
  Task ID: TEST001  ← 第1个任务立即开始

Waiting tasks: 2
  Position: 1
  Task ID: TEST002  ← 第2个任务等待

  Position: 2
  Task ID: TEST003  ← 第3个任务等待
```

**阶段2（第1个任务完成）：**
```
Running tasks: 1
  Task ID: TEST002  ← 自动启动第2个任务

Waiting tasks: 1
  Position: 1
  Task ID: TEST003  ← 还剩1个等待
```

**阶段3（第2个任务完成）：**
```
Running tasks: 1
  Task ID: TEST003  ← 自动启动第3个任务

Waiting tasks: 0  ← 等待队列已空
```

**阶段4（所有任务完成）：**
```
Running tasks: 0
Waiting tasks: 0
```

---

### 5️⃣ 检查日志（30秒）

```bash
tail -50 logs/queue.log
```

**期望看到：**
```
[时间] New task request: TEST001
[时间] Slot available, starting task immediately
[时间] New task request: TEST002
[时间] All slots occupied, adding to waiting queue
[时间] Task TEST002 queued at position 1
[时间] New task request: TEST003
[时间] All slots occupied, adding to waiting queue
[时间] Task TEST003 queued at position 2
...
[时间] Task TEST001 finished successfully
[时间] Starting next task from queue: TEST002
...
[时间] Task TEST002 finished successfully
[时间] Starting next task from queue: TEST003
...
[时间] Task TEST003 finished successfully
[时间] No more tasks in waiting queue
```

---

### 6️⃣ 验证结果文件（30秒）

```bash
# 检查结果目录
ls -lh result/TEST001/
ls -lh result/TEST002/
ls -lh result/TEST003/
```

**期望看到每个目录中有：**
```
brief.html          ← 结果概览页面
result_1.html       ← 第1个分子详情
result_2.html       ← 第2个分子详情
result_3.html       ← 第3个分子详情
molecule_1.xyz      ← 分子坐标文件
molecule_1.sdf      ← 分子结构文件
...
summary.json        ← 结果摘要
```

---

## ✅ 测试成功标准

- [ ] 队列文件成功创建
- [ ] 第1个任务立即执行
- [ ] 第2、3个任务进入等待队列
- [ ] 任务完成后自动启动下一个
- [ ] 所有任务最终都完成
- [ ] 生成了HTML结果页面
- [ ] 生成了分子文件（XYZ、SDF）
- [ ] 日志记录完整

---

## 🔧 快速故障排查

### 问题：任务不执行

**检查：**
```bash
# 查看进程
ps aux | grep EDM.sh

# 查看队列
cat running.queue
cat waiting.queue
```

**解决：**
```bash
# 清空队列重试
> running.queue
> waiting.queue
bash init_queue.sh
```

---

### 问题：权限错误

**解决：**
```bash
chmod 666 running.queue waiting.queue
chmod 755 queue_edm.sh EDM.sh
```

---

### 问题：找不到Python环境

**检查后端配置：**
- 查看 `EDM_backend.sh` 中的 Python 路径
- 确认 conda 环境 `edm_web` 存在

---

## 📊 性能基准

**预期时间（3个分子）：**
- 任务1：~145秒
- 任务2：~145秒（等待任务1完成后开始）
- 任务3：~145秒（等待任务2完成后开始）
- **总计：** ~435秒（7.5分钟）

**如果设置 `MAX_CONCURRENT=2`：**
- 任务1和任务2并行：~145秒
- 任务3：~145秒
- **总计：** ~290秒（5分钟）

---

## 🎯 下一步

测试成功后，可以：

1. **通过Web界面测试**
   ```
   访问: http://your-server/bioinf2/edm_web/index.html
   ```

2. **调整并发数**
   ```bash
   # 编辑 queue_edm.sh
   nano queue_edm.sh
   # 修改 MAX_CONCURRENT=2（如果有双GPU）
   ```

3. **设置监控**
   ```bash
   # 添加到 crontab
   0 */6 * * * bash /var/www/bioinf2/edm_web/check_queue.sh >> /var/www/bioinf2/edm_web/logs/queue_status.log
   ```

4. **部署到生产**
   - 修改默认分子数为100
   - 配置邮件发送
   - 设置定期清理任务

---

**测试用时：** 约5-10分钟（取决于是否等待完整生成）
**建议：** 首次测试使用3个分子，验证流程正确后再改为100
