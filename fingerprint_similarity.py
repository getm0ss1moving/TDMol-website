#!/usr/bin/env python3
"""
fingerprint_similarity.py - 分子指纹相似度比较模块
根据ChEMBL数据库计算分子指纹的余弦相似度，找出最相似的分子
"""

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from typing import List, Tuple, Dict
import os


def get_fps(smiles: str, fp_size: int = 256) -> np.ndarray:
    """
    根据SMILES码生成分子指纹

    Args:
        smiles: SMILES字符串
        fp_size: 指纹长度（默认256，需与ChEMBL数据库一致）

    Returns:
        0/1数组，表示分子指纹
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None

        # 使用RDKFingerprint生成指纹，指定长度为256以匹配ChEMBL数据库
        fp = Chem.RDKFingerprint(mol, fpSize=fp_size)

        # 将指纹转换为numpy数组
        fp_array = np.zeros((fp_size,), dtype=np.int8)
        for i in range(fp_size):
            fp_array[i] = fp[i]

        return fp_array
    except Exception as e:
        print(f"Error generating fingerprint for SMILES {smiles}: {e}")
        return None


def cosine_similarity(fp1: np.ndarray, fp2: np.ndarray) -> float:
    """
    计算两个分子指纹之间的余弦相似度

    Args:
        fp1: 第一个分子指纹
        fp2: 第二个分子指纹

    Returns:
        余弦相似度值 (0-1之间)
    """
    # 计算点积
    dot_product = np.dot(fp1, fp2)

    # 计算模长
    norm1 = np.linalg.norm(fp1)
    norm2 = np.linalg.norm(fp2)

    # 避免除以零
    if norm1 == 0 or norm2 == 0:
        return 0.0

    # 余弦相似度
    similarity = dot_product / (norm1 * norm2)

    return float(similarity)


def find_top_similar_molecules(
    query_smiles: str,
    chembl_fps_file: str,
    top_k: int = 10
) -> List[Dict[str, any]]:
    """
    在ChEMBL数据库中查找与给定分子最相似的top-k个分子（优化版）

    使用向量化操作批量计算所有分子的余弦相似度，大幅提升性能

    Args:
        query_smiles: 待查询分子的SMILES码
        chembl_fps_file: ChEMBL指纹数据库文件路径 (fps.npy)
        top_k: 返回相似度最高的前k个分子 (默认10)

    Returns:
        相似分子列表，每个元素包含: {
            'chembl_id': ChEMBL ID,
            'smiles': SMILES码,
            'similarity': 余弦相似度
        }
    """
    # 检查数据库文件是否存在
    if not os.path.exists(chembl_fps_file):
        print(f"Warning: ChEMBL fingerprint file not found: {chembl_fps_file}")
        return []

    try:
        # 先加载ChEMBL指纹数据库以确定指纹长度
        # 格式: (number, 3) - [ID, SMILES, FPS]
        chembl_data = np.load(chembl_fps_file, allow_pickle=True)

        # 检查第一个指纹的长度
        num_mols = len(chembl_data)
        first_fp_str = chembl_data[0][2]

        # 确定数据库中的指纹长度
        if isinstance(first_fp_str, str):
            fp_length = len(first_fp_str)
        else:
            fp_length = len(first_fp_str)

        print(f"  Database fingerprint length: {fp_length}")

        # 生成查询分子的指纹，使用与数据库相同的长度
        query_fp = get_fps(query_smiles, fp_size=fp_length)
        if query_fp is None:
            print(f"Warning: Failed to generate fingerprint for query SMILES: {query_smiles}")
            return []

        # 提取所有指纹并转换为矩阵（极速向量化优化）
        print(f"  Loading {num_mols} fingerprints...")

        # 检查数据格式
        if isinstance(chembl_data[0][2], str):
            # 字符串格式：超快速批量转换
            # 方法1：直接拼接所有字符串，一次性转换（最快）
            all_fps_str = ''.join([entry[2] for entry in chembl_data])

            # 转换为字节数组（ASCII: '0'=48, '1'=49），减去48得到0和1
            fps_bytes = np.frombuffer(all_fps_str.encode('ascii'), dtype=np.uint8) - 48

            # reshape为矩阵 (num_mols, fp_length)
            fps_matrix = fps_bytes.reshape(num_mols, fp_length).astype(np.int8)
        else:
            # 已经是数组格式
            fps_matrix = np.array([entry[2] for entry in chembl_data], dtype=np.int8)

        print(f"  Fingerprints loaded, computing similarities...")

        # 向量化计算所有分子的余弦相似度
        # 计算点积（矩阵乘法）
        dot_products = np.dot(fps_matrix, query_fp)

        # 计算模长
        query_norm = np.linalg.norm(query_fp)
        fps_norms = np.linalg.norm(fps_matrix, axis=1)

        # 计算余弦相似度（向量化）
        # 避免除以零
        similarities = np.zeros(num_mols)
        valid_idx = fps_norms > 0
        similarities[valid_idx] = dot_products[valid_idx] / (query_norm * fps_norms[valid_idx])

        # 找出top-k相似度最高的索引
        # 使用argpartition部分排序，比完全排序更快
        if top_k < num_mols:
            top_indices = np.argpartition(similarities, -top_k)[-top_k:]
            # 对top-k结果按相似度降序排序
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
        else:
            top_indices = np.argsort(similarities)[::-1]

        # 构建结果列表
        top_similar = []
        for idx in top_indices:
            top_similar.append({
                'chembl_id': chembl_data[idx][0],
                'smiles': chembl_data[idx][1],
                'similarity': float(similarities[idx])
            })

        return top_similar

    except Exception as e:
        print(f"Error loading ChEMBL database or computing similarities: {e}")
        import traceback
        traceback.print_exc()
        return []


def batch_find_similar_molecules(
    smiles_list: List[str],
    chembl_fps_file: str,
    top_k: int = 10
) -> Dict[str, List[Dict]]:
    """
    批量查找多个分子的相似分子（优化版：只加载一次数据库）

    Args:
        smiles_list: SMILES码列表
        chembl_fps_file: ChEMBL指纹数据库文件路径
        top_k: 每个分子返回的相似分子数量

    Returns:
        字典，key为SMILES码，value为相似分子列表
    """
    results = {}

    print(f"\n{'='*60}")
    print(f"Starting batch similarity search for {len(smiles_list)} molecules")
    print(f"{'='*60}\n")

    # 检查数据库文件是否存在
    if not os.path.exists(chembl_fps_file):
        print(f"Warning: ChEMBL fingerprint file not found: {chembl_fps_file}")
        return {smiles: [] for smiles in smiles_list}

    try:
        # ========== 只加载一次数据库 ==========
        print(f"[1/3] Loading ChEMBL database...")
        chembl_data = np.load(chembl_fps_file, allow_pickle=True)
        num_mols = len(chembl_data)

        # 确定指纹长度
        first_fp_str = chembl_data[0][2]
        if isinstance(first_fp_str, str):
            fp_length = len(first_fp_str)
        else:
            fp_length = len(first_fp_str)

        print(f"  Database loaded: {num_mols} molecules, fingerprint length: {fp_length}")

        # ========== 转换数据库指纹为矩阵（只做一次）==========
        print(f"[2/3] Converting fingerprints to matrix...")
        if isinstance(chembl_data[0][2], str):
            all_fps_str = ''.join([entry[2] for entry in chembl_data])
            fps_bytes = np.frombuffer(all_fps_str.encode('ascii'), dtype=np.uint8) - 48
            fps_matrix = fps_bytes.reshape(num_mols, fp_length).astype(np.int8)
        else:
            fps_matrix = np.array([entry[2] for entry in chembl_data], dtype=np.int8)

        # 预计算数据库指纹的模长（只做一次）
        fps_norms = np.linalg.norm(fps_matrix, axis=1)
        print(f"  Matrix ready, shape: {fps_matrix.shape}")

        # ========== 批量处理所有查询分子 ==========
        print(f"[3/3] Computing similarities for {len(smiles_list)} query molecules...")

        for i, smiles in enumerate(smiles_list, start=1):
            print(f"  [{i}/{len(smiles_list)}] Processing: {smiles[:60]}...")

            # 生成查询分子的指纹
            query_fp = get_fps(smiles, fp_size=fp_length)
            if query_fp is None:
                print(f"    ✗ Failed to generate fingerprint")
                results[smiles] = []
                continue

            # 计算余弦相似度（向量化）
            dot_products = np.dot(fps_matrix, query_fp)
            query_norm = np.linalg.norm(query_fp)

            similarities = np.zeros(num_mols)
            valid_idx = fps_norms > 0
            similarities[valid_idx] = dot_products[valid_idx] / (query_norm * fps_norms[valid_idx])

            # 找出top-k
            if top_k < num_mols:
                top_indices = np.argpartition(similarities, -top_k)[-top_k:]
                top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
            else:
                top_indices = np.argsort(similarities)[::-1]

            # 构建结果
            top_similar = []
            for idx in top_indices:
                top_similar.append({
                    'chembl_id': chembl_data[idx][0],
                    'smiles': chembl_data[idx][1],
                    'similarity': float(similarities[idx])
                })

            results[smiles] = top_similar

            if top_similar:
                print(f"    ✓ Top similarity: {top_similar[0]['similarity']:.4f} ({top_similar[0]['chembl_id']})")
            else:
                print(f"    ✗ No similar molecules found")

        print(f"\n{'='*60}")
        print(f"Batch similarity search completed!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Error in batch processing: {e}")
        import traceback
        traceback.print_exc()
        return {smiles: [] for smiles in smiles_list}

    return results


def format_chembl_url(chembl_id: str) -> str:
    """
    生成ChEMBL数据库链接

    Args:
        chembl_id: ChEMBL ID (例如: CHEMBL178234)

    Returns:
        ChEMBL网页链接
    """
    return f"https://www.ebi.ac.uk/chembl/explore/compound/{chembl_id}"


# 测试代码
if __name__ == "__main__":
    # 示例：测试单个分子
    test_smiles = "CCO"  # 乙醇
    chembl_file = "/data/yfang/ChEMBL/fps.npy"

    print("Testing fingerprint similarity module...")
    print(f"Query SMILES: {test_smiles}")

    # 生成指纹（默认256位）
    fp = get_fps(test_smiles, fp_size=256)
    if fp is not None:
        print(f"Fingerprint generated: length={len(fp)}, sum={np.sum(fp)}")

    # 查找相似分子
    if os.path.exists(chembl_file):
        similar_mols = find_top_similar_molecules(test_smiles, chembl_file, top_k=5)

        print(f"\nTop 5 similar molecules:")
        for i, mol in enumerate(similar_mols, start=1):
            print(f"  {i}. {mol['chembl_id']}: {mol['smiles'][:50]} (similarity: {mol['similarity']:.4f})")
            print(f"     URL: {format_chembl_url(mol['chembl_id'])}")
    else:
        print(f"ChEMBL database file not found: {chembl_file}")
