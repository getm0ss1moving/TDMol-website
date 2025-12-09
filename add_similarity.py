#!/usr/bin/env python3
"""
add_similarity.py - 为已生成的分子结果添加相似度信息

用法:
    python add_similarity.py <task_id>

功能:
    1. 读取指定任务的summary.json
    2. 为每个分子计算与ChEMBL数据库的相似度
    3. 更新summary.json添加相似度信息
    4. 重新生成HTML页面（包含相似度信息）

示例:
    python add_similarity.py 20231204_120000
"""

import sys
import os
import json
import argparse
from fingerprint_similarity import find_top_similar_molecules, format_chembl_url


def add_similarity_to_results(task_id, result_dir, chembl_fps_file, top_k=10):
    """
    为已生成的结果添加相似度信息

    Args:
        task_id: 任务ID
        result_dir: 结果目录路径
        chembl_fps_file: ChEMBL指纹数据库文件路径
        top_k: 返回的相似分子数量
    """
    summary_file = os.path.join(result_dir, "summary.json")

    # 检查文件是否存在
    if not os.path.exists(summary_file):
        print(f"Error: Summary file not found: {summary_file}")
        return False

    if not os.path.exists(chembl_fps_file):
        print(f"Error: ChEMBL database file not found: {chembl_fps_file}")
        return False

    # 读取summary.json
    print(f"Loading results from: {summary_file}")
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)

    results = summary_data.get('results', [])
    total_molecules = len(results)

    if total_molecules == 0:
        print("No molecules found in summary file")
        return False

    print(f"\n{'='*60}")
    print(f"Task ID: {task_id}")
    print(f"Total molecules: {total_molecules}")
    print(f"ChEMBL database: {chembl_fps_file}")
    print(f"Finding top {top_k} similar molecules for each...")
    print(f"{'='*60}\n")

    # 为每个分子计算相似度
    for i, result in enumerate(results, start=1):
        smiles = result['smiles']
        print(f"[{i}/{total_molecules}] Processing: {smiles[:60]}...")

        # 查找相似分子
        similar_mols = find_top_similar_molecules(smiles, chembl_fps_file, top_k=top_k)

        # 添加到结果中
        result['similar_molecules'] = similar_mols

        if similar_mols:
            top_sim = similar_mols[0]
            print(f"  ✓ Found {len(similar_mols)} similar molecules")
            print(f"    Top match: {top_sim['chembl_id']} (similarity: {top_sim['similarity']:.4f})")
        else:
            print(f"  ✗ No similar molecules found")
        print()

    # 保存更新后的summary.json
    print(f"Saving updated results to: {summary_file}")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=4)

    print(f"\n{'='*60}")
    print(f"Similarity calculation completed!")
    print(f"Updated summary file: {summary_file}")
    print(f"{'='*60}\n")

    return True


def regenerate_html(task_id, result_dir, email=""):
    """
    重新生成HTML页面（包含相似度信息）

    Args:
        task_id: 任务ID
        result_dir: 结果目录路径
        email: 用户邮箱（可选）
    """
    print("Regenerating HTML pages with similarity information...")

    try:
        # 导入processhtml模块
        import processhtml

        summary_file = os.path.join(result_dir, "summary.json")

        # 读取summary.json
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)

        # 生成每个分子的result_X.html
        for i, result in enumerate(summary_data.get('results', [])):
            result_file = os.path.join(result_dir, f"result_{i+1}.html")
            processhtml.generate_result_html(result, result_file, task_id)
            print(f"  Generated: result_{i+1}.html")

        # 生成brief.html（不包含相似度信息）
        brief_file = os.path.join(result_dir, "brief.html")
        processhtml.generate_brief_html(task_id, summary_data, brief_file)
        print(f"  Generated: brief.html")

        print("\n✓ HTML pages regenerated successfully!")
        return True

    except ImportError as e:
        print(f"Error: Could not import processhtml module: {e}")
        print("Please run processhtml.py manually")
        return False
    except Exception as e:
        print(f"Error regenerating HTML: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Add similarity information to existing molecule generation results'
    )
    parser.add_argument('task_id', help='Task ID')
    parser.add_argument(
        '--result-dir',
        help='Result directory (default: /data/yfang/EDM_web/1111/web_apps/result/<task_id>/)',
        default=None
    )
    parser.add_argument(
        '--chembl-db',
        help='ChEMBL fingerprint database file (default: /data/yfang/ChEMBL/fps.npy)',
        default='/data/yfang/ChEMBL/fps.npy'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=10,
        help='Number of similar molecules to find (default: 10)'
    )
    parser.add_argument(
        '--skip-html',
        action='store_true',
        help='Skip HTML regeneration'
    )
    parser.add_argument(
        '--email',
        default='',
        help='User email (optional)'
    )

    args = parser.parse_args()

    # 确定结果目录
    if args.result_dir:
        result_dir = args.result_dir
    else:
        result_dir = f"/data/yfang/EDM_web/1111/web_apps/result/{args.task_id}/"

    # 添加相似度信息
    success = add_similarity_to_results(
        args.task_id,
        result_dir,
        args.chembl_db,
        top_k=args.top_k
    )

    if not success:
        print("Failed to add similarity information")
        sys.exit(1)

    # 重新生成HTML（如果未跳过）
    if not args.skip_html:
        print()
        html_success = regenerate_html(args.task_id, result_dir, args.email)
        if not html_success:
            print("\nWarning: HTML regeneration failed, but similarity data has been saved.")
            print("You can manually run: python processhtml.py {} {}".format(
                args.task_id, args.email or 'user@example.com'
            ))
    else:
        print("\nHTML regeneration skipped (--skip-html flag)")
        print("To regenerate HTML with similarity info, run:")
        print(f"  python processhtml.py {args.task_id} {args.email or 'user@example.com'}")

    print("\n✓ All done!")


if __name__ == "__main__":
    main()
