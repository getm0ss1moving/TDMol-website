#!/usr/bin/env python3
"""
processhtml.py - 生成HTML结果页面 (类似RNAJog的processhtml.py)
参数:
    sys.argv[1] = task_id (timeVar)
    sys.argv[2] = email
"""

import sys
import os
import json
import base64
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D

# 导入分子指纹相似度模块
try:
    from fingerprint_similarity import find_top_similar_molecules, batch_find_similar_molecules, format_chembl_url
    SIMILARITY_ENABLED = True
except ImportError as e:
    print(f"Warning: Fingerprint similarity module not available: {e}")
    SIMILARITY_ENABLED = False

def generate_2d_image_base64(smiles):
    """从SMILES生成2D图像的Base64编码"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None

        # 生成2D坐标
        AllChem.Compute2DCoords(mol)

        # 使用RDKit绘制分子
        drawer = rdMolDraw2D.MolDraw2DCairo(300, 300)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        # 转换为Base64
        png_bytes = drawer.GetDrawingText()
        base64_data = base64.b64encode(png_bytes).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"
    except Exception as e:
        print(f"Error generating 2D image: {e}")
        return None

def sdf_to_base64(sdf_file):
    """读取SDF文件并转换为Base64编码"""
    try:
        with open(sdf_file, 'r') as f:
            sdf_content = f.read()
        return base64.b64encode(sdf_content.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Error reading SDF file: {e}")
        return None

def generate_result_html(result_data, output_file, task_id, chembl_fps_file=None):
    """Generate individual molecule result_X.html page"""
    mol_id = result_data['mol_id']
    smiles = result_data['smiles']
    xyz_file = result_data.get('xyz_file', '')
    similar_molecules = result_data.get('similar_molecules', [])

    # 构建SDF文件路径
    sdf_file = xyz_file.replace('.xyz', '.sdf') if xyz_file else ''

    # 生成2D图像（Base64编码）
    image_2d = generate_2d_image_base64(smiles)
    if image_2d is None:
        image_2d = ""

    # 读取SDF文件并转换为Base64 (SDF包含完整的键信息)
    sdf_base64 = sdf_to_base64(sdf_file) if os.path.exists(sdf_file) else ""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Molecule Details - {mol_id}</title>
    <base href="/bioinf/TDMol/static/jsmol/j2s/">
    <script type="text/javascript" src="/bioinf/TDMol/static/jsmol/JSmol.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="/bioinf/TDMol/css/unified-style.css">
    <style>
        .mol-info {{ margin-top: 20px; }}
    </style>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script type="text/javascript">
        var jmolApplet;
        var jmolInfo = {{
            width: "100%",
            height: "100%",
            debug: false,
            color: "0xFFFFFF",
            use: "HTML5",
            j2sPath: "/bioinf/TDMol/static/jsmol/j2s",
            serverURL: "https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
            disableJ2SLoadMonitor: true,
            disableInitialConsole: true,
            script: "set defaultColorScheme CPK; background white; wireframe off; spacefill off;"
        }};

        $(document).ready(function() {{
            Jmol.setDocument(false);
            jmolApplet = Jmol.getApplet("jmolApplet", jmolInfo);
            $("#jmol-container").html(Jmol.getAppletHtml(jmolApplet));

            // 加载SDF数据 (SDF格式包含完整的键连接信息)
            var sdfDataBase64 = "{sdf_base64}";
            if (sdfDataBase64) {{
                var sdfData = atob(sdfDataBase64);
                Jmol.script(jmolApplet, 'load data "mol"\\n' + sdfData + '\\nend "mol"');
                Jmol.script(jmolApplet, "spacefill 23%; wireframe 0.15; select all; center all; zoom 100%;");
            }}
        }});
    </script>
</head>
<body>
    <div class="main-header">
        <h1>EDM Molecule Generation</h1>
        <h2>Molecule Details: {mol_id}</h2>
    </div>

    <div class="page-container">
        <div class="btn-group" style="margin-bottom: 20px;">
            <a href="/bioinf/TDMol/result/{task_id}/brief.html" class="btn btn-primary">&laquo; Back to Results Overview</a>
            <a href="/bioinf/TDMol/index.html" class="btn btn-default">Back to Home</a>
        </div>

        <div class="jmol-container" id="jmol-container">
            <!-- JSmol will be loaded here -->
        </div>

        <div class="card mol-info">
            <div class="card-header">Molecule Information</div>
            <div class="card-body">
                <div class="info-box">
                    <p><strong>SMILES:</strong> <code>{smiles}</code></p>
                </div>

                <h3>2D Structure</h3>
                <img src="{image_2d}" alt="2D Structure" style="max-width: 300px; border: 1px solid #ddd; padding: 10px; border-radius: 6px; background-color: white;">

                <h3>Download Files</h3>
                <div class="btn-group">
                    <a href="molecule_{mol_id.split('_')[-1]}.xyz" class="btn btn-success" download>Download XYZ File</a>
                    <a href="molecule_{mol_id.split('_')[-1]}.sdf" class="btn btn-info" download>Download SDF File</a>
                </div>
            </div>
        </div>
    </div>
"""

    # Add similar molecules information
    if similar_molecules:
        html_content += """
    <div class="page-container">
        <div class="card">
            <div class="card-header">Similar Molecules (from ChEMBL Database)</div>
            <div class="card-body">
                <p style="color: #666; margin-bottom: 15px;">Top 10 most similar bioactive molecules found in ChEMBL database based on molecular fingerprint cosine similarity:</p>
                <table class="table table-striped table-bordered">
                    <thead>
                        <tr>
                            <th style="width: 10%;">Rank</th>
                            <th style="width: 20%;">ChEMBL ID</th>
                            <th style="width: 50%;">SMILES</th>
                            <th style="width: 20%;">Cosine Similarity</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for i, sim_mol in enumerate(similar_molecules, start=1):
            chembl_id = sim_mol['chembl_id']
            sim_smiles = sim_mol['smiles']
            similarity = sim_mol['similarity']
            chembl_url = format_chembl_url(chembl_id)

            # 保留3位有效数字
            html_content += f"""
                    <tr>
                        <td style="text-align: center;"><strong>#{i}</strong></td>
                        <td><a href="{chembl_url}" target="_blank" class="btn btn-sm btn-link">{chembl_id}</a></td>
                        <td><code style="font-size: 12px;">{sim_smiles}</code></td>
                        <td style="text-align: center; font-weight: bold;">{similarity:.3f}</td>
                    </tr>
"""

        html_content += """
                    </tbody>
                </table>
                <p style="margin-top: 10px; font-size: 13px; color: #666;">
                    <strong>Note:</strong> Click on ChEMBL ID to view detailed information about that molecule in the ChEMBL database.
                </p>
            </div>
        </div>
    </div>
"""

    html_content += """
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_brief_html(task_id, summary_data, output_file):
    """Generate brief.html overview page"""
    user_input = summary_data.get('user_input', 'N/A')
    results = summary_data.get('results', [])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Results Overview - {task_id}</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <link rel="stylesheet" href="/bioinf/TDMol/css/unified-style.css">
    <style>
        .result-table img {{ max-width: 200px; height: auto; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="main-header">
        <h1>EDM Molecule Generation</h1>
        <h2>Results Overview</h2>
    </div>

    <div class="page-container">
        <div class="info-box info-box-success">
            <p><strong>Task ID:</strong> <code>{task_id}</code></p>
            <p><strong>Input Description:</strong> "{user_input}"</p>
            <p><strong>Number of Molecules Generated:</strong> {len(results)}</p>
        </div>

        <div style="margin-bottom: 20px;">
            <a href="/bioinf/TDMol/index.html" class="btn btn-primary">&laquo; Back to Home</a>
        </div>

        <div class="card">
            <div class="card-header">Generated Molecules</div>
            <div class="card-body">
                <table class="table table-striped table-bordered result-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>SMILES</th>
                            <th>2D Structure</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    for i, result in enumerate(results):
        mol_id = result['mol_id']
        smiles = result['smiles']

        # 生成2D图像
        image_2d = generate_2d_image_base64(smiles)
        if image_2d is None:
            image_2d = ""

        html_content += f"""
                <tr>
                    <td><code>{mol_id}</code></td>
                    <td><code>{smiles}</code></td>
                    <td><img src="{image_2d}" alt="2D Structure"></td>
                    <td><a href="result_{i+1}.html" class="btn btn-sm btn-primary">View Details</a></td>
                </tr>
"""

    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) < 3:
        print("Usage: processhtml.py <task_id> <email>")
        sys.exit(1)

    task_id = sys.argv[1]
    email = sys.argv[2]

    # ChEMBL指纹数据库文件路径
    chembl_fps_file = "/data/yfang/ChEMBL/fps.npy"

    # 读取结果目录
    result_dir = f"/data/yfang/EDM_web/1111/web_apps/result/{task_id}/"
    summary_file = os.path.join(result_dir, "summary.json")

    if not os.path.exists(summary_file):
        print(f"Error: Summary file not found: {summary_file}")
        sys.exit(1)

    # 读取summary.json
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)

    # 默认启用相似度比较
    if SIMILARITY_ENABLED:
        if os.path.exists(chembl_fps_file):
            # 使用批量查询（只加载一次数据库，大幅提升性能）
            smiles_list = [result['smiles'] for result in summary_data.get('results', [])]

            # 批量查找相似分子
            similarity_results = batch_find_similar_molecules(smiles_list, chembl_fps_file, top_k=10)

            # 将结果写回summary_data
            for result in summary_data.get('results', []):
                smiles = result['smiles']
                result['similar_molecules'] = similarity_results.get(smiles, [])

            # 更新summary.json以保存相似度信息
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=4)
        else:
            print(f"Warning: ChEMBL database file not found: {chembl_fps_file}")
            print(f"Skipping similarity search...\n")
    else:
        print("Warning: Similarity module not available, skipping similarity search\n")

    # 生成每个分子的result_X.html
    print("Generating HTML pages...")
    for i, result in enumerate(summary_data.get('results', [])):
        result_file = os.path.join(result_dir, f"result_{i+1}.html")
        generate_result_html(result, result_file, task_id, chembl_fps_file)
        print(f"  Generated: result_{i+1}.html")

    # 生成brief.html（不包含相似度信息）
    brief_file = os.path.join(result_dir, "brief.html")
    generate_brief_html(task_id, summary_data, brief_file)
    print(f"  Generated: brief.html")

    print(f"\n{'='*60}")
    print(f"HTML generation completed for task {task_id}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
