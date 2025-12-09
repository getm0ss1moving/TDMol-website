#!/usr/bin/env python3
"""
benchmark_similarity.py - 分子指纹相似度计算性能测试

用于测试向量化优化后的性能提升
"""

import time
import numpy as np
from fingerprint_similarity import find_top_similar_molecules, get_fps


def benchmark_single_molecule(smiles, chembl_file, top_k=10):
    """测试单个分子的查询性能"""
    print(f"\n{'='*60}")
    print(f"测试单个分子查询性能")
    print(f"{'='*60}")
    print(f"查询分子: {smiles}")
    print(f"Top-K: {top_k}")
    print()

    start_time = time.time()
    similar_mols = find_top_similar_molecules(smiles, chembl_file, top_k)
    elapsed_time = time.time() - start_time

    print(f"\n结果：")
    print(f"  找到 {len(similar_mols)} 个相似分子")
    print(f"  耗时: {elapsed_time:.2f} 秒")

    if similar_mols:
        print(f"\nTop 3 相似分子:")
        for i, mol in enumerate(similar_mols[:3], start=1):
            print(f"  {i}. {mol['chembl_id']}: {mol['similarity']:.3f}")

    return elapsed_time


def benchmark_batch_molecules(smiles_list, chembl_file, top_k=10):
    """测试批量分子查询性能"""
    print(f"\n{'='*60}")
    print(f"测试批量分子查询性能")
    print(f"{'='*60}")
    print(f"分子数量: {len(smiles_list)}")
    print(f"Top-K: {top_k}")
    print()

    times = []
    total_start = time.time()

    for i, smiles in enumerate(smiles_list, start=1):
        print(f"[{i}/{len(smiles_list)}] 处理: {smiles[:40]}...")

        start_time = time.time()
        similar_mols = find_top_similar_molecules(smiles, chembl_file, top_k)
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)

        if similar_mols:
            print(f"  ✓ 耗时: {elapsed_time:.2f}秒, Top相似度: {similar_mols[0]['similarity']:.3f}")
        else:
            print(f"  ✗ 未找到相似分子")

    total_time = time.time() - total_start
    avg_time = np.mean(times)
    min_time = np.min(times)
    max_time = np.max(times)

    print(f"\n{'='*60}")
    print(f"批量处理性能统计")
    print(f"{'='*60}")
    print(f"总分子数: {len(smiles_list)}")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均耗时: {avg_time:.2f} 秒/分子")
    print(f"最快: {min_time:.2f} 秒")
    print(f"最慢: {max_time:.2f} 秒")
    print(f"{'='*60}")

    return total_time, avg_time


def estimate_performance(num_molecules, avg_time_per_mol):
    """估算大规模处理时间"""
    print(f"\n{'='*60}")
    print(f"性能估算（基于当前测试结果）")
    print(f"{'='*60}")

    test_cases = [10, 50, 100, 200, 500, 1000]

    for n in test_cases:
        estimated_time = n * avg_time_per_mol
        minutes = estimated_time / 60
        hours = estimated_time / 3600

        if hours >= 1:
            time_str = f"{hours:.2f} 小时"
        elif minutes >= 1:
            time_str = f"{minutes:.2f} 分钟"
        else:
            time_str = f"{estimated_time:.2f} 秒"

        print(f"  {n:4d} 个分子: 约 {time_str}")

    print(f"{'='*60}")


def main():
    """运行性能测试"""
    import os

    chembl_file = "/data/yfang/ChEMBL/fps.npy"

    print("\n" + "="*70)
    print(" "*15 + "分子指纹相似度性能测试")
    print("="*70)

    # 检查数据库文件
    if not os.path.exists(chembl_file):
        print(f"\n错误: ChEMBL数据库文件不存在: {chembl_file}")
        print("请修改 chembl_file 变量为正确的路径")
        return

    # 测试用分子
    test_smiles = [
        "CCO",                          # 乙醇
        "CC(C)O",                       # 异丙醇
        "c1ccccc1",                     # 苯
        "CC(=O)O",                      # 乙酸
        "CC(C)CC1=CC=C(C=C1)C(C)C",    # 布洛芬
    ]

    print(f"\nChEMBL数据库: {chembl_file}")
    print(f"测试分子数量: {len(test_smiles)}")

    # 测试1: 单个分子查询
    single_time = benchmark_single_molecule(test_smiles[0], chembl_file, top_k=10)

    # 测试2: 批量查询
    total_time, avg_time = benchmark_batch_molecules(test_smiles, chembl_file, top_k=10)

    # 性能估算
    estimate_performance(100, avg_time)

    # 性能评级
    print(f"\n{'='*60}")
    print(f"性能评级")
    print(f"{'='*60}")

    if avg_time < 1:
        grade = "优秀"
        emoji = "🚀"
    elif avg_time < 2:
        grade = "良好"
        emoji = "✅"
    elif avg_time < 5:
        grade = "一般"
        emoji = "⚠️"
    else:
        grade = "较慢"
        emoji = "🐌"

    print(f"{emoji} 平均查询速度: {avg_time:.2f} 秒/分子 - {grade}")

    if avg_time < 2:
        print("\n✨ 恭喜！你的系统性能达到了优化后的预期速度！")
        print("   100个分子的批量处理预计只需要 1-3 分钟。")
    elif avg_time < 5:
        print("\n💡 提示：性能可接受，但可能受服务器负载影响。")
        print("   建议在服务器空闲时运行大规模计算。")
    else:
        print("\n⚠️  警告：性能低于预期，可能的原因：")
        print("   1. 服务器性能较低")
        print("   2. ChEMBL数据库文件I/O较慢")
        print("   3. NumPy未使用优化的BLAS库")

    print(f"\n{'='*70}")
    print(" "*25 + "测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
