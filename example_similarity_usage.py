#!/usr/bin/env python3
"""
example_similarity_usage.py - 分子指纹相似度功能使用示例

演示如何使用fingerprint_similarity模块查找相似分子
"""

from fingerprint_similarity import (
    get_fps,
    find_top_similar_molecules,
    batch_find_similar_molecules,
    format_chembl_url,
    cosine_similarity
)
import numpy as np


def example1_single_molecule():
    """示例1: 查找单个分子的相似分子"""
    print("\n" + "="*60)
    print("示例1: 查找单个分子的相似分子")
    print("="*60 + "\n")

    # 定义要查询的分子（乙醇）
    query_smiles = "CCO"
    chembl_file = "/data/yfang/ChEMBL/fps.npy"

    print(f"查询分子SMILES: {query_smiles}")
    print(f"ChEMBL数据库: {chembl_file}\n")

    # 查找top 5相似分子
    similar_mols = find_top_similar_molecules(query_smiles, chembl_file, top_k=5)

    if similar_mols:
        print(f"找到 {len(similar_mols)} 个相似分子:\n")
        for i, mol in enumerate(similar_mols, start=1):
            print(f"{i}. ChEMBL ID: {mol['chembl_id']}")
            print(f"   SMILES: {mol['smiles']}")
            print(f"   相似度: {mol['similarity']:.4f}")
            print(f"   链接: {format_chembl_url(mol['chembl_id'])}")
            print()
    else:
        print("未找到相似分子")


def example2_batch_molecules():
    """示例2: 批量查找多个分子的相似分子"""
    print("\n" + "="*60)
    print("示例2: 批量查找多个分子的相似分子")
    print("="*60 + "\n")

    # 定义多个要查询的分子
    smiles_list = [
        "CCO",           # 乙醇
        "CC(C)O",        # 异丙醇
        "c1ccccc1",      # 苯
        "CC(=O)O"        # 乙酸
    ]

    chembl_file = "/data/yfang/ChEMBL/fps.npy"

    print(f"查询 {len(smiles_list)} 个分子:")
    for i, smiles in enumerate(smiles_list, start=1):
        print(f"  {i}. {smiles}")
    print()

    # 批量查找（每个分子找top 3）
    results = batch_find_similar_molecules(smiles_list, chembl_file, top_k=3)

    # 打印结果
    for smiles, similar_mols in results.items():
        print(f"\n分子: {smiles}")
        if similar_mols:
            print(f"相似分子 (top 3):")
            for i, mol in enumerate(similar_mols, start=1):
                print(f"  {i}. {mol['chembl_id']}: {mol['smiles'][:40]}... (相似度: {mol['similarity']:.4f})")
        else:
            print("  未找到相似分子")


def example3_calculate_fingerprints():
    """示例3: 计算分子指纹和相似度"""
    print("\n" + "="*60)
    print("示例3: 手动计算分子指纹和相似度")
    print("="*60 + "\n")

    # 两个分子
    smiles1 = "CCO"      # 乙醇
    smiles2 = "CC(C)O"   # 异丙醇

    print(f"分子1: {smiles1}")
    print(f"分子2: {smiles2}\n")

    # 计算指纹
    fp1 = get_fps(smiles1)
    fp2 = get_fps(smiles2)

    if fp1 is not None and fp2 is not None:
        print(f"分子1指纹: 长度={len(fp1)}, 1的数量={np.sum(fp1)}")
        print(f"分子2指纹: 长度={len(fp2)}, 1的数量={np.sum(fp2)}\n")

        # 计算相似度
        similarity = cosine_similarity(fp1, fp2)
        print(f"余弦相似度: {similarity:.4f}")

        # 解释相似度
        if similarity >= 0.9:
            print("→ 非常相似")
        elif similarity >= 0.7:
            print("→ 相似")
        elif similarity >= 0.5:
            print("→ 有一定相似性")
        else:
            print("→ 不太相似")
    else:
        print("指纹计算失败")


def example4_filter_by_similarity():
    """示例4: 根据相似度阈值过滤结果"""
    print("\n" + "="*60)
    print("示例4: 根据相似度阈值过滤结果")
    print("="*60 + "\n")

    query_smiles = "CCO"
    chembl_file = "/data/yfang/ChEMBL/fps.npy"
    similarity_threshold = 0.8

    print(f"查询分子: {query_smiles}")
    print(f"相似度阈值: {similarity_threshold}\n")

    # 先找top 20
    similar_mols = find_top_similar_molecules(query_smiles, chembl_file, top_k=20)

    # 过滤出相似度 >= 阈值的分子
    filtered_mols = [mol for mol in similar_mols if mol['similarity'] >= similarity_threshold]

    print(f"找到 {len(similar_mols)} 个相似分子")
    print(f"相似度 >= {similarity_threshold} 的分子: {len(filtered_mols)} 个\n")

    if filtered_mols:
        print("高相似度分子:")
        for i, mol in enumerate(filtered_mols, start=1):
            print(f"  {i}. {mol['chembl_id']}: {mol['smiles'][:50]}...")
            print(f"     相似度: {mol['similarity']:.4f}")
    else:
        print("没有找到满足阈值的分子")


def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print(" "*15 + "分子指纹相似度功能使用示例")
    print("="*70)

    # 检查ChEMBL数据库文件
    import os
    chembl_file = "/data/yfang/ChEMBL/fps.npy"

    if not os.path.exists(chembl_file):
        print(f"\n警告: ChEMBL数据库文件不存在: {chembl_file}")
        print("某些示例可能无法运行")
        print("\n运行示例3 (不需要数据库文件):")
        example3_calculate_fingerprints()
        return

    # 运行所有示例
    try:
        example1_single_molecule()
        example2_batch_molecules()
        example3_calculate_fingerprints()
        example4_filter_by_similarity()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print(" "*25 + "示例结束")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
