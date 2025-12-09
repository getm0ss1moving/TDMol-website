# EDM 排队系统测试检查清单

## 📝 测试前准备

- [ ] 服务器已部署所有文件到 `/var/www/bioinf2/edm_web/`
- [ ] 后端服务器SSH连接正常
- [ ] Python环境配置正确
- [ ] 所有shell脚本有执行权限（chmod +x）

---

## 🧪 测试1：基础功能验证

### 步骤1：初始化
```bash
bash init_queue.sh
```
- [ ] 创建了 `running.queue` 文件
- [ ] 创建了 `waiting.queue` 文件
- [ ] 文件权限为 666（rw-rw-rw-）
- [ ] 没有报错信息

### 步骤2：检查状态
```bash
bash check_queue.sh
```
- [ ] 显示 "Running tasks: 0"
- [ ] 显示 "Waiting tasks: 0"
- [ ] 没有报错信息

---

## 🧪 测试2：单任务测试

### 步骤1：创建测试输入
```bash
echo "Generate benzene derivatives" > upload/SINGLE_TEST.txt
```
- [ ] 文件创建成功

### 步骤2：提交任务
```bash
bash queue_edm.sh "test@test.com" "SINGLE_TEST" >> logs/test.log 2>&1 &
```
- [ ] 命令执行无错误

### 步骤3：检查队列
```bash
bash check_queue.sh
```
- [ ] 显示 "Running tasks: 1"
- [ ] 显示任务ID "SINGLE_TEST"
- [ ] 显示邮箱 "test@test.com"

### 步骤4：查看日志
```bash
tail -20 logs/queue.log
```
- [ ] 看到 "New task request: SINGLE_TEST"
- [ ] 看到 "Slot available, starting task immediately"
- [ ] 看到 "Executing: bash EDM.sh"

### 步骤5：等待完成（约5-10分钟）
```bash
watch -n 5 bash check_queue.sh
```
- [ ] 任务完成后 "Running tasks: 0"
- [ ] 日志显示 "Task SINGLE_TEST finished successfully"

### 步骤6：验证结果
```bash
ls result/SINGLE_TEST/
```
- [ ] 存在 `brief.html`
- [ ] 存在 `result_*.html`
- [ ] 存在 `molecule_*.xyz`
- [ ] 存在 `molecule_*.sdf`
- [ ] 存在 `summary.json`

---

## 🧪 测试3：多任务排队测试

### 步骤1：准备多个任务
```bash
echo "Benzene" > upload/MULTI_TEST_1.txt
echo "Toluene" > upload/MULTI_TEST_2.txt
echo "Phenol" > upload/MULTI_TEST_3.txt
```
- [ ] 3个文件创建成功

### 步骤2：快速提交3个任务
```bash
bash queue_edm.sh "test@test.com" "MULTI_TEST_1" >> logs/test.log 2>&1 &
sleep 1
bash queue_edm.sh "test@test.com" "MULTI_TEST_2" >> logs/test.log 2>&1 &
sleep 1
bash queue_edm.sh "test@test.com" "MULTI_TEST_3" >> logs/test.log 2>&1 &
```
- [ ] 3个命令执行无错误

### 步骤3：立即检查队列
```bash
bash check_queue.sh
```
- [ ] 显示 "Running tasks: 1"（任务1）
- [ ] 显示 "Waiting tasks: 2"（任务2和3）
- [ ] 任务2在位置1
- [ ] 任务3在位置2

### 步骤4：查看排队日志
```bash
grep "MULTI_TEST" logs/queue.log
```
- [ ] MULTI_TEST_1: "starting task immediately"
- [ ] MULTI_TEST_2: "adding to waiting queue"
- [ ] MULTI_TEST_2: "queued at position 1"
- [ ] MULTI_TEST_3: "adding to waiting queue"
- [ ] MULTI_TEST_3: "queued at position 2"

### 步骤5：等待第1个任务完成
```bash
watch -n 5 bash check_queue.sh
```
观察任务转移：
- [ ] 任务1完成，从 running.queue 消失
- [ ] 任务2自动从 waiting.queue 移到 running.queue
- [ ] 日志显示 "Starting next task from queue: MULTI_TEST_2"

### 步骤6：等待第2个任务完成
- [ ] 任务2完成，从 running.queue 消失
- [ ] 任务3自动从 waiting.queue 移到 running.queue
- [ ] 日志显示 "Starting next task from queue: MULTI_TEST_3"

### 步骤7：等待所有任务完成
- [ ] Running tasks: 0
- [ ] Waiting tasks: 0
- [ ] 日志显示 "No more tasks in waiting queue"

### 步骤8：验证所有结果
```bash
ls result/ | grep MULTI_TEST
```
- [ ] 存在 `MULTI_TEST_1/` 目录及内容
- [ ] 存在 `MULTI_TEST_2/` 目录及内容
- [ ] 存在 `MULTI_TEST_3/` 目录及内容

---

## 🧪 测试4：使用自动化脚本

### 步骤1：运行测试脚本
```bash
bash test_queue.sh 3
```
- [ ] 脚本运行无错误
- [ ] 显示 "All tasks submitted!"
- [ ] 显示当前队列状态

### 步骤2：监控执行
```bash
tail -f logs/queue.log
```
- [ ] 看到3个任务提交
- [ ] 看到排队和执行过程
- [ ] 看到自动调度日志

---

## 🧪 测试5：Web界面测试

### 步骤1：访问网页
```
http://your-server/bioinf2/edm_web/index.html
```
- [ ] 页面正常加载
- [ ] 表单显示正常

### 步骤2：填写表单
- Molecule Description: `Generate molecules with benzene and hydroxyl`
- Email: `your-email@example.com`
- Number of Molecules: `3`

- [ ] 所有字段填写完成

### 步骤3：提交任务
点击 Submit 按钮
- [ ] 跳转到 EDM.php 页面
- [ ] 显示 "Thank you for using EDM"
- [ ] 显示 "task is now in the queue system"
- [ ] 页面开始自动检查结果

### 步骤4：服务器端验证
```bash
bash check_queue.sh
```
- [ ] 看到新提交的任务
- [ ] 任务ID格式为 `YYYYMMDDHHMMSSx`

### 步骤5：等待结果
在Web页面上：
- [ ] 页面每15秒自动检查一次
- [ ] 显示检查次数和时间
- [ ] 任务完成后链接变为可点击
- [ ] 点击链接可查看结果

### 步骤6：查看结果页面
- [ ] brief.html 正常显示
- [ ] 显示所有生成的分子
- [ ] 2D图像正常显示
- [ ] SMILES字符串显示正确

### 步骤7：查看分子详情
点击任意分子的 "查看详情"
- [ ] result_X.html 正常显示
- [ ] JSmol 3D查看器正常加载
- [ ] 可以旋转和缩放分子
- [ ] 2D图像显示正确
- [ ] 下载链接正常工作

---

## 🧪 测试6：并发数调整测试

### 步骤1：修改并发数
```bash
nano queue_edm.sh
```
修改第31行：
```bash
MAX_CONCURRENT=2  # 改为2
```
- [ ] 文件修改成功

### 步骤2：提交4个任务
```bash
bash test_queue.sh 4
```

### 步骤3：验证并发
```bash
bash check_queue.sh
```
- [ ] 显示 "Running tasks: 2"（同时运行2个）
- [ ] 显示 "Waiting tasks: 2"（等待2个）

### 步骤4：验证并发执行
```bash
ps aux | grep EDM.sh
```
- [ ] 看到2个 EDM.sh 进程同时运行

---

## 🧪 测试7：异常处理测试

### 测试7.1：权限问题
```bash
chmod 444 running.queue  # 改为只读
bash queue_edm.sh "test@test.com" "PERM_TEST"
```
- [ ] 显示权限错误
- [ ] 恢复权限：`chmod 666 running.queue`

### 测试7.2：队列文件丢失
```bash
rm running.queue waiting.queue
bash check_queue.sh
```
- [ ] 显示错误提示
- [ ] 提示运行 `init_queue.sh`

### 测试7.3：清空队列
```bash
> running.queue
> waiting.queue
bash check_queue.sh
```
- [ ] 队列清空成功
- [ ] 显示0个任务

---

## 📊 测试结果记录

### 测试环境
- **服务器IP：** _______________
- **测试日期：** _______________
- **Python版本：** _______________
- **并发设置：** MAX_CONCURRENT = _____

### 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 测试1：基础功能 | ☐ 通过 ☐ 失败 | |
| 测试2：单任务 | ☐ 通过 ☐ 失败 | |
| 测试3：多任务排队 | ☐ 通过 ☐ 失败 | |
| 测试4：自动化脚本 | ☐ 通过 ☐ 失败 | |
| 测试5：Web界面 | ☐ 通过 ☐ 失败 | |
| 测试6：并发调整 | ☐ 通过 ☐ 失败 | |
| 测试7：异常处理 | ☐ 通过 ☐ 失败 | |

### 性能数据

**单任务（3个分子）：**
- 执行时间：_________ 秒
- CPU使用率：_________ %
- 内存使用：_________ MB

**多任务排队（3个任务）：**
- 总时间：_________ 秒
- 平均等待时间：_________ 秒

**并发执行（MAX_CONCURRENT=2）：**
- 总时间：_________ 秒
- 相比串行提升：_________ %

---

## ✅ 测试完成标准

全部测试通过需满足：

- [ ] 所有7个测试项状态为"通过"
- [ ] 无报错或异常信息
- [ ] 队列自动调度正常工作
- [ ] Web界面正常显示结果
- [ ] 生成的分子文件完整

---

## 📝 问题记录

测试中遇到的问题及解决方案：

| 问题描述 | 解决方案 | 状态 |
|----------|----------|------|
| | | |
| | | |
| | | |

---

**测试人员签名：** ________________
**测试日期：** ________________
**系统版本：** v1.0
