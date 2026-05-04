"""
光遗传学数据分析脚本
读取文件，进行 PSTH 绘图、光刺激前后对比以及配对 t 检验。

需要安装以下 Python 库：
    pandas, numpy, matplotlib, scipy, openpyxl
可以使用以下命令安装：
    pip install pandas numpy matplotlib scipy openpyxl
    在file_name = 'input_file.xlsx'中替换你的文件
Optogenetic Data Analysis Script
Read the file, perform PSTH plotting, comparison before and after optical stimulation, and paired t-test analysis.
Required Python libraries:
pandas, numpy, matplotlib, scipy, openpyxl
Installation command:
pip install pandas numpy matplotlib scipy openpyxl
Replace 'input_file.xlsx' in the line file_name = 'input_file.xlsx' with your own file path and name.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
# 设置中文字体支持（根据系统环境可能需要调整）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 尝试使用黑体或默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 1. 读取数据
file_name = 'input_file.xlsx'
xls = pd.ExcelFile(file_name)
# 读取各工作表
df_control_time = pd.read_excel(xls, sheet_name='control_time')
df_z_score      = pd.read_excel(xls, sheet_name='z_score')
df_psth1        = pd.read_excel(xls, sheet_name='psth1')
df_psth1_mean   = pd.read_excel(xls, sheet_name='psth1_mean')
df_psth1_sem    = pd.read_excel(xls, sheet_name='psth1_sem')
df_times        = pd.read_excel(xls, sheet_name='times')
df_pre_time     = pd.read_excel(xls, sheet_name='pre_time')
df_post_time    = pd.read_excel(xls, sheet_name='post_time')
# 提取关键数据为 numpy 数组
psth1 = df_psth1.values                        # 形状：(试验次数, 时间点数)
times = df_times.values.flatten()              # 一维时间轴
psth1_mean = df_psth1_mean.values.flatten()    # 一维平均
psth1_sem = df_psth1_sem.values.flatten()      # 一维 SEM
# 获取光刺激前后时间信息（用于后续可能的时间窗口划分）
pre_time = df_pre_time.values.flatten()
post_time = df_post_time.values.flatten()
# 2. 绘制 PSTH（平均 peri-event time histogram）
plt.figure(figsize=(12, 5))
plt.plot(times, psth1_mean, color='#1f77b4', linewidth=1.5, label='平均 z-score')
plt.fill_between(times, psth1_mean - psth1_sem, psth1_mean + psth1_sem,
                 color='#1f77b4', alpha=0.2, label='± SEM')
plt.axvline(x=0, color='red', linestyle='--', linewidth=1.2, label='光刺激开始')
plt.xlabel('时间 (秒)')
plt.ylabel('z-score')
plt.title('光刺激前后平均放电频率')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('psth.png', dpi=150)
plt.show()
# 3. 计算光刺激前、后的平均 z-score（每个 trial）
# 假设 times[0] 到 0 之间为基线，0 到 times[-1] 为刺激后
# 更精确的方法：根据 pre_time 和 post_time 来取范围
# 这里简单地以时间 0 为界
baseline_mask = times < 0
stim_mask = times >= 0
baseline_mean_trial = np.mean(psth1[:, baseline_mask], axis=1)
stim_mean_trial = np.mean(psth1[:, stim_mask], axis=1)
# 4. 绘制光刺激前后对比散点图
plt.figure(figsize=(6, 6))
plt.scatter(baseline_mean_trial, stim_mean_trial, alpha=0.5, c='gray', label='单次试验')
# 绘制对角线
min_val = min(np.min(baseline_mean_trial), np.min(stim_mean_trial))
max_val = max(np.max(baseline_mean_trial), np.max(stim_mean_trial))
plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x (无变化线)')
# 绘制均值 ± 标准差
mean_base = np.mean(baseline_mean_trial)
mean_stim = np.mean(stim_mean_trial)
plt.errorbar(mean_base, mean_stim,
             xerr=np.std(baseline_mean_trial), yerr=np.std(stim_mean_trial),
             fmt='ro', capsize=5, label='均值 ± SD')
plt.xlabel('光刺激前平均 z-score')
plt.ylabel('光刺激后平均 z-score')
plt.title('各试验光刺激前后放电率对比')
plt.legend()
plt.grid(True, alpha=0.3)
plt.axis('equal')
plt.tight_layout()
plt.savefig('pre_post_scatter.png', dpi=150)
plt.show()
# 5. 统计检验：配对 t 检验
t_stat, p_val = stats.ttest_rel(baseline_mean_trial, stim_mean_trial)
print("="*50)
print("配对 t 检验结果")
print("="*50)
print(f"t 统计量: {t_stat:.4f}")
print(f"p 值:     {p_val:.4f}")
print("="*50)
if p_val < 0.05:
    print("结论：光刺激后的放电频率与基线存在显著差异（p < 0.05）。")
else:
    print("结论：光刺激后的放电频率与基线无显著差异（p >= 0.05）。")
