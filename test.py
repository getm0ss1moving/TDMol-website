# test_rdkit.py
from rdkit import Chem
# 导入底层模块
from rdkit.Chem import rdMolDescriptors

mol = Chem.MolFromSmiles('CCO')

try:
    # 使用底层函数调用
    logp_value = rdMolDescriptors._CalcCrippenLogP(mol)
    print("测试成功！")
    print(f"乙醇的 LogP (通过底层 API) 是: {logp_value}")
except Exception as e:
    print(f"测试失败: {e}")