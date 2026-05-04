"""
mat_to_excle
需要安装以下 Python 库：(Required Python libraries:)
scipy h5py pandas openpyxl numpy
可以使用以下命令安装：(Installation command:)
pip install scipy h5py pandas openpyxl numpy
在主函数定义中修改你的输入文件与输出文件
Modify your input file and output file in the main function definition.
"""

import scipy.io
import h5py
import numpy as np
import pandas as pd
# 1 加载 MAT 文件
def load_mat_file(file_path):
    try:
        data = scipy.io.loadmat(file_path)
        print("MAT version: v7.2 or earlier")
        return {k: v for k, v in data.items() if not k.startswith("__")}
    except NotImplementedError:
        print("MAT version: v7.3 (HDF5)")
        return load_hdf5_mat(file_path)
def load_hdf5_mat(file_path):
    data = {}
    def extract(name, obj):
        if isinstance(obj, h5py.Dataset):
            data[name] = np.array(obj)
        elif isinstance(obj, h5py.Group):
            for key in obj:
                extract(f"{name}/{key}", obj[key])
    with h5py.File(file_path, 'r') as f:
        for key in f.keys():
            extract(key, f[key])
    return data
# 2. 数据清洗
def simplify(value):
    """
    递归处理 MATLAB struct / cell / object
    """
    if isinstance(value, np.ndarray):
        if value.dtype == object:
            return [simplify(v) for v in value.flatten()]
        else:
            return value
    return value
# 3. 转 DataFrame
def to_dataframe(value, key="var"):
    """
    将各种数据类型转为 DataFrame
    """
    value = simplify(value)
    try:
        # numpy数组
        if isinstance(value, np.ndarray):

            if value.ndim == 0:
                return pd.DataFrame([value.item()], columns=[key])

            elif value.ndim == 1:
                return pd.DataFrame(value, columns=[key])

            elif value.ndim == 2:
                return pd.DataFrame(value)

            else:
                # 高维展开
                reshaped = value.reshape(value.shape[0], -1)
                return pd.DataFrame(reshaped)

        # list（cell展开后）
        elif isinstance(value, list):
            return pd.DataFrame(value)
        # 其他类型
        else:
            return pd.DataFrame([str(value)], columns=[key])
    except Exception as e:
        print(f"Convert error ({key}): {e}")
        return None
# 4. 保存为 Excel
def save_to_excel(data, output_file="result.xlsx"):
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for key, value in data.items():
            df = to_dataframe(value, key)
            if df is None:
                continue
            try:
                sheet_name = key[:31]  # Excel限制
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Saved sheet: {sheet_name}")
            except Exception as e:
                print(f"Skip {key}: {e}")

    print(f"Excel saved: {output_file}")
# 5. 主函数
def main():
    file_path = "input.mat"   # ← 修改这里
    output_file = "output.xlsx"
    data = load_mat_file(file_path)
    print("\nVariables:")
    for k in data:
        print(f" - {k}")
    save_to_excel(data, output_file)
# 6. 主函数调用
if __name__ == "__main__":
    main()
