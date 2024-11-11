# %%
# 第二个代码块: 导入需要的库
import pandas as pd
from anthropic import Anthropic
import json
from datetime import datetime
import os

# %%
# 第三个代码块: 定义主要类
class ESGReportGenerator:
    def __init__(self, api_key):
        self.anthropic = Anthropic(api_key=api_key)
        
    def read_csv(self, file_path):
        """读取CSV文件"""
        try:
            df = pd.read_csv(file_path)
            return df.to_dict(orient='records')
        except Exception as e:
            raise Exception(f"读取CSV文件失败: {str(e)}")
            
    def generate_report(self, data):
        """生成ESG评分报告"""
        prompt = f"""我有一份ESG数据,请对其进行分析并生成评分报告和可视化。

数据内容:
{json.dumps(data, ensure_ascii=False, indent=2)}

请提供:
1. 详细的评分标准(包括环境、社会和治理三个维度)
2. 具体的评分结果
3. 一个React组件用于可视化展示结果(使用Recharts绘制图表)
4. 详细的分析报告(包括优势、不足和改进建议)

评分报告要求:
- 基于新加坡交易所(SGX)的可持续发展指标
- 提供明确的评分依据
- 包含量化和定性分析
- 针对新能源行业特点

请确保React组件代码可以直接运行,使用Tailwind CSS进行样式设置。
"""

        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"生成报告失败: {str(e)}")
            
    def save_report(self, report, output_dir="reports"):
        """保存报告到文件"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"esg_report_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'content': report,
                    'generated_at': timestamp
                }, f, ensure_ascii=False, indent=2)
                
            return filepath
        except Exception as e:
            raise Exception(f"保存报告失败: {str(e)}")

# %%
# 第四个代码块: 使用示例
# 替换为您的 API key
api_key = "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"  

# CSV文件路径
csv_file_path = "train_label2.csv"  # 替换为您的CSV文件路径

# 初始化生成器
generator = ESGReportGenerator(api_key)

# 读取CSV数据
data = generator.read_csv(csv_file_path)

# 生成报告
report = generator.generate_report(data)

# 保存报告
filepath = generator.save_report(report)

print(f"报告已保存至: {filepath}")

# 显示报告内容
print("\nESG评分报告内容:")
print(report)



# %%
