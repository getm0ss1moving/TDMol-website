# model_runner.py

import os
import pickle
import torch
import numpy as np
from tqdm import tqdm
from rdkit import Chem
from os.path import join
import time

# 假设你的所有依赖项都在这里
from eval_sample import *
from finetune_CL_new import *

# --- 1. 初始化函数 (与之前相同，保持不变) ---
def initialize_models():
    
    
    model_path = '/data/yfang/EDM_new/outputs/edm_geom_drugs/'
    cl_model_path = "/data/yfang/EDM_new/model_GCN/model_GCN_1111_fixed_full200_epoch20_guidance_epoch26.pt"

    with open(join(model_path, 'args.pickle'), 'rb') as f:
        args = pickle.load(f)

    if not hasattr(args, 'normalization_factor'):
        args.normalization_factor = 1
    if not hasattr(args, 'aggregation_method'):
        args.aggregation_method = 'sum'

    args.cuda = not args.no_cuda and torch.cuda.is_available()
    device = torch.device("cuda:0" if args.cuda else "cpu")
    args.device = device

    dataset_info = get_dataset_info(args.dataset, args.remove_h)
    dataloaders, charge_scale = dataset.retrieve_dataloaders(args)

    flow, nodes_dist, prop_dist = get_model(args, device, dataset_info, dataloaders['train'])
    flow.to(device)

    fn = 'generative_model_ema.npy' if args.ema_decay > 0 else 'generative_model.npy'
    flow_state_dict = torch.load(join(model_path, fn), map_location=device)
    flow.load_state_dict(flow_state_dict)
    flow.eval()

    diff_checkpoint = torch.load(cl_model_path, map_location=device)
    model.load_state_dict(diff_checkpoint, strict=False)
    model.to(device)
    model.eval()

    
    
    return {
        "flow": flow,
        "model": model,
        "nodes_dist": nodes_dist,
        "dataset_info": dataset_info,
        "device": device,
        "args": args,
        "text_trunc_length": text_trunc_length # 假设 text_trunc_length 是全局可访问的
    }

# --- 2. 原始的 generate_mol 函数 (稍作修改以接收参数) ---
def generate_mol_original(text, samples, index, save_path, model_objects, scale=5.0):
    # 从 model_objects 字典中解包所有需要的对象
    flow = model_objects['flow']
    model = model_objects['model']
    nodes_dist = model_objects['nodes_dist']
    dataset_info = model_objects['dataset_info']
    device = model_objects['device']
    text_trunc_length = model_objects['text_trunc_length']
    max_n_nodes = dataset_info['max_n_nodes']

    for sample in tqdm(range(samples), desc=f"Generating samples for index {index}"):
        n_samples = 1
        batch_size = 1
        nodesxsample = nodes_dist.sample(n_samples)

        node_mask = torch.zeros(batch_size, max_n_nodes)
        for i in range(batch_size):
            node_mask[i, 0:nodesxsample[i]] = 1

        edge_mask = node_mask.unsqueeze(1) * node_mask.unsqueeze(2)
        diag_mask = ~torch.eye(edge_mask.size(1), dtype=torch.bool).unsqueeze(0)
        edge_mask *= diag_mask
        edge_mask = edge_mask.view(batch_size * max_n_nodes * max_n_nodes, 1).to(device)
        node_mask = node_mask.unsqueeze(2).to(device)

        text_input = gd.text_tokenizer(text, truncation=True, padding = 'max_length', 
                                       max_length=text_trunc_length, return_tensors = 'pt')
        text_token = text_input['input_ids'].to(device)
        text_mask = text_input['attention_mask'].to(device)

        x, h, x_clean, h_clean = flow.sample_ob(batch_size, max_n_nodes, node_mask, edge_mask, None, fix_noise=None,
                                      cond_fn=cond_fn_sdg, guidance_kwargs=[text_token,text_mask,model],prior_network=None,scale=scale)

        molecules = {'one_hot': [h['categorical'].detach().cpu()], 'x': [x.detach().cpu()], 'node_mask': [node_mask.detach().cpu()]}
        molecules = {key: torch.cat(molecules[key], dim=0) for key in molecules}
        
        from qm9.analyze import analyze_stability_for_molecules
        stability_dict, rdkit_metrics = analyze_stability_for_molecules(molecules, dataset_info)
        
        # 你的原始文件保存逻辑
        np.save('{}/mol{}.npy'.format(save_path, sample), molecules)
        try:
            with open('{}/mol_{}.txt'.format(save_path, index),'a') as f:
                f.write(rdkit_metrics[1][0]+'\n')   
        except:
            with open('{}/mol_{}.txt'.format(save_path, index),'a') as f:
                f.write('Invalid Molecule\n')              
        
        molecules_clean = {'one_hot': [h_clean['categorical'].detach().cpu()], 'x': [x_clean.detach().cpu()], 'node_mask': [node_mask.detach().cpu()]}
        molecules_clean = {key: torch.cat(molecules_clean[key], dim=0) for key in molecules_clean}
        
        np.save('{}/mol_clean{}.npy'.format(save_path, sample), molecules_clean)
        
        stability_dict_clean, rdkit_metrics_clean = analyze_stability_for_molecules(molecules_clean, dataset_info)
        
        try:
            with open('{}/mol_clean_{}.txt'.format(save_path, index),'a') as f:
                f.write(rdkit_metrics_clean[1][0]+'\n')
        except:
            with open('{}/mol_clean_{}.txt'.format(save_path, index),'a') as f:
                f.write('Invalid Molecule\n')

# --- 3. WebApp调用的主函数 ---
def run_generation_for_webapp(user_input, task_id, model_objects):
    """
    为Web应用执行完整的生成流程，并返回结果摘要。
    """
    try:
        start_time = time.time()
        
        # 定义参数
        samples = 100  # 保持原始样本数
        save_path = f"results/{task_id}" # 为每个任务创建唯一的输出目录
        os.makedirs(save_path, exist_ok=True)
        
        # 在你的原始代码中, index 是文本在列表中的索引。
        # 对于Web应用, 每次只有一个输入, 我们可以简单地将 index 设为 0。
        index = 0

        print(f"开始为任务 {task_id} 生成 {samples} 个样本...")
        
        # 调用保持原始功能的函数
        generate_mol_original(user_input, samples, index, save_path, model_objects)

        # --- 以下是你原始代码中的文件聚合逻辑 ---
        data_list = []
        data_list_clean = []
        for i in range(samples):
            mol_path = '{}/mol{}.npy'.format(save_path, i)
            mol_clean_path = '{}/mol_clean{}.npy'.format(save_path, i)
            
            if os.path.exists(mol_path):
                data = np.load(mol_path, allow_pickle=True)
                os.remove(mol_path) # 清理临时文件
            else:
                data = np.array({'one_hot':'null','x':'null','node_mask':'null'})
            
            if os.path.exists(mol_clean_path):
                data_clean = np.load(mol_clean_path, allow_pickle=True)
                os.remove(mol_clean_path) # 清理临时文件
            else:
                data_clean = np.array({'one_hot':'null','x':'null','node_mask':'null'})

            data_list.append(data)
            data_list_clean.append(data_clean)
            
        # 保存聚合后的大文件
        np.save('{}/mol_{}.npy'.format(save_path, index), data_list)
        np.save('{}/mol_clean_{}.npy'.format(save_path, index), data_list_clean)
        
        print(f"任务 {task_id} 文件处理完成。")

        # --- 生成返回给网页的结果摘要 ---
        # 读取生成的SMILES文件来创建摘要
        summary = f"任务ID: {task_id}\n"
        summary += f"输入描述: {user_input}\n"
        summary += f"-----------------------------------\n"
        summary += f"成功生成 {samples} 个样本。\n"
        
        smiles_clean_file = f'{save_path}/mol_clean_{index}.txt'
        if os.path.exists(smiles_clean_file):
            with open(smiles_clean_file, 'r') as f:
                smiles_list = [line.strip() for line in f.readlines() if line.strip() and line.strip() != 'Invalid Molecule']
            
            summary += f"有效 'Clean' 分子数: {len(smiles_list)}\n\n"
            summary += "部分有效 'Clean' SMILES 列表 (最多显示前10个):\n"
            for i, smiles in enumerate(smiles_list[:10]):
                summary += f"{i+1}. {smiles}\n"
        else:
            summary += "未能生成 'Clean' SMILES 结果文件。\n"
        
        duration = time.time() - start_time
        summary += f"\n-----------------------------------\n"
        summary += f"任务耗时: {duration:.2f} 秒。\n"
        summary += f"所有生成的数据文件已保存在服务器路径: {save_path}"

        return summary

    except Exception as e:
        print(f"处理任务 {task_id} 时发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        return f"处理失败: {str(e)}"