# 相似度功能故障排查指南

## 问题：网页中没有显示相似分子信息

### 快速检查清单

#### 1. 检查文件是否已上传到服务器

在后端服务器 (202.121.180.146:2346) 上检查：

```bash
cd /data/yfang/EDM_web/1111/web_apps

# 检查必需文件是否存在
ls -lh fingerprint_similarity.py
ls -lh processhtml.py

# 检查ChEMBL数据库文件
ls -lh /data/yfang/ChEMBL/fps.npy
```

**预期结果：**
```
-rw-r--r-- 1 yfang yfang  8.5K fingerprint_similarity.py
-rw-r--r-- 1 yfang yfang  15K  processhtml.py
-rw-r--r-- 1 yfang yfang  XX G /data/yfang/ChEMBL/fps.npy
```

如果文件不存在，请上传：
- `fingerprint_similarity.py`
- `processhtml.py`（更新版）

#### 2. 运行诊断脚本

```bash
cd /data/yfang/EDM_web/1111/web_apps
python debug_similarity.py
```

该脚本会检查：
- ✓ fingerprint_similarity模块是否可导入
- ✓ ChEMBL数据库文件是否存在
- ✓ 相似度计算是否正常
- ✓ summary.json中是否有相似度数据
- ✓ HTML中是否包含相似度信息

#### 3. 检查日志输出

查看最近的processhtml.py运行日志：

```bash
tail -n 100 /data/yfang/EDM_web/1111/web_apps/logs/edm_backend.log
```

**寻找以下关键信息：**

✅ **成功的标志：**
```
============================================================
Calculating molecular fingerprint similarity...
============================================================

[1/3] Finding similar molecules for: CCO...
  ✓ Found 10 similar molecules (top: 0.923)
[2/3] Finding similar molecules for: CC(C)O...
  ✓ Found 10 similar molecules (top: 0.856)
...
============================================================
Similarity search completed!
============================================================
```

❌ **失败的标志：**
```
Warning: Fingerprint similarity module not available: No module named 'fingerprint_similarity'
Warning: Similarity module not available, skipping similarity search
```

或者：
```
Warning: ChEMBL database file not found: /data/yfang/ChEMBL/fps.npy
Skipping similarity search...
```

#### 4. 检查summary.json

查看生成的summary.json文件：

```bash
# 假设你的任务ID是20231204_120000
cat /data/yfang/EDM_web/1111/web_apps/result/20231204_120000/summary.json | head -n 50
```

**应该包含：**
```json
{
    "results": [
        {
            "mol_id": "20231204_120000_1",
            "smiles": "CCO",
            "similar_molecules": [
                {
                    "chembl_id": "CHEMBL12345",
                    "smiles": "CC(O)...",
                    "similarity": 0.923
                },
                ...
            ]
        }
    ]
}
```

如果`similar_molecules`字段为空`[]`或不存在，说明相似度计算失败。

#### 5. 检查HTML文件

```bash
# 检查result_1.html是否包含相似度内容
grep "相似分子" /data/yfang/EDM_web/1111/web_apps/result/20231204_120000/result_1.html
grep "ChEMBL ID" /data/yfang/EDM_web/1111/web_apps/result/20231204_120000/result_1.html
```

**应该有输出：**
```html
<h2>相似分子 (来自ChEMBL数据库)</h2>
<th style="width: 20%;">ChEMBL ID</th>
```

如果没有输出，说明HTML中确实没有相似度内容。

## 常见问题及解决方案

### 问题1: fingerprint_similarity模块导入失败

**错误信息：**
```
Warning: Fingerprint similarity module not available: No module named 'fingerprint_similarity'
```

**解决方案：**
```bash
# 1. 确认文件存在
cd /data/yfang/EDM_web/1111/web_apps
ls -lh fingerprint_similarity.py

# 2. 如果不存在，从本地上传
# 在本地：
scp -P 2346 fingerprint_similarity.py yfang@202.121.180.146:/data/yfang/EDM_web/1111/web_apps/

# 3. 检查Python能否导入
python -c "from fingerprint_similarity import get_fps; print('OK')"
```

### 问题2: ChEMBL数据库文件不存在

**错误信息：**
```
Warning: ChEMBL database file not found: /data/yfang/ChEMBL/fps.npy
```

**解决方案：**
```bash
# 1. 检查文件是否在其他位置
find /data/yfang -name "fps.npy" 2>/dev/null

# 2. 如果找到但路径不同，修改processhtml.py中的路径
# 编辑 processhtml.py 第293行：
# chembl_fps_file = "/data/yfang/ChEMBL/fps.npy"  # 改为实际路径

# 3. 如果文件不存在，需要准备该文件
# 参考PDF文档中的说明
```

### 问题3: 使用了旧版本的processhtml.py

**症状：**
- 日志中没有"Calculating molecular fingerprint similarity..."
- 或者需要添加--enable-similarity参数

**解决方案：**
```bash
# 1. 检查processhtml.py版本
head -n 30 /data/yfang/EDM_web/1111/web_apps/processhtml.py | grep "fingerprint_similarity"

# 应该看到：
# from fingerprint_similarity import find_top_similar_molecules, format_chembl_url

# 2. 如果没有，上传新版本
scp -P 2346 processhtml.py yfang@202.121.180.146:/data/yfang/EDM_web/1111/web_apps/

# 3. 备份旧版本（可选）
cp processhtml.py processhtml.py.bak
```

### 问题4: 相似度计算完成但HTML中没显示

**可能原因：**
- summary.json中有数据，但HTML生成时出错
- 浏览器缓存了旧的HTML

**解决方案：**
```bash
# 1. 手动重新生成HTML
cd /data/yfang/EDM_web/1111/web_apps
python processhtml.py <task_id> <email>

# 2. 检查生成的HTML文件
grep -A 5 "相似分子" result/<task_id>/result_1.html

# 3. 清除浏览器缓存，强制刷新页面（Ctrl+F5）
```

## 完整测试流程

### 测试步骤

```bash
# 1. 进入工作目录
cd /data/yfang/EDM_web/1111/web_apps

# 2. 激活conda环境
conda activate edm_web

# 3. 运行诊断脚本
python debug_similarity.py

# 4. 如果诊断通过，测试单个分子
python -c "
from fingerprint_similarity import find_top_similar_molecules
similar = find_top_similar_molecules('CCO', '/data/yfang/ChEMBL/fps.npy', top_k=3)
print(f'Found {len(similar)} similar molecules')
for mol in similar:
    print(f'  {mol[\"chembl_id\"]}: {mol[\"similarity\"]:.3f}')
"

# 5. 重新运行processhtml.py（使用实际的task_id）
python processhtml.py <your_task_id> <your_email>

# 6. 检查生成的HTML
cat result/<your_task_id>/summary.json | python -m json.tool | head -n 30
grep "相似分子" result/<your_task_id>/result_1.html
```

### 预期输出

**诊断脚本：**
```
============================================================
相似度功能诊断工具
============================================================

[1] 检查fingerprint_similarity模块...
✓ fingerprint_similarity模块导入成功

[2] 检查ChEMBL数据库文件...
  数据库路径: /data/yfang/ChEMBL/fps.npy
✓ ChEMBL数据库文件存在
  文件大小: 5432.12 MB

[3] 测试相似度计算...
  测试分子SMILES: CCO
  正在计算分子指纹...
  ✓ 分子指纹生成成功 (长度: 2048)
  正在查找相似分子 (可能需要几秒钟)...
✓ 相似度计算成功，找到 3 个相似分子

  Top 3 相似分子:
    1. CHEMBL12345: 0.923
    2. CHEMBL67890: 0.856
    3. CHEMBL11111: 0.812
```

**processhtml.py：**
```
============================================================
Calculating molecular fingerprint similarity...
============================================================

[1/3] Finding similar molecules for: CCO...
  ✓ Found 10 similar molecules (top: 0.923)
[2/3] Finding similar molecules for: CC(C)O...
  ✓ Found 10 similar molecules (top: 0.856)
[3/3] Finding similar molecules for: c1ccccc1...
  ✓ Found 10 similar molecules (top: 0.789)

============================================================
Similarity search completed!
============================================================

Generating HTML pages...
  Generated: result_1.html
  Generated: result_2.html
  Generated: result_3.html
  Generated: brief.html

============================================================
HTML generation completed for task 20231204_120000
============================================================
```

## 需要帮助？

如果以上步骤都无法解决问题，请提供以下信息：

1. **诊断脚本输出：**
   ```bash
   python debug_similarity.py > debug_output.txt 2>&1
   ```

2. **processhtml.py日志：**
   ```bash
   tail -n 200 /data/yfang/EDM_web/1111/web_apps/logs/edm_backend.log > processhtml_log.txt
   ```

3. **文件列表：**
   ```bash
   ls -lh /data/yfang/EDM_web/1111/web_apps/*.py > file_list.txt
   ls -lh /data/yfang/ChEMBL/ >> file_list.txt
   ```

4. **summary.json示例：**
   ```bash
   head -n 50 result/<task_id>/summary.json > summary_sample.txt
   ```

将这些文件提供给技术支持以快速定位问题。
