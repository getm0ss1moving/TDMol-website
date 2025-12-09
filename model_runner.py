# model_runner.py (Final Optimized Version)

import os
import pickle
import torch
import numpy as np
from rdkit import Chem
from os.path import join
import time

project_paths = [
    '/data/yfang/txt2mol/code',
    # 很可能您的 dataset.py 和 eval_sample.py 在这个目录下
    '/data/yfang/EDM_new/' 
]
# --- 依赖项导入 (保持不变) ---
try:
    from eval_sample import *
    from finetune_CL_new import *
    from qm9.analyze import analyze_stability_for_molecules
except ImportError as e:
    print(f"错误：未能导入必要的模块: {e}")
    exit(1)

# --- 全局变量、initialize_models、_extract_data_from_mol_dict (保持不变) ---
text_trunc_length = 512

def initialize_models():
    # ... (此函数与之前完全相同) ...
    print("正在初始化模型...")
    
    model_path = '/data/yfang/EDM_new/outputs/edm_geom_drugs/'
    cl_model_path = "/data/yfang/EDM_new/model_GCN/model_GCN_1111_fixed_full200_epoch20_guidance_epoch26.pt"

    if not os.path.exists(model_path) or not os.path.exists(cl_model_path):
        raise FileNotFoundError(f"模型路径未找到，请检查: {model_path} 或 {cl_model_path}")

    with open(join(model_path, 'args.pickle'), 'rb') as f:
        args = pickle.load(f)

    args.normalization_factor = getattr(args, 'normalization_factor', 1)
    args.aggregation_method = getattr(args, 'aggregation_method', 'sum')

    args.cuda = torch.cuda.is_available()
    device = torch.device("cuda:0" if args.cuda else "cpu")
    args.device = device

    dataset_info = get_dataset_info(args.dataset, args.remove_h)
    dataloaders, charge_scale = dataset.retrieve_dataloaders(args)

    flow, nodes_dist, prop_dist = get_model(args, device, dataset_info, dataloaders['train'])
    
    fn = 'generative_model_ema.npy' if hasattr(args, 'ema_decay') and args.ema_decay > 0 else 'generative_model.npy'
    flow_state_dict = torch.load(join(model_path, fn), map_location=device)
    flow.load_state_dict(flow_state_dict)
    flow.to(device)
    flow.eval()

    diff_checkpoint = torch.load(cl_model_path, map_location=device)
    model.load_state_dict(diff_checkpoint, strict=False)
    model.to(device)
    model.eval()
    
    print("模型初始化完成。")
    
    return {
        "flow": flow,
        "model": model,
        "nodes_dist": nodes_dist,
        "dataset_info": dataset_info,
        "device": device,
        "args": args,
        "text_trunc_length": text_trunc_length
    }

def _extract_data_from_mol_dict(mol_dict, dataset_info):
    # ... (此函数与之前完全相同) ...
    if isinstance(mol_dict, np.ndarray):
        mol_dict = mol_dict.item()
    num_atoms = int(torch.sum(mol_dict['node_mask']))
    coords = mol_dict['x'][0, :num_atoms, :].numpy()
    one_hot = mol_dict['one_hot'][0, :num_atoms, :]
    atom_types_indices = torch.argmax(one_hot, dim=1).numpy()
    atom_decoder = dataset_info['atom_decoder']
    atomic_number_map = {name: Chem.GetPeriodicTable().GetAtomicNumber(name) for name in atom_decoder}
    atomic_numbers = np.array([atomic_number_map[atom_decoder[i]] for i in atom_types_indices])
    return atomic_numbers, coords

# --- [新] 核心生成逻辑 (无文件I/O) ---
def _generate_single_molecule_in_memory(text, model_objects, scale=5.0):
    """
    执行单次分子生成的核心逻辑，并直接返回内存中的数据。
    这个函数取代了原来写入文件的循环体。
    """
    flow = model_objects['flow']
    model = model_objects['model']
    nodes_dist = model_objects['nodes_dist']
    dataset_info = model_objects['dataset_info']
    device = model_objects['device']
    text_trunc_length = model_objects['text_trunc_length']
    max_n_nodes = dataset_info['max_n_nodes']
    
    # --- 模型输入准备 (与原来相同) ---
    nodesxsample = nodes_dist.sample(1)
    node_mask = torch.zeros(1, max_n_nodes)
    node_mask[0, 0:nodesxsample[0]] = 1
    edge_mask = (node_mask.unsqueeze(1) * node_mask.unsqueeze(2))
    diag_mask = ~torch.eye(edge_mask.size(1), dtype=torch.bool).unsqueeze(0)
    edge_mask *= diag_mask
    edge_mask = edge_mask.view(1 * max_n_nodes * max_n_nodes, 1).to(device)
    node_mask = node_mask.unsqueeze(2).to(device)
    text_input = gd.text_tokenizer(text, truncation=True, padding='max_length', max_length=text_trunc_length, return_tensors='pt')
    text_token = text_input['input_ids'].to(device)
    text_mask = text_input['attention_mask'].to(device)

    # --- 运行模型 (与原来相同) ---
    x, h, x_clean, h_clean = flow.sample_ob(1, max_n_nodes, node_mask, edge_mask, None, fix_noise=None,
                                  cond_fn=cond_fn_sdg, guidance_kwargs=[text_token, text_mask, model],
                                  prior_network=None, scale=scale)

    # --- 数据处理并返回 (取代文件写入) ---
    molecules_clean = {
        'one_hot': h_clean['categorical'].detach().cpu(),
        'x': x_clean.detach().cpu(),
        'node_mask': node_mask.detach().cpu()
    }
    _, rdkit_metrics_clean = analyze_stability_for_molecules(molecules_clean, dataset_info)
    
    smiles = "Invalid Molecule"
    if rdkit_metrics_clean[0] and rdkit_metrics_clean[1]:
        smiles = rdkit_metrics_clean[1][0]
        
    return molecules_clean, smiles

# --- [最终] WebApp 调用的主函数 (无文件I/O) ---
def generate_and_evaluate_for_webapp(user_input, model_objects, task_id, num_samples=100, guidance_scale=5.0):
    """
    为 Web 应用执行生成和评估流程，全程在内存中操作。

    参数:
        user_input: 用户输入的文本描述
        model_objects: 模型对象字典
        task_id: 任务ID
        num_samples: 要生成的分子数量（默认100）
        guidance_scale: 引导尺度（默认5.0）

    返回:
        generated_molecules: 生成的所有有效分子列表
        evaluation_summary: 评估摘要
    """
    start_time = time.time()

    generated_molecules = []
    evaluation_summary = {
        'total_samples': num_samples,
        'valid_molecules': 0,
        'invalid_molecules': 0,
        'valid_smiles_list': [],
        'processing_time': 0,
        'error_message': None
    }

    try:
        print(f"开始为任务 {task_id} 生成 {num_samples} 个分子...")
        print(f"使用 guidance_scale = {guidance_scale}")

        valid_smiles_list = []

        # 生成指定数量的分子
        for i in range(num_samples):
            print(f"生成分子 {i+1}/{num_samples}...", end=' ')

            # 1. 使用指定的guidance_scale生成分子
            mol_dict, smiles = _generate_single_molecule_in_memory(user_input, model_objects, scale=guidance_scale)

            # 2. 处理生成结果
            if smiles and smiles != 'Invalid Molecule':
                atomic_numbers, coordinates = _extract_data_from_mol_dict(mol_dict, model_objects['dataset_info'])
                molecule_data = {
                    "atoms": atomic_numbers,
                    "coords": coordinates,
                    "smiles": smiles,
                    "index": i + 1
                }
                generated_molecules.append(molecule_data)
                valid_smiles_list.append(smiles)
                print(f"✓ 有效 (SMILES: {smiles[:50]}...)")
            else:
                evaluation_summary['invalid_molecules'] += 1
                print("✗ 无效")

        # 3. 填充最终的评估摘要
        evaluation_summary['valid_molecules'] = len(valid_smiles_list)
        evaluation_summary['valid_smiles_list'] = valid_smiles_list
        duration = time.time() - start_time
        evaluation_summary['processing_time'] = f"{duration:.2f}"

        print(f"\n{'='*60}")
        print(f"生成完成！")
        print(f"  有效分子数: {len(valid_smiles_list)}/{num_samples}")
        print(f"  无效分子数: {evaluation_summary['invalid_molecules']}/{num_samples}")
        print(f"  任务 {task_id} 总耗时: {duration:.2f} 秒")
        print(f"{'='*60}\n")

        return generated_molecules, evaluation_summary

    except Exception as e:
        import traceback
        error_msg = f"处理任务 {task_id} 期间发生严重错误: {e}"
        print(error_msg)
        traceback.print_exc()
        evaluation_summary['error_message'] = error_msg
        return [], evaluation_summary