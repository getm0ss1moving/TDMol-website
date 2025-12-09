#!/usr/bin/env python3
"""
debug_similarity.py - 诊断相似度功能问题

检查：
1. fingerprint_similarity模块是否可导入
2. ChEMBL数据库文件是否存在
3. 相似度计算是否正常
4. summary.json中是否有相似度数据
5. HTML中是否包含相似度信息
"""

import os
import sys
import json

print("="*60)
print("相似度功能诊断工具")
print("="*60)

# 1. 检查fingerprint_similarity模块
print("\n[1] 检查fingerprint_similarity模块...")
try:
    from fingerprint_similarity import find_top_similar_molecules, get_fps, format_chembl_url
    print("✓ fingerprint_similarity模块导入成功")
except ImportError as e:
    print(f"✗ fingerprint_similarity模块导入失败: {e}")
    print("  请确认fingerprint_similarity.py在当前目录")
    sys.exit(1)

# 2. 检查ChEMBL数据库文件
print("\n[2] 检查ChEMBL数据库文件...")
chembl_file = "/data/yfang/ChEMBL/fps.npy"
print(f"  数据库路径: {chembl_file}")

if os.path.exists(chembl_file):
    file_size = os.path.getsize(chembl_file) / (1024 * 1024)  # MB
    print(f"✓ ChEMBL数据库文件存在")
    print(f"  文件大小: {file_size:.2f} MB")
else:
    print(f"✗ ChEMBL数据库文件不存在: {chembl_file}")
    print("  相似度功能将无法工作")
    print("\n可能的解决方案:")
    print("  1. 检查文件路径是否正确")
    print("  2. 确认文件已从2346服务器正确下载")
    print("  3. 检查文件权限")
    sys.exit(1)

# 3. 测试相似度计算
print("\n[3] 测试相似度计算...")
test_smiles = "CCO"  # 乙醇
print(f"  测试分子SMILES: {test_smiles}")

try:
    print("  正在计算分子指纹...")
    fp = get_fps(test_smiles)
    if fp is not None:
        print(f"  ✓ 分子指纹生成成功 (长度: {len(fp)})")
    else:
        print(f"  ✗ 分子指纹生成失败")
        sys.exit(1)

    print("  正在查找相似分子 (可能需要几秒钟)...")
    similar_mols = find_top_similar_molecules(test_smiles, chembl_file, top_k=3)

    if similar_mols:
        print(f"✓ 相似度计算成功，找到 {len(similar_mols)} 个相似分子")
        print("\n  Top 3 相似分子:")
        for i, mol in enumerate(similar_mols, start=1):
            print(f"    {i}. {mol['chembl_id']}: {mol['similarity']:.3f}")
    else:
        print("✗ 未找到相似分子")

except Exception as e:
    print(f"✗ 相似度计算失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 检查是否有任务结果目录
print("\n[4] 检查任务结果...")
result_base = "/data/yfang/EDM_web/1111/web_apps/result/"

if not os.path.exists(result_base):
    print(f"  结果目录不存在: {result_base}")
    print("  跳过任务检查")
else:
    # 列出最近的任务
    tasks = sorted([d for d in os.listdir(result_base) if os.path.isdir(os.path.join(result_base, d))])

    if tasks:
        print(f"  找到 {len(tasks)} 个任务目录")
        latest_task = tasks[-1]
        print(f"  最新任务: {latest_task}")

        # 检查summary.json
        summary_file = os.path.join(result_base, latest_task, "summary.json")
        if os.path.exists(summary_file):
            print(f"\n  检查 summary.json...")
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)

            results = summary_data.get('results', [])
            print(f"    分子数量: {len(results)}")

            if results:
                first_mol = results[0]
                print(f"    第一个分子SMILES: {first_mol.get('smiles', 'N/A')}")

                # 检查是否有相似度数据
                similar_mols = first_mol.get('similar_molecules', [])
                if similar_mols:
                    print(f"    ✓ 找到相似度数据: {len(similar_mols)} 个相似分子")
                    print(f"      Top相似分子: {similar_mols[0]['chembl_id']} (相似度: {similar_mols[0]['similarity']:.3f})")
                else:
                    print(f"    ✗ 没有相似度数据 (similar_molecules字段为空)")
                    print("\n    可能原因:")
                    print("      1. processhtml.py运行时ChEMBL数据库不存在")
                    print("      2. processhtml.py运行时fingerprint_similarity模块导入失败")
                    print("      3. 相似度计算出错但被忽略")

        # 检查result_1.html
        result_html = os.path.join(result_base, latest_task, "result_1.html")
        if os.path.exists(result_html):
            print(f"\n  检查 result_1.html...")
            with open(result_html, 'r', encoding='utf-8') as f:
                html_content = f.read()

            if "相似分子" in html_content or "ChEMBL" in html_content:
                print(f"    ✓ HTML包含相似度内容")
                if "ChEMBL ID" in html_content:
                    print(f"    ✓ 找到相似分子表格")
            else:
                print(f"    ✗ HTML中没有相似度内容")
                print("\n    可能原因:")
                print("      1. summary.json中没有similar_molecules数据")
                print("      2. processhtml.py版本过旧")
    else:
        print(f"  没有找到任务目录")

# 5. 给出建议
print("\n" + "="*60)
print("诊断总结")
print("="*60)
print("\n如果相似度功能不工作，可能的原因:")
print("  1. ChEMBL数据库文件路径不正确")
print("  2. processhtml.py未更新到最新版本")
print("  3. fingerprint_similarity.py未部署到服务器")
print("  4. 相似度计算时发生错误但被静默忽略")
print("\n建议操作:")
print("  1. 确认以下文件已上传到服务器:")
print("     - fingerprint_similarity.py")
print("     - processhtml.py (更新版)")
print("  2. 确认ChEMBL数据库文件存在:")
print(f"     - {chembl_file}")
print("  3. 重新运行processhtml.py:")
print("     python processhtml.py <task_id> <email>")
print("  4. 检查日志输出是否有错误信息")
print("\n" + "="*60)
