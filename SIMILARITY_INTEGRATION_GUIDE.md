# 分子指纹相似度比较功能 - 集成指南

## 概述

本功能为EDM分子生成系统添加了分子指纹相似度比较功能，能够从ChEMBL数据库（包含约2,878,135个生物活性分子）中找出与生成分子最相似的分子。

## 新增文件

### 1. `fingerprint_similarity.py`
分子指纹相似度比较核心模块

**主要功能：**
- `get_fps(smiles)`: 根据SMILES码生成分子指纹（2048位）
- `cosine_similarity(fp1, fp2)`: 计算两个分子指纹之间的余弦相似度
- `find_top_similar_molecules(query_smiles, chembl_fps_file, top_k=10)`: 在ChEMBL数据库中查找最相似的top-k个分子
- `batch_find_similar_molecules(smiles_list, chembl_fps_file, top_k=10)`: 批量查找相似分子
- `format_chembl_url(chembl_id)`: 生成ChEMBL数据库链接

## 修改的文件

### 1. `processhtml.py`
更新了HTML生成逻辑，添加相似度比较功能

**主要改动：**
- 导入`fingerprint_similarity`模块
- `generate_result_html()`: 在单个分子详情页添加相似分子表格
- `generate_brief_html_with_similarity()`: 新增带相似度信息的概览页面生成函数
- `main()`: 添加`--enable-similarity`命令行参数支持

## 使用方法

### 方法1: 在processhtml.py中启用（推荐）

生成HTML时添加`--enable-similarity`参数：

```bash
python processhtml.py <task_id> <email> --enable-similarity
```

**示例：**
```bash
python processhtml.py 20231204_120000 user@example.com --enable-similarity
```

### 方法2: 独立运行相似度比较

如果已经生成了HTML但想添加相似度信息，可以重新运行processhtml.py：

```bash
cd /data/yfang/EDM_web/1111/web_apps
python processhtml.py <task_id> <email> --enable-similarity
```

### 方法3: 使用Python代码调用

```python
from fingerprint_similarity import find_top_similar_molecules, format_chembl_url

# 单个分子查询
smiles = "CCO"  # 乙醇
chembl_file = "/data/yfang/ChEMBL/fps.npy"

similar_mols = find_top_similar_molecules(smiles, chembl_file, top_k=10)

for i, mol in enumerate(similar_mols, start=1):
    print(f"{i}. {mol['chembl_id']}: {mol['smiles']}")
    print(f"   Similarity: {mol['similarity']:.4f}")
    print(f"   URL: {format_chembl_url(mol['chembl_id'])}")
```

## 数据库文件位置

**ChEMBL指纹数据库：**
```
/data/yfang/ChEMBL/fps.npy
```

**数据格式：**
- 形状：(number, 3)
- 第一列：ChEMBL ID
- 第二列：SMILES码
- 第三列：分子指纹（2048位0/1字符串）

## HTML展示效果

### 1. 单个分子详情页（result_X.html）

在分子详情页底部添加了"相似分子"部分，展示：
- 排名（1-10）
- ChEMBL ID（可点击链接到ChEMBL数据库）
- SMILES码
- 余弦相似度（带颜色标记）
  - 绿色：≥0.9（高相似度）
  - 橙色：0.8-0.9（中等相似度）
  - 灰色：<0.8（低相似度）

### 2. 结果概览页（brief.html）

在概览表格中添加了"最相似分子"列，显示：
- 最高相似度分子的ChEMBL ID
- 相似度徽章（带颜色）
- SMILES码预览
- 其他相似分子数量提示

## 配置选项

### 修改ChEMBL数据库路径

在`processhtml.py`的`main()`函数中修改：

```python
chembl_fps_file = "/data/yfang/ChEMBL/fps.npy"  # 修改为你的路径
```

### 修改返回的相似分子数量

在调用`find_top_similar_molecules`时修改`top_k`参数：

```python
similar_mols = find_top_similar_molecules(smiles, chembl_fps_file, top_k=10)  # 默认10个
```

## 性能考虑

- **处理时间**：对于2,878,135个ChEMBL分子，每个查询分子大约需要10-30秒
- **批量处理**：如果有100个生成的分子，总共需要约15-50分钟
- **优化建议**：
  - 可以使用多进程并行处理多个分子
  - 可以预先构建索引以加速搜索（需要额外开发）

## 数据库连接（可选功能）

根据PDF文档，可以将结果写入MySQL数据库：

```python
import pymysql as mdb
from time import gmtime, strftime

dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
conn = mdb.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='12345',
    db='bioinformatics',
    charset='utf8'
)
cur = conn.cursor()

# 创建TDmol表（如果不存在）
# CREATE TABLE TDmol (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     time DATETIME,
#     task_id VARCHAR(255),
#     smiles TEXT,
#     chembl_id VARCHAR(50),
#     similarity FLOAT
# );

sql = 'INSERT INTO TDmol(time, task_id, smiles, chembl_id, similarity) VALUES (%s, %s, %s, %s, %s)'

for mol in similar_molecules:
    par = (dt, task_id, query_smiles, mol['chembl_id'], mol['similarity'])
    try:
        cur.execute(sql, par)
        conn.commit()
    except:
        conn.rollback()

conn.close()
```

## 故障排查

### 问题1: 找不到ChEMBL数据库文件

**错误信息：**
```
Warning: ChEMBL fingerprint file not found: /data/yfang/ChEMBL/fps.npy
```

**解决方案：**
- 确认文件路径是否正确
- 检查文件是否存在：`ls -l /data/yfang/ChEMBL/fps.npy`
- 检查文件权限：`chmod 644 /data/yfang/ChEMBL/fps.npy`

### 问题2: 导入fingerprint_similarity失败

**错误信息：**
```
Warning: Fingerprint similarity module not available
```

**解决方案：**
- 确认`fingerprint_similarity.py`在正确的目录
- 检查Python路径：`echo $PYTHONPATH`
- 检查RDKit是否正确安装：`python -c "from rdkit import Chem"`

### 问题3: 相似度计算速度慢

**解决方案：**
- 使用NumPy的向量化操作（已优化）
- 考虑使用多进程：
  ```python
  from multiprocessing import Pool

  def process_molecule(smiles):
      return find_top_similar_molecules(smiles, chembl_file, top_k=10)

  with Pool(processes=4) as pool:
      results = pool.map(process_molecule, smiles_list)
  ```

## 测试

测试单个分子的相似度查询：

```bash
cd /data/yfang/EDM_web/1111/web_apps
python fingerprint_similarity.py
```

这将测试乙醇(CCO)的相似分子查找功能。

## 依赖项

- Python 3.7+
- RDKit
- NumPy
- (可选) PyMySQL - 用于数据库集成

安装命令：
```bash
pip install rdkit-pypi numpy pymysql
```

## 注意事项

1. **首次运行**：首次运行时会加载整个ChEMBL数据库（约2.9M分子），可能需要较长时间
2. **内存使用**：fps.npy文件加载后会占用一定内存，建议服务器至少有8GB可用内存
3. **文件编码**：确保所有Python文件使用UTF-8编码
4. **路径问题**：Windows路径使用反斜杠(\\)，Linux使用正斜杠(/)，注意区分

## 后续改进建议

1. **缓存机制**：缓存计算过的相似度结果，避免重复计算
2. **异步处理**：使用异步任务队列（如Celery）处理相似度计算
3. **数据库索引**：构建FAISS或Annoy索引以加速相似度搜索
4. **可视化对比**：在HTML中添加生成分子与相似分子的2D/3D结构对比
5. **批量导出**：添加导出所有相似度结果为CSV或Excel的功能

## 联系支持

如有问题，请参考以下资源：
- RDKit文档：https://www.rdkit.org/docs/
- ChEMBL数据库：https://www.ebi.ac.uk/chembl/
- NumPy文档：https://numpy.org/doc/

---
**版本**：1.0
**更新日期**：2025-12-04
**作者**：Claude Code
