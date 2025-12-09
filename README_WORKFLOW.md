# EDM Web Application Workflow

## 概述
这是一个完全仿照RNAJog架构的EDM分子生成Web应用系统。用户在前端输入分子描述文本，系统在后端生成分子并返回3D可视化结果。

## 系统架构

```
前端服务器 (22端口)          后端服务器 (2349端口)
     |                              |
index.html (用户界面)               |
     ↓                              |
  EDM.php                           |
     ↓                              |
EDM_server.py -----(SSH/SFTP)----> EDM.sh
                                    ↓
                            run_generation.py
                                    ↓
                            (调用model_runner.py生成分子)
                                    ↓
                            processhtml.py
                                    ↓
                            send_email.py (可选)
                                    ↓
                    (结果传回前端服务器)
                                    ↓
                            brief.html & result_X.html
```

## 文件说明

### 前端文件 (部署在前端服务器)

1. **index.html** - 主页面
   - 用户输入分子描述文本
   - 可选填写邮箱地址
   - 表单提交到 EDM.php

2. **EDM.php** - 表单处理脚本
   - 生成唯一任务ID (timeVar)
   - 保存用户输入到文本文件
   - 调用 EDM_server.py
   - 跳转到 waiting.html

3. **waiting.html** - 等待页面
   - 显示任务ID
   - 定期检查结果是否生成
   - 自动跳转到结果页面

4. **EDM_server.py** - 任务调度脚本
   - 上传用户输入文件到后端服务器
   - 通过SSH在后端服务器执行 EDM.sh
   - 下载结果文件(brief.html, result_X.html, XYZ, SDF等)

### 后端文件 (部署在后端服务器 2349端口)

5. **EDM.sh** - 后端执行脚本
   - 创建结果目录
   - 调用 run_generation.py 生成分子
   - 调用 processhtml.py 生成HTML页面
   - 如果有邮箱，调用 send_email.py 发送邮件

6. **run_generation.py** - 分子生成核心脚本
   - 读取用户输入文本
   - 初始化模型 (调用model_runner.py)
   - 生成指定数量的分子 (默认3个)
   - 保存XYZ和SDF格式的分子文件
   - 生成summary.json摘要文件

7. **processhtml.py** - HTML结果生成脚本
   - 读取summary.json
   - 为每个分子生成result_X.html (包含JSmol 3D可视化)
   - 生成brief.html概览页面 (包含所有分子的2D结构)

8. **send_email.py** - 邮件发送脚本
   - 如果用户提供了邮箱，发送结果通知邮件

### 支持文件

9. **model_runner.py** - 模型运行器
   - initialize_models(): 初始化EDM模型
   - generate_and_evaluate_for_webapp(): 生成并评估分子

10. **app.py** - 原始模型脚本 (保留功能不变)

## 数据流

### 输入数据
- **用户输入**: 分子描述文本 (英文)
- **邮箱**: 可选

### 处理流程
1. 用户在index.html填写表单
2. EDM.php生成任务ID并保存输入
3. EDM_server.py上传输入文件到后端
4. 后端EDM.sh执行完整的生成流程
5. run_generation.py调用模型生成分子
6. processhtml.py生成可视化页面
7. 结果文件传回前端
8. 用户查看结果

### 输出数据

#### 每个任务生成以下文件:
```
result/{task_id}/
├── brief.html              # 结果概览页面
├── result_1.html           # 分子1详情页面 (含3D可视化)
├── result_2.html           # 分子2详情页面
├── result_3.html           # 分子3详情页面
├── molecule_1.xyz          # 分子1的XYZ坐标文件
├── molecule_1.sdf          # 分子1的SDF文件
├── molecule_2.xyz
├── molecule_2.sdf
├── molecule_3.xyz
├── molecule_3.sdf
└── summary.json            # 任务摘要JSON文件
```

## 参数说明

### 系统参数 (在代码中设定，用户不可见)
- **num_samples**: 3 (生成分子数量)
- **guidance_scale**: 5.0 (引导系数)

### 传递参数
- EDM.php → EDM_server.py: `email, task_id`
- EDM_server.py → EDM.sh: `email, task_id`
- EDM.sh → run_generation.py: `task_id, input_file, output_dir`
- EDM.sh → processhtml.py: `task_id, email`
- EDM.sh → send_email.py: `email, task_id` (仅当email非空)

## 部署说明

### 前端服务器部署
1. 将以下文件放置在 `/var/www/bioinf2/edm_web/`:
   - index.html
   - EDM.php
   - waiting.html
   - EDM_server.py

2. 创建目录:
   ```bash
   mkdir -p /var/www/bioinf2/edm_web/upload
   mkdir -p /var/www/bioinf2/edm_web/result
   ```

### 后端服务器部署
1. 将以下文件放置在 `/data/yfang/EDM_new/web_apps/`:
   - EDM.sh
   - run_generation.py
   - processhtml.py
   - send_email.py
   - model_runner.py
   - app.py (及其依赖文件)

2. 创建目录:
   ```bash
   mkdir -p /data/yfang/EDM_new/web_apps/upload
   mkdir -p /data/yfang/EDM_new/web_apps/result
   ```

3. 设置执行权限:
   ```bash
   chmod +x /data/yfang/EDM_new/web_apps/EDM.sh
   ```

## 3D分子可视化

使用JSmol进行3D分子可视化:
- JSmol库位置: `/bioinf2/edm_web/static/jsmol/` 或 `../jsmol-16.3.33/jsmol/`
- 每个result_X.html包含完整的JSmol初始化代码
- XYZ坐标数据通过Base64编码嵌入HTML

## 2D分子可视化

使用RDKit生成2D分子结构图:
- 在processhtml.py中通过SMILES生成PNG图像
- 图像以Base64 Data URL形式嵌入HTML

## 测试流程

1. 访问 `http://server/bioinf2/edm_web/index.html`
2. 输入示例文本 (点击Example按钮)
3. 提交表单
4. 等待页面自动跳转到结果
5. 查看brief.html和各个result_X.html

## 注意事项

1. **SSH认证**: EDM_server.py需要能够SSH连接到后端服务器
2. **Python环境**: 后端需要安装所有EDM模型依赖
3. **文件权限**: 确保upload和result目录可写
4. **邮件配置**: 如需使用邮件功能,修改send_email.py中的SMTP设置
5. **路径配置**: 根据实际部署调整所有脚本中的路径

## 故障排查

- **任务超时**: 检查后端服务器SSH连接和Python环境
- **文件未传回**: 检查SFTP权限和网络连接
- **3D可视化失败**: 检查JSmol路径和XYZ文件格式
- **邮件发送失败**: 检查SMTP服务器配置和网络

## 与RNAJog的对应关系

| RNAJog | EDM | 说明 |
|--------|-----|------|
| RNAJog.php | EDM.php | 表单处理 |
| RNAJog_server.py | EDM_server.py | 任务调度 |
| RNAJog.sh | EDM.sh | 后端执行 |
| run.py | run_generation.py | 核心计算 |
| processhtml.py | processhtml.py | HTML生成 |
| index.html | index.html | 用户界面 |

## 版本信息
- EDM Model: E(n) Equivariant Diffusion
- JSmol: 16.3.33
- RDKit: Latest
- Python: 3.8+
