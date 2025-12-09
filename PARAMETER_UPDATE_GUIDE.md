# 参数控制更新说明

## 📝 更新摘要

现在可以在 `run_generation.py` 中控制 `model_runner.py` 的生成参数，并且**所有生成的有效分子都会被展示**（不再是从100个样本中只选3个）。

---

## 🔧 新增功能

### 1. 可配置参数

在 `run_generation.py` 中添加了两个命令行参数：

```bash
--num_molecules <数量>      # 要生成的分子数量（默认：100）
--guidance_scale <数值>      # 引导尺度（默认：5.0）
```

### 2. 展示所有有效分子

- **旧行为**：生成100个样本 → 选择第一个有效分子 → 重复3次 → 展示3个分子
- **新行为**：生成N个分子 → 展示所有有效分子（跳过无效分子）

---

## 📋 修改的文件

### 1. `model_runner.py`

**修改内容**：
- `generate_and_evaluate_for_webapp()` 函数现在接受两个新参数：
  - `num_samples`: 要生成的分子数量
  - `guidance_scale`: 引导尺度
- 返回**所有生成的有效分子列表**（而不是只返回第一个）

**关键代码**：
```python
def generate_and_evaluate_for_webapp(user_input, model_objects, task_id,
                                     num_samples=100, guidance_scale=5.0):
    """
    参数:
        num_samples: 要生成的分子数量（默认100）
        guidance_scale: 引导尺度（默认5.0）

    返回:
        generated_molecules: 生成的所有有效分子列表
        evaluation_summary: 评估摘要
    """
    # 生成所有分子并返回有效的
    for i in range(num_samples):
        mol_dict, smiles = _generate_single_molecule_in_memory(
            user_input, model_objects, scale=guidance_scale
        )
        if smiles and smiles != 'Invalid Molecule':
            generated_molecules.append(molecule_data)
```

### 2. `run_generation.py`

**修改内容**：
- 添加命令行参数 `--num_molecules` 和 `--guidance_scale`
- 一次性调用 `generate_and_evaluate_for_webapp()` 生成所有分子
- 保存所有有效分子到文件

**关键代码**：
```python
parser.add_argument('--num_molecules', type=int, default=100,
                   help='Number of molecules to generate (default: 100)')
parser.add_argument('--guidance_scale', type=float, default=5.0,
                   help='Guidance scale for generation (default: 5.0)')

# 调用生成函数
generated_molecules, evaluation_summary = generate_and_evaluate_for_webapp(
    user_input, model_objects, args.task_id,
    num_samples=num_molecules,
    guidance_scale=guidance_scale
)

# 保存所有有效分子
for i, molecule in enumerate(generated_molecules, start=1):
    save_molecule_files(molecule, args.task_id, i, args.output_dir)
```

### 3. `EDM.sh`

**修改内容**：
- 接受两个新的可选参数：`$3` (num_molecules) 和 `$4` (guidance_scale)
- 如果不提供，使用默认值：100个分子，guidance_scale=5.0

**关键代码**：
```bash
# 参数:
# $1 = email
# $2 = timeVar (任务ID)
# $3 = num_molecules (可选，默认100)
# $4 = guidance_scale (可选，默认5.0)

NUM_MOLECULES=${3:-100}
GUIDANCE_SCALE=${4:-5.0}

$PYTHON_CMD ./run_generation.py \
    --task_id "$2" \
    --input_file "$BASE_DIR/upload/${2}.txt" \
    --output_dir "$BASE_DIR/result/${2}/" \
    --num_molecules "$NUM_MOLECULES" \
    --guidance_scale "$GUIDANCE_SCALE"
```

### 4. `processhtml.py`

**修改内容**：
- 移除了"有效分子比例"列（因为现在只展示有效分子）
- 自动适应任意数量的分子

**关键改动**：
- 移除了表格中的"有效率"列
- 移除了详情页面中的"有效分子比例"信息

---

## 🚀 使用方法

### 方法1: 使用默认参数（推荐）

生成100个分子，guidance_scale=5.0：

```bash
bash EDM.sh "" "task_20231128001"
```

### 方法2: 指定分子数量

生成50个分子：

```bash
bash EDM.sh "" "task_20231128001" 50
```

### 方法3: 指定分子数量和guidance_scale

生成200个分子，guidance_scale=7.0：

```bash
bash EDM.sh "" "task_20231128001" 200 7.0
```

### 方法4: 直接调用 run_generation.py

```bash
python run_generation.py \
    --task_id "test123" \
    --input_file "upload/test123.txt" \
    --output_dir "result/test123/" \
    --num_molecules 50 \
    --guidance_scale 6.0
```

---

## 📊 输出变化

### summary.json 新增字段

```json
{
    "task_id": "20231128001",
    "user_input": "A molecule with benzene rings",
    "num_molecules": 100,          // 新增：尝试生成的数量
    "guidance_scale": 5.0,         // 新增：使用的guidance scale
    "total_generated": 87,         // 新增：实际生成的有效分子数
    "total_attempted": 100,        // 新增：尝试生成的总数
    "valid_count": 87,             // 新增：有效分子数
    "invalid_count": 13,           // 新增：无效分子数
    "processing_time": "1250.45",
    "results": [...]
}
```

### 控制台输出

新的输出格式更清晰：

```
开始为任务 test123 生成 100 个分子...
使用 guidance_scale = 5.0

生成分子 1/100... ✓ 有效 (SMILES: CC(C)C1=CC=CC=C1...)
生成分子 2/100... ✗ 无效
生成分子 3/100... ✓ 有效 (SMILES: C1=CC=C(C=C1)O...)
...

============================================================
生成完成！
  有效分子数: 87/100
  无效分子数: 13/100
  任务 test123 总耗时: 1250.45 秒
============================================================
```

---

## 🎯 关键变化总结

| 项目 | 旧行为 | 新行为 |
|------|--------|--------|
| 生成方式 | 生成100个样本，选第一个有效的，重复3次 | 生成N个分子，返回所有有效的 |
| 展示数量 | 固定3个分子 | 所有有效分子（可能是50、87、100等） |
| 参数控制 | 硬编码在代码中 | 通过命令行参数控制 |
| 有效率显示 | 显示"有效分子比例: 15/100" | 只展示有效分子，不显示比例 |
| guidance_scale | 固定5.0 | 可配置（默认5.0） |

---

## 🔄 向后兼容性

**完全兼容！**

如果不提供新参数，系统使用默认值：
- 生成100个分子
- guidance_scale = 5.0

现有的调用方式无需修改：
```bash
# 这个命令仍然有效
bash EDM.sh "" "task_20231128001"
```

---

## 💡 推荐配置

根据不同需求选择参数：

### 快速测试
```bash
bash EDM.sh "" "test" 10 5.0
# 10个分子，快速验证系统
```

### 标准使用
```bash
bash EDM.sh "" "task001" 100 5.0
# 100个分子，平衡质量和速度（默认）
```

### 高质量生成
```bash
bash EDM.sh "" "task002" 200 7.0
# 200个分子，更高的guidance scale
```

### 探索性生成
```bash
bash EDM.sh "" "task003" 500 3.0
# 500个分子，较低的guidance scale增加多样性
```

---

## 📌 注意事项

1. **无效分子不会被展示**：如果生成100个分子，但只有70个有效，则只展示70个
2. **处理时间线性增长**：生成200个分子大约需要生成100个分子的2倍时间
3. **guidance_scale 影响**：
   - 较低值（3.0-4.0）：更多样化，但可能更多无效分子
   - 中等值（5.0-6.0）：平衡质量和多样性（推荐）
   - 较高值（7.0-10.0）：更符合描述，但多样性降低

---

## 版本信息

- 更新日期：2025-11-28
- 版本：2.0
- 向后兼容：是
