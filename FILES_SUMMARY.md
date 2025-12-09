# EDM Web Application - 文件清单

## 完成的所有文件

### 1. 前端文件

#### web_apps/templates/index.html
- **作用**: 用户界面,接收分子描述输入
- **关键功能**:
  - 用户输入文本框 (user_text)
  - 邮箱输入框 (可选)
  - 表单提交到 EDM.php
  - JavaScript表单验证
  - 示例填充功能
- **修改**: 完全仿照RNAJog的表单结构

#### web_apps/EDM.php
- **作用**: 处理表单提交,启动后端任务
- **关键功能**:
  - 生成唯一任务ID (timeVar)
  - 保存用户输入到文本文件
  - 创建upload和result目录
  - 调用 EDM_server.py
  - 跳转到 waiting.html
- **参数**: email, task_id

#### web_apps/waiting.html
- **作用**: 等待页面,显示处理状态
- **关键功能**:
  - 显示任务ID
  - Loading动画
  - AJAX定期检查结果文件
  - 自动跳转到结果页面
  - 防止用户刷新

#### web_apps/EDM_server.py
- **作用**: 任务调度,连接前后端
- **关键功能**:
  - 使用paramiko进行SSH连接
  - 上传用户输入文件到2349服务器
  - 在远程执行 EDM.sh
  - 下载所有结果文件 (HTML, XYZ, SDF)
- **参数**: email, task_id

### 2. 后端文件

#### web_apps/EDM.sh
- **作用**: 后端主执行脚本
- **关键功能**:
  - 创建结果目录
  - 调用 run_generation.py 生成分子
  - 调用 processhtml.py 生成HTML
  - 调用 send_email.py 发送邮件(如果有邮箱)
- **参数**: email, task_id

#### web_apps/run_generation.py
- **作用**: 分子生成核心脚本
- **关键功能**:
  - 读取用户输入文本
  - 调用 model_runner.py 初始化模型
  - 生成3个分子 (默认)
  - 保存XYZ和SDF文件
  - 生成summary.json
- **参数**: task_id, input_file, output_dir
- **输出**:
  - molecule_X.xyz
  - molecule_X.sdf
  - summary.json

#### web_apps/processhtml.py
- **作用**: 生成HTML结果页面
- **关键功能**:
  - 读取summary.json
  - 生成2D分子图像 (RDKit)
  - 生成XYZ文件的Base64编码
  - 创建 result_X.html (包含JSmol 3D可视化)
  - 创建 brief.html (结果概览)
- **参数**: task_id, email
- **输出**:
  - brief.html
  - result_1.html, result_2.html, result_3.html

#### web_apps/send_email.py
- **作用**: 发送结果通知邮件
- **关键功能**:
  - SMTP邮件发送
  - HTML格式邮件
  - 包含结果链接
- **参数**: email, task_id

### 3. 支持文件 (保留原有功能)

#### web_apps/model_runner.py
- **作用**: 模型运行器
- **关键函数**:
  - `initialize_models()`: 初始化EDM模型
  - `generate_and_evaluate_for_webapp()`: 生成分子
  - `_generate_single_molecule_in_memory()`: 内存中生成单个分子
  - `numpy_to_xyz_string()`: 转换坐标为XYZ格式

#### web_apps/app.py
- **作用**: 原始应用脚本 (功能保留)
- **说明**: 现在通过run_generation.py封装调用

### 4. 文档文件

#### web_apps/README_WORKFLOW.md
- **作用**: 系统架构和工作流程文档
- **内容**:
  - 系统架构图
  - 文件说明
  - 数据流说明
  - 部署指南
  - 测试流程
  - 故障排查

#### web_apps/FILES_SUMMARY.md (本文件)
- **作用**: 文件清单和总结

## 数据流示意图

```
用户输入 (文本)
    ↓
index.html
    ↓
EDM.php (生成task_id, 保存输入)
    ↓
EDM_server.py (上传到2349)
    ↓
EDM.sh (后端执行)
    ↓
run_generation.py (生成分子)
    ↓
processhtml.py (生成HTML)
    ↓
send_email.py (发送邮件, 可选)
    ↓
EDM_server.py (下载结果)
    ↓
用户查看结果 (brief.html, result_X.html)
```

## 生成的结果文件

对于每个任务 (task_id), 生成以下文件:

```
/var/www/bioinf2/edm_web/result/
└── {task_id}_brief.html        # 前端概览页面
└── {task_id}/
    ├── brief.html              # 后端概览页面 (传回)
    ├── result_1.html           # 分子1详情
    ├── result_2.html           # 分子2详情
    ├── result_3.html           # 分子3详情
    ├── molecule_1.xyz          # 分子1坐标
    ├── molecule_1.sdf          # 分子1结构
    ├── molecule_2.xyz
    ├── molecule_2.sdf
    ├── molecule_3.xyz
    ├── molecule_3.sdf
    └── summary.json            # 任务摘要
```

## 关键技术点

### 1. 3D分子可视化
- **库**: JSmol
- **数据格式**: XYZ坐标 → Base64编码 → 嵌入HTML
- **渲染**: JavaScript初始化JSmol Applet
- **交互**: 用户可旋转、缩放3D分子模型

### 2. 2D分子可视化
- **库**: RDKit
- **数据格式**: SMILES → PNG图像 → Base64 Data URL
- **显示**: 直接在HTML中作为img标签的src

### 3. 文件传输
- **协议**: SSH/SFTP (paramiko)
- **端口**: 2349
- **方向**:
  - 前端→后端: 用户输入文件
  - 后端→前端: 所有结果文件

### 4. 任务管理
- **任务ID**: 时间戳 + 随机MD5
- **状态跟踪**: AJAX轮询检查文件存在性
- **超时处理**: 最多等待10分钟

### 5. 邮件通知
- **协议**: SMTP
- **服务器**: smtp.163.com
- **格式**: HTML邮件,包含结果链接

## 与RNAJog的对应关系

| 功能 | RNAJog实现 | EDM实现 | 说明 |
|------|-----------|---------|------|
| 前端界面 | index.html | index.html | 完全仿照 |
| 表单处理 | RNAJog.php | EDM.php | 逻辑相同 |
| 任务调度 | RNAJog_server.py | EDM_server.py | SSH/SFTP传输 |
| 后端执行 | RNAJog.sh | EDM.sh | Shell脚本 |
| 核心计算 | run.py | run_generation.py | Python脚本 |
| HTML生成 | processhtml.py | processhtml.py | 相同概念 |
| 等待页面 | (内嵌) | waiting.html | 独立页面 |
| 邮件发送 | mail.py | send_email.py | SMTP |

## 参数传递链

```
用户输入参数:
- user_text: 分子描述文本
- email: 邮箱地址 (可选)

系统生成参数:
- task_id: 唯一任务标识符

传递链:
EDM.php
  ↓ (email, task_id)
EDM_server.py
  ↓ (email, task_id)
EDM.sh
  ↓ (task_id, input_file, output_dir)
run_generation.py
  + (task_id, email)
  processhtml.py
  + (email, task_id)
  send_email.py
```

## 部署检查清单

### 前端服务器
- [ ] index.html 放置在正确位置
- [ ] EDM.php 有执行权限
- [ ] waiting.html 可访问
- [ ] EDM_server.py 有执行权限
- [ ] upload/ 目录可写
- [ ] result/ 目录可写
- [ ] Python3 已安装 paramiko

### 后端服务器
- [ ] EDM.sh 有执行权限
- [ ] run_generation.py 可执行
- [ ] processhtml.py 可执行
- [ ] send_email.py 可执行
- [ ] model_runner.py 及依赖完整
- [ ] upload/ 目录可写
- [ ] result/ 目录可写
- [ ] Python环境包含所有EDM依赖
- [ ] JSmol库已部署

### 网络配置
- [ ] 前端可SSH到后端(2349端口)
- [ ] 前端可SFTP到后端(2349端口)
- [ ] SMTP服务器可访问(邮件功能)
- [ ] 防火墙规则允许相关连接

## 测试用例

### 测试1: 基本功能
1. 输入: "A small aromatic molecule with benzene ring"
2. 不填邮箱
3. 提交
4. 预期: 生成3个分子,显示3D和2D结构

### 测试2: 带邮箱
1. 输入: "Molecule with hydroxyl groups"
2. 填写邮箱: test@example.com
3. 提交
4. 预期: 生成结果 + 收到邮件

### 测试3: 长文本
1. 输入: 100字符的详细描述
2. 提交
3. 预期: 正常生成

### 测试4: 特殊字符
1. 输入: 包含引号、逗号等特殊字符
2. 提交
3. 预期: 正确处理转义

## 后续优化建议

1. **性能优化**
   - 实现任务队列系统
   - 缓存模型加载
   - 并行生成多个分子

2. **用户体验**
   - 实时进度条
   - WebSocket实时推送
   - 历史任务查询

3. **功能扩展**
   - 用户自定义生成数量
   - 多种可视化模式
   - 结果下载打包

4. **安全加固**
   - 输入验证强化
   - SQL注入防护
   - 文件上传限制

## 维护联系

- 开发者: [Your Name]
- 邮箱: support@example.com
- 最后更新: 2025-11-28
