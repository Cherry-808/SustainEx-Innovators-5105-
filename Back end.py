from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from werkzeug.utils import secure_filename
import configparser
import fitz  # PyMuPDF
from PIL import Image
import sys
import base64
import json
from dotenv import load_dotenv
import openai
import re
from openai import OpenAI
import pandas as pd
from anthropic import Anthropic
from datetime import datetime
import dash


app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'  # 添加时间戳到日志
)
logger = app.logger

# 配置 CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3004",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3004",
    "http://localhost:65079"
]
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

# OpenAI setup
client = OpenAI(
    api_key='sk-d6v51KC96JwJsE7VxcjchYfezR2wMLmn0K72l0Q3zkkVkOJP',
    base_url='https://xiaoai.plus/v1'
)

# Anthropic API Key
ANTHROPIC_API_KEY = "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"

model_name = "gpt-4o"

# 配置上传和输出路径
UPLOAD_FOLDER = r'E:\Files\NUS\DSS\DSS 5105\Project\input'
OUTPUT_FOLDER = r'E:\Files\NUS\DSS\DSS 5105\Project\output'
STATIC_FOLDER = r'E:\Files\NUS\DSS\DSS 5105\Project\static'

# OpenAI相关配置
system_prompt = 'You are an OCR engineer'
text_content = 'Extract all data content from the document'
text_content2 = '''Extract data information with numbers from the text and convert it into JSON format. 
Please follow these requirements:
1. Only include data with numbers
2. Use only English characters and numbers
3. Convert any Chinese punctuation marks to English ones
4. Remove any non-ASCII characters
5. Keep the structure simple and clean'''

# SGX ESG指标列表
sgx_esg_indicators = [
    "Age-Based Diversity(existing employees by age group)", 
    "Alignment with Frameworks And Disclosure Practices",
    "Assurance of Sustainability Report",
    "Board Composition",
    "ESG-related Certifications",
    "Development & Training",
    "Economic Performance",
    "Employment",
    "Energy Consumption(GJ)",
    "Ethical Behaviour(anti-corruption)",
    "Gender Diversity",
    "Greenhouse Gas Emissions('GHG')",
    "Management Diversity",
    "Occupational Health & Safety",
    "Waste Generation",
    "Water Consumption"
]

# 配置上传
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 添加GPT3客户端配置
OPENAI_API_KEY_GPT3 = "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"

# 初始化GPT3客户端
gpt3_client = OpenAI(
    api_key=OPENAI_API_KEY_GPT3
)

# Utility functions
def create_required_directories():
    directories = [UPLOAD_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER]
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

def flatten_json(nested_json, parent_key=''):
    items = []
    if isinstance(nested_json, list):
        for i, item in enumerate(nested_json):
            items.extend(flatten_json(item, f"{parent_key}[{i}]").items() if isinstance(flatten_json(item, f"{parent_key}[{i}]"), dict) else [(f"{parent_key}[{i}]", flatten_json(item, f"{parent_key}[{i}]"))])
    elif isinstance(nested_json, dict):
        for k, v in nested_json.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_json(v, new_key).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    items.extend(flatten_json(item, f"{new_key}[{i}]").items() if isinstance(flatten_json(item, f"{new_key}[{i}]"), dict) else [(f"{new_key}[{i}]", flatten_json(item, f"{new_key}[{i}]"))])
            else:
                items.append((new_key, v))
    else:
        return nested_json
    return dict(items)

def extract_images_from_pdf(pdf_path, output_folder, debug=False):
    """从PDF提取图片"""
    try:
        pdf_document = fitz.open(pdf_path)
        logger.info(f"Successfully opened PDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to open PDF file {pdf_path}: {e}")
        return False

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Created output folder: {output_folder}")

    for page_num in range(len(pdf_document)):
        try:
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)

            for image_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_name = f"image_{page_num + 1}_{image_index + 1}.{image_ext}"
                    image_path = os.path.join(output_folder, image_name)

                    with open(image_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    logger.info(f"Saved image: {image_path}")

                except Exception as e:
                    logger.error(f"Failed to extract image {image_index + 1} on page {page_num + 1}: {e}")

        except Exception as e:
            logger.error(f"Error processing page {page_num + 1}: {e}")
    
    return True

def render_pdf_page_as_image(pdf_path, output_folder, zoom=2):
    """将PDF页面渲染为图像"""
    try:
        pdf_document = fitz.open(pdf_path)
        logger.info(f"Successfully opened PDF for rendering: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to open PDF file {pdf_path}: {e}")
        return False

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Created output folder: {output_folder}")

    for page_num in range(len(pdf_document)):
        try:
            page = pdf_document.load_page(page_num)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            image_name = f"page_{page_num + 1}.png"
            image_path = os.path.join(output_folder, image_name)
            pix.save(image_path)
            logger.info(f"Rendered page {page_num + 1} as image: {image_path}")
        except Exception as e:
            logger.error(f"Failed to render page {page_num + 1}: {e}")
            return False
    
    return True

def convert_chinese_chars(text):
    """将中文字符转换为英文字符"""
    mapping = {
        '，': ',',
        '。': '.',
        '：': ':',
        '；': ';',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '（': '(',
        '）': ')',
        '【': '[',
        '】': ']',
        '％': '%',
        '！': '!',
        '？': '?',
        '、': ',',
        '《': '<',
        '》': '>',
        '—': '-',
        '～': '~',
    }
    for zh, en in mapping.items():
        text = text.replace(zh, en)
    return text

def process_with_openai(rendered_pages_folder, pdf_name):
    """使用OpenAI处理图片并提取数据"""
    try:
        json_folder = os.path.join(OUTPUT_FOLDER, 'json_output')
        os.makedirs(json_folder, exist_ok=True)
        
        json_output_path = os.path.join(json_folder, f"{pdf_name}.json")
        logger.info(f"Will save JSON to: {os.path.abspath(json_output_path)}")
        
        extracted_data_list = []

        # 获取并排序图片文件
        file_names = [file_name for file_name in os.listdir(rendered_pages_folder) if
                      re.match(r'page_(\d+)\.png', file_name)]
        sorted_file_names = sorted(file_names, key=lambda x: int(re.search(r'(\d+)', x).group()))

        for file_name in sorted_file_names:
            image_path = os.path.join(rendered_pages_folder, file_name)
            logger.info(f"Processing file: {file_name}")

            base64_image = encode_image(image_path)
            if not base64_image:
                logger.error(f"Skipping {file_name} due to encoding error.")
                continue

            # First OpenAI call - Extract text
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                            {"type": "text", "text": text_content},
                        ],
                    },
                ]

                resp = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.0
                )

                extracted_data = resp.choices[0].message.content
                extracted_data = convert_chinese_chars(extracted_data)
                logger.info(f"Successfully extracted text from {file_name}")

            except Exception as e:
                logger.error(f"Error during completion for {file_name}: {e}")
                continue

            # Second OpenAI call - Convert to JSON
            try:
                resp = client.chat.completions.create(
                    model=model_name,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": text_content2},
                        {"role": "user", "content": [{"type": "text", "text": extracted_data}]},
                    ],
                    temperature=0.0,
                )

                extracted_data_json = resp.choices[0].message.content
                extracted_data_json = convert_chinese_chars(extracted_data_json)
                logger.info(f"Extracted JSON for {file_name}: {extracted_data_json}")
                data = json.loads(extracted_data_json)
                extracted_data_list.append({file_name: data})

            except Exception as e:
                logger.error(f"Error processing JSON for {file_name}: {e}")
                continue

        with open(json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data_list, json_file, ensure_ascii=False, indent=4)

        logger.info(f"JSON data saved successfully to: {os.path.abspath(json_output_path)}")
        return True, json_output_path

    except Exception as e:
        logger.error(f"Error in OpenAI processing: {e}")
        return False, str(e)
    
class ESGReportGenerator:
    def __init__(self):
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.logger = logging.getLogger(__name__)
        
        # 添加ESG指标列表
        self.sgx_esg_indicators = [
            "Age-Based Diversity(existing employees by age group)", 
            "Alignment with Frameworks And Disclosure Practices",
            "Assurance of Sustainability Report",
            "Board Composition",
            "ESG-related Certifications",
            "Development & Training",
            "Economic Performance",
            "Employment",
            "Energy Consumption(GJ)",
            "Ethical Behaviour(anti-corruption)",
            "Gender Diversity",
            "Greenhouse Gas Emissions('GHG')",
            "Management Diversity",
            "Occupational Health & Safety",
            "Waste Generation",
            "Water Consumption"
        ]

    def process_json_data(self, json_folder):
        """处理JSON文件夹中的所有数据"""
        try:
            df = pd.DataFrame()
            for file_name in os.listdir(json_folder):
                if file_name.endswith('.json'):
                    file_path = os.path.join(json_folder, file_name)
                    with open(file_path, 'r',encoding='utf-8') as file:
                        data = json.load(file)
                        company_report_name = re.sub(r'\d+', '', file_name.replace('.json', ''))
                        year = re.search(r'\d+', file_name)
                        year = int(year.group()) if year else None
                        
                        flattened_data = self.flatten_json(data)
                        df_1 = pd.DataFrame([flattened_data])
                        df_1 = df_1.T
                        df_1.columns = ['index_value']
                        df_1.index.name = 'index_name'
                        df_1 = df_1.reset_index()
                        df_1['Company Report Name'] = company_report_name.strip()
                        df_1['Year'] = year
                        df = pd.concat([df, df_1], ignore_index=True)
            
            # 处理数据并生成预测标签
            df = self.process_dataframe(df)
            
            # 生成ESG评分
            df = self.generate_esg_scores(df)
            
            # 保存处理后的数据到CSV
            self.save_to_csv(df)
            
            return df

        except Exception as e:
            self.logger.error(f"Error occurred while processing JSON data: {str(e)}")
            raise

    def flatten_json(self, nested_json, parent_key=''):
        """扁平化嵌套的JSON结构"""
        items = []
        if isinstance(nested_json, list):
            for i, item in enumerate(nested_json):
                new_dict = self.flatten_json(item, f"{parent_key}[{i}]")
                if isinstance(new_dict, dict):
                    items.extend(new_dict.items())
                else:
                    items.append((f"{parent_key}[{i}]", new_dict))
        elif isinstance(nested_json, dict):
            for k, v in nested_json.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, (dict, list)):
                    items.extend(self.flatten_json(v, new_key).items())
                else:
                    items.append((new_key, v))
        else:
            return nested_json
        return dict(items)

    def process_dataframe(self, df):
        """处理和清理DataFrame"""
        # 清理索引名称
        df["index_name"] = df["index_name"].apply(lambda x: ".".join(x.strip('.').split('.')[-2:]))
        
        # 过滤数值并移除不需要的条目
        df = df[pd.to_numeric(df["index_value"], errors='coerce').notna()].reset_index(drop=True)
        df = df[~df["index_name"].str.contains("page_number", na=False)].reset_index(drop=True)
        df = df[~df["index_name"].str.contains("Reference", na=False)].reset_index(drop=True)
        
        # 使用GPT-3.5生成预测标签
        df['Predicted_label'] = df.apply(
            lambda row: self.chatgpt_label_text(row['index_name'], self.sgx_esg_indicators),
            axis=1
        )
        
        # 清理和标准化标签
        df = self.clean_labels(df)
        
        return df

    def chatgpt_label_text(self, index_name, label_options):
        """使用GPT-3.5进行标签预测"""
        try:
            prompt = f"Classify the following text into a category: '{index_name}'. The all possible categories are: {', '.join(label_options)}. The output should be only one 'category' in the possible categories without any extra text. If there is no match, output 'NaN'"
            
            response = gpt3_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert in Singapore ESG field."},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-3.5-turbo",
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"GPT label prediction error: {e}")
            return "NaN"

    def clean_labels(self, df):
        """清理和标准化标签"""
        replacements = {
            r'.*\b(Greenhouse Gas|GHG|Carbon|carbon)\b.*': 'Greenhouse Gas Emissions("GHG")',
            r'.*\b(Energy)\b.*': 'Energy Consumption(GJ)',
            r'.*\b(Economic)\b.*': 'Economic Performance',
            r'.*\b(Water)\b.*': 'Water Consumption',
            r'.*\b(Safety)\b.*': 'Occupational Health & Safety',
            r'.*\b(Training)\b.*': 'Development & Training',
            r'.*\b(Employment)\b.*': 'Employment',
            r'.*\b(Gender|gender)\b.*': 'Gender Diversity',
            r'.*\b(Ethical)\b.*': 'Ethical Behaviour'
        }
        
        for pattern, replacement in replacements.items():
            df['Predicted_label'] = df['Predicted_label'].replace(
                to_replace=pattern, value=replacement, regex=True
            )
        df = df[df['Predicted_label'].str.strip().isin(sgx_esg_indicators)].reset_index(drop=True)
        
        return df

    def generate_esg_scores(self, df):
        """生成ESG评分"""
        try:
            df['Score'] = df.apply(
                lambda row: self.generate_scores(row['index_name'], row['index_value']),
                axis=1
            )
            # 确保评分为数值类型
            df = df[pd.to_numeric(df["Score"], errors='coerce').notna()].reset_index(drop=True)
            return df
        except Exception as e:
            self.logger.error(f"Error occurred while generating an ESG score: {e}")
            raise

    def generate_scores(self, index_name, index_value):
        """使用Anthropic生成单个评分"""
        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[
                    {
                        "role": "user",
                        "content": f"Based on the Singapore Exchange standards, please provide a score from 0 to 10 for the value {index_name}: {index_value}. Output only the number."
                    }
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            self.logger.error(f"Error occurred while generating the score: {e}")
            return None

    def save_to_csv(self, df):
        """保存处理后的数据到CSV"""
        try:
            output_folder = os.path.join(OUTPUT_FOLDER, 'processed_data')
            os.makedirs(output_folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(output_folder, f'esg_scores.csv')
            df.to_csv(csv_path, encoding='utf-8-sig', index=False)
            self.logger.info(f"Data saved to: {csv_path}")
            return csv_path
        except Exception as e:
            self.logger.error(f"Error occurred when saving CSV file: {e}")
            raise

# Flask路由
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file format. Only PDF files are allowed.'}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(file_path)
        logger.info(f"File successfully uploaded: {filename}")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_path': file_path,
            'filename': filename
        }), 200

    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during upload'}), 500

@app.route('/start_process', methods=['POST'])
def start_process():
    try:
        logger.info("Start processing...")
        
        # === 代码块1: 处理PDF文件 ===
        logger.info("PDF file processing...")
        
        pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]

        if not pdf_files:
            return jsonify({
                'message': 'No PDF file found in the input directory',
                'status': 'warning'
            }), 200

        processed_files = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file)
            pdf_base_name = os.path.splitext(pdf_file)[0]
            
            # 创建输出文件夹
            images_output_folder = os.path.join(OUTPUT_FOLDER, pdf_base_name, "extracted_images")
            rendered_pages_folder = os.path.join(OUTPUT_FOLDER, pdf_base_name, "rendered_pages")

            logger.info(f"Process PDF file: {pdf_file}")

            # 提取图片和渲染页面
            extract_success = extract_images_from_pdf(pdf_path, images_output_folder, debug=True)
            render_success = render_pdf_page_as_image(pdf_path, rendered_pages_folder, zoom=2)

            # === 代码块2: OpenAI处理 ===
            logger.info("Processing with OpenAI...")
            if render_success:
                openai_success, result_path = process_with_openai(rendered_pages_folder, pdf_base_name)
            else:
                openai_success = False
                result_path = "Fail to render PDF"

            processed_files.append({
                'filename': pdf_file,
                'extract_success': extract_success,
                'render_success': render_success,
                'openai_success': openai_success,
                'result_path': result_path if openai_success else None
            })

        # === 代码块3: 生成ESG报告 ===
        try:
            logger.info("Generating ESG report...")
            json_folder = os.path.join(OUTPUT_FOLDER, 'json_output')
            if not os.path.exists(json_folder):
                logger.error("JSON output folder not found")
                return jsonify({
                    'message': 'Processing completed but ESG report generation failed - JSON folder not found',
                    'status': 'partial_success',
                    'processed_files': processed_files
                }), 200

            # 初始化ESG报告生成器
            generator = ESGReportGenerator()

            # 处理JSON数据
            df = generator.process_json_data(json_folder)
            
            # 创建输出文件夹结构
            report_folder = os.path.join(OUTPUT_FOLDER, 'esg_reports')
            processed_data_folder = os.path.join(OUTPUT_FOLDER, 'processed_data')
            os.makedirs(report_folder, exist_ok=True)
            os.makedirs(processed_data_folder, exist_ok=True)
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存JSON报告
            report_path = os.path.join(report_folder, f"esg_report.json")
            report_data = df.to_dict(orient='records')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 保存CSV文件
            csv_path = os.path.join(processed_data_folder, f"esg_scores.csv")
            df.to_csv(csv_path, encoding='utf-8-sig', index=False)

            # 生成处理结果摘要
            summary = {
                'total_files_processed': len(processed_files),
                'successful_extractions': sum(1 for f in processed_files if f['extract_success']),
                'successful_renders': sum(1 for f in processed_files if f['render_success']),
                'successful_analyses': sum(1 for f in processed_files if f['openai_success']),
                'total_records_processed': len(df),
                'unique_companies': len(df['Company Report Name'].unique()),
                'report_path': report_path,
                'csv_path': csv_path
            }

            return jsonify({
                'message': 'Processing completed successfully',
                'status': 'success',
                'processed_files': processed_files,
                'summary': summary,
                'report_path': report_path,
                'csv_path': csv_path
            }), 200

        except Exception as e:
            logger.error(f"Error occurred while generating the ESG report: {str(e)}")
            return jsonify({
                'message': 'The processing completed but the ESG report failed to be generated',
                'status': 'partial_success',
                'processed_files': processed_files,
                'error': str(e)
            }), 200

    except Exception as e:
        logger.error(f"Error occurred during processing: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500







@app.route('/analyze_esg', methods=['POST'])
def analyze_esg():
    try:
        # 运行 ESG 分析代码
        import pandas as pd
        import numpy as np
        
        # 读取数据
        
        # 设置ESG权重
        weights = {'E': 0.5, 'S': 0.3, 'G': 0.2}
        
        import pandas as pd
        import numpy as np

        # Assuming the data is saved in a file named "company_data.csv"
        df = pd.read_csv('output\processed_data\esg_scores.csv')

        # Set the weight for each ESG category
        weights = {
            'E': 0.5,  # Environmental (E) contributes 50%
            'S': 0.3,  # Social (S) contributes 30%
            'G': 0.2   # Governance (G) contributes 20%
        }

        # Define categorized metrics
        environmental_metrics = [
            "Greenhouse Gas Emissions('GHG')",
            "Energy Consumption(GJ)",
            "Water Consumption",
            "Waste Generation"
        ]

        social_metrics = [
            "Age-Based Diversity(existing employees by age group)",
            "Development & Training",
            "Employment",
            "Gender Diversity",
            "Occupational Health & Safety"
        ]

        governance_metrics = [
            "Alignment with Frameworks And Disclosure Practices",
            "Assurance of Sustainability Report",
            "Board Composition",
            "ESG-related Certifications",
            "Economic Performance",
            "Ethical Behaviour(anti-corruption)",
            "Management Diversity"
        ]



        # Classification function
        def classify_metrics(label):
            if label in environmental_metrics:
                return 'E'
            elif label in social_metrics:
                return 'S'
            elif label in governance_metrics:
                return 'G'
            else:
                return 'Unknown'

        # Classify each Predicted_label
        df['Category'] = df['Predicted_label'].apply(classify_metrics)

        # Calculate the average score for each category
        category_scores = df.groupby('Category')['Score'].mean().reset_index()

        # Calculate the weighted score
        def calculate_scores(category_scores, weights):
            category_score = {'E': 0, 'S': 0, 'G': 0}
            
            # Get the average score for each category
            for category in ['E', 'S', 'G']:
                category_score[category] = category_scores[category_scores['Category'] == category]['Score'].mean() if not category_scores[category_scores['Category'] == category].empty else 0
            
            # Calculate the weighted total score
            weighted_score = (
                category_score['E'] * weights['E'] + 
                category_score['S'] * weights['S'] + 
                category_score['G'] * weights['G']
            )
            
            return category_score, weighted_score

        # Calculate the scores
        category_score, total_score = calculate_scores(category_scores, weights)

        # Standardize scores to range 0-100 and round to two decimal places
        def standardize_score(score, score_range):
            standardized = (score - score_range[0]) / (score_range[1] - score_range[0]) * 100
            return round(standardized, 2)

        # Set score range
        score_range = {
            'E': (0, 10),
            'S': (0, 10),
            'G': (0, 10)
        }

        # Standardize the scores
        standardized_scores = {
            category: standardize_score(category_score[category], score_range[category])
            for category in category_score
        }

        # Standardize the total score
        total_standardized_score = standardize_score(total_score, (0, 10))

        # Score classification
        def categorize_score(score):
            if score < 50:
                return 'Poor'
            elif score > 70:
                return 'Good'
            else:
                return 'Average'

        # Output the results
        category_labels = [f'{category} Score' for category in ['E', 'S', 'G']]
        print(f"Company's ESG Scores:")
        for category, score in standardized_scores.items():
            print(f"  {category_labels.pop(0)}: {score:.2f}")
            
        print(f"  Total Score: {total_standardized_score:.2f}")
        print(f"  Total Score Classification: {categorize_score(total_standardized_score)}")

        environmental_score = standardized_scores['E']
        social_score = standardized_scores['S']
        governance_score = standardized_scores['G']

        # Assuming standardized_scores is a dictionary with ESG scores for each category
        standardized_scores = {
            'E': environmental_score,  # Environmental score
            'S': social_score,         # Social score
            'G': governance_score      # Governance score
        }

        # Mapping of category codes to their full names for easier output
        category_names = {
            'E': 'Environmental',
            'S': 'Social',
            'G': 'Governance'
        }

        # Function to determine the highest and lowest rated dimensions
        def get_highest_and_lowest_rated(scores):
            # Find the dimension with the highest score
            highest_rated_dimension = category_names[max(scores, key=scores.get)]
            # Find the dimension with the lowest score
            lowest_rated_dimension = category_names[min(scores, key=scores.get)]
            
            return highest_rated_dimension, lowest_rated_dimension

        # Get the results
        highest_rated_dimension, lowest_rated_dimension = get_highest_and_lowest_rated(standardized_scores)

        # Display the results
        print("Highest Rated Dimension:", highest_rated_dimension)
        print("Lowest Rated Dimension:", lowest_rated_dimension)


        import pandas as pd
        import numpy as np
        import plotly.graph_objects as go
        import dash
        from dash import dcc, html

        # 假设数据文件名为 "company_data.csv"
        df = pd.read_csv("output\processed_data\esg_scores.csv")

        # 设置ESG权重
        weights = {'E': 0.5, 'S': 0.3, 'G': 0.2}

        # 定义指标分类
        # Define categorized metrics
        environmental_metrics = [
            "Greenhouse Gas Emissions('GHG')",
            "Energy Consumption(GJ)",
            "Water Consumption",
            "Waste Generation"
        ]

        social_metrics = [
            "Age-Based Diversity(existing employees by age group)",
            "Development & Training",
            "Employment",
            "Gender Diversity",
            "Occupational Health & Safety"
        ]

        governance_metrics = [
            "Alignment with Frameworks And Disclosure Practices",
            "Assurance of Sustainability Report",
            "Board Composition",
            "ESG-related Certifications",
            "Economic Performance",
            "Ethical Behaviour(anti-corruption)",
            "Management Diversity"
        ]

        # 分类函数
        def classify_metrics(label):
            if label in environmental_metrics:
                return 'E'
            elif label in social_metrics:
                return 'S'
            elif label in governance_metrics:
                return 'G'
            else:
                return 'Unknown'

        # 对每个指标进行分类
        df['Category'] = df['Predicted_label'].apply(classify_metrics)

        # 按类别计算各指标均值
        category_avg_scores = df.groupby(['Category', 'Predicted_label'])['Score'].mean().reset_index()

        # 创建柱状图展示各指标的均值
        bar_chart = go.Figure([
            go.Bar(
                x=category_avg_scores['Predicted_label'], 
                y=category_avg_scores['Score'],
                name="ESG Scores",
                marker=dict(color=category_avg_scores['Score'], colorscale='Viridis')
            )
        ])

        # 计算每个类别的得分均值
        category_scores = df.groupby('Category')['Score'].mean().to_dict()
        E_score, S_score, G_score = category_scores.get('E', 0), category_scores.get('S', 0), category_scores.get('G', 0)

        # 计算加权总得分
        total_score = E_score * weights['E'] + S_score * weights['S'] + G_score * weights['G']

        # Standardize scores to range 0-100 and round to two decimal places
        def standardize_score(score, score_range):
            standardized = (score - score_range[0]) / (score_range[1] - score_range[0]) * 100
            return round(standardized, 2)


        # 设置得分范围
        score_range = {'E': (0, 10), 'S': (0, 10), 'G': (0, 10)}

        # 标准化得分
        standardized_scores = {
            'E': standardize_score(E_score, score_range['E']),
            'S': standardize_score(S_score, score_range['S']),
            'G': standardize_score(G_score, score_range['G']),
        }
        total_standardized_score = round(standardize_score(total_score, (0, 10)),2)

        # 仪表图
        gauge_e = go.Figure(go.Indicator(
            mode="gauge+number", value=standardized_scores['E'],
            title={'text': "Environmental (E) Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        gauge_s = go.Figure(go.Indicator(
            mode="gauge+number", value=standardized_scores['S'],
            title={'text': "Social (S) Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        gauge_g = go.Figure(go.Indicator(
            mode="gauge+number", value=standardized_scores['G'],
            title={'text': "Governance (G) Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        gauge_total = go.Figure(go.Indicator(
            mode="gauge+number", value=total_standardized_score,
            title={'text': "Total ESG Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        # Dash应用布局
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.H1("Company ESG Performance Dashboard"),
            html.P("This dashboard shows the ESG performance of Company XYZ based on recent scoring."),

            # ESG Bar Chart
            dcc.Graph(id='esg-bar-chart', figure=bar_chart),

            html.H2("ESG Score Visualization"),
            html.Div([
                dcc.Graph(id='gauge-e', figure=gauge_e, style={'display': 'inline-block', 'width': '45%'}),
                dcc.Graph(id='gauge-s', figure=gauge_s, style={'display': 'inline-block', 'width': '45%'})
            ]),
            html.Div([
                dcc.Graph(id='gauge-g', figure=gauge_g, style={'display': 'inline-block', 'width': '45%'}),
                dcc.Graph(id='gauge-total', figure=gauge_total, style={'display': 'inline-block', 'width': '45%'})
            ]),

            html.H2("Key Insights"),
            html.P("This dashboard provides an overview of the ESG performance across various categories, along with an overall ESG score.")
        ])

        # 运行应用
        if __name__ == '__main__':
            app.run_server(debug=True)

        import dash
        from dash import dcc, html
        import plotly.graph_objects as go

        # Your figures
        gauge_e = go.Figure(go.Indicator(
            mode="gauge+number", value=standardized_scores['E'],
            title={'text': "Environmental (E) Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        gauge_s = go.Figure(go.Indicator(
            mode="gauge+number", value=standardized_scores['S'],
            title={'text': "Social (S) Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        gauge_g = go.Figure(go.Indicator(
            mode="gauge+number", value=standardized_scores['G'],
            title={'text': "Governance (G) Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        gauge_total = go.Figure(go.Indicator(
            mode="gauge+number", value=total_standardized_score,
            title={'text': "Total ESG Score"},
            gauge={'axis': {'range': [None, 100]},
                'steps': [{'range': [0, 40], 'color': "red"},
                            {'range': [40, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}]
                }
        ))

        # Dash app setup
        app = dash.Dash(__name__)

        import plotly.graph_objects as go

        # Assuming `gauge_e`, `gauge_s`, `gauge_g`, and `gauge_total` are your Plotly figures
        gauge_e.write_html('gauge_e.html')
        gauge_s.write_html('gauge_s.html')
        gauge_g.write_html('gauge_g.html')
        gauge_total.write_html('gauge_total.html')
        bar_chart.write_html("bar_chart.html")
        # Now you can manually create an HTML template or use an HTML file to link these files
        html_template = """
        <html>
        <head>
            <title>Company ESG Performance Dashboard</title>
        </head>
        <body>
            <h1>Company ESG Performance Dashboard</h1>
            <p>This dashboard shows the ESG performance of Company XYZ based on recent scoring.</p>

            <h2>ESG Score Visualization</h2>
            <div>
                <!-- First row with two gauges -->
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <h3>Environmental (E) Score</h3>
                        <iframe src="gauge_e.html" width="500" height="400"></iframe>
                    </div>
                    <div>
                        <h3>Social (S) Score</h3>
                        <iframe src="gauge_s.html" width="500" height="400"></iframe>
                    </div>
                </div>

                <!-- Second row with two gauges -->
                <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                    <div>
                        <h3>Governance (G) Score</h3>
                        <iframe src="gauge_g.html" width="500" height="400"></iframe>
                    </div>
                    <div>
                        <h3>Total ESG Score</h3>
                        <iframe src="gauge_total.html" width="500" height="400"></iframe>
                    </div>
                </div>
            </div>

            <!-- Adding the bar chart here -->
            <h2>ESG Score Distribution</h2>
            <div>
                <h3>ESG Scores by Category</h3>
                <iframe src="bar_chart.html" width="800" height="600"></iframe>
            </div>

            <h2>Key Insights</h2>
            <p>This dashboard provides an overview of the ESG performance across various categories, along with an overall ESG score.</p>
        </body>
        </html>
        """


        with open('esg_dashboard_report.html', 'w') as f:
            f.write(html_template)

        import random
        from jinja2 import Environment, FileSystemLoader
        # Generate random industry average values between 5 and 9 for each indicator
        random.seed(42)  # Set random seed for reproducibility
        industry_avg_dict = {indicator: round(random.uniform(5, 9), 2) for indicator in df['Predicted_label'].unique()}

        # Calculate company values for each indicator (mean score for each Predicted_label)
        category_avg_scores = df.groupby('Predicted_label')['Score'].mean().reset_index()
        category_avg_scores['Score'] = category_avg_scores['Score'].round(2)  # Round to 2 decimal places

        # Prepare the indicator data
        indicator_data = []

        # Populate the data list with company value, industry average, and performance summary
        for _, row in category_avg_scores.iterrows():
            indicator = row['Predicted_label']
            company_value = row['Score']
            industry_avg = industry_avg_dict.get(indicator, 0)  # Default to 0 if not found
            
            # Calculate performance summary
            if company_value > industry_avg:
                performance_summary = f"Company is performing above the industry average by {round(company_value - industry_avg, 2)} points."
            elif company_value < industry_avg:
                performance_summary = f"Company is performing below the industry average by {round(industry_avg - company_value, 2)} points."
            else:
                performance_summary = "Company is performing at the industry average."
            
            # Add to the indicator data list
            indicator_data.append({
                'indicator': indicator,
                'company_value': company_value,
                'industry_avg': industry_avg,
                'performance_summary': performance_summary
            })


        
        from jinja2 import Environment, FileSystemLoader
        from datetime import date
        import matplotlib.pyplot as plt
        import base64
        import io
        data = {
            "company_name": "Sample Company",
            "upload_date": date.today().strftime("%Y-%m-%d"),
            "analysis_date": date.today().strftime("%Y-%m-%d"),
            "background": {
                "introduction": "focused on sustainable innovation in its industry..."
            },
            "highlights": {
                "strategy": "Company's multi-year strategy for sustainable growth...",
                "goals": [
                    {"indicator": "Energy Efficiency", "value": 85, "industry_avg": 78, "summary": "Above industry average."},
                    # Add more indicators as needed
                ]
            },
            "scores": {
                "environmental": environmental_score,  # Replace with actual scores
                "social": social_score,         # Replace with actual scores
                "governance": governance_score,     # Replace with actual scores
                "total": total_standardized_score,         # Replace with actual scores
                "industry_position_env": 80,  # Replace with actual scores
                "industry_position_soc": 75,  # Replace with actual scores
                "industry_position_gov": 70,  # Replace with actual scores
                "industry_position_total":80,  # Replace with actual scores
                "environmental_summary": "Good progress in environmental practices.",
                "social_summary": "Strong social initiatives.",
                "governance_summary": "Governance requires improvement.",
                "total_summary": "Good Performance in ESG"
            },
            "achievements_outlook": "Company's efforts align with upcoming regulatory trends...",
            "highest_rated_dimension": "Environmental",
            "lowest_rated_dimension": "Governance",
            "contact_info": "contact@sustainex.com"
        }

        # Define thresholds and summaries based on scores
        def update_industry_position_and_summary(data):
            # Environmental position and summary
            if data["scores"]["environmental"] > 70:
                data["industry_position_env"] = "Top 10%"
                data["environmental_summary"] = "Strong in emissions reduction."
            elif 40 < data["scores"]["environmental"] <= 70:
                data["industry_position_env"] = "Median"
                data["environmental_summary"] = "Average in emissions reduction."
            else:
                data["industry_position_env"] = "Below Median"
                data["environmental_summary"] = "Needs improvement in emissions reduction."
            
            # Social position and summary
            if data["scores"]["social"] > 70:
                data["industry_position_soc"] = "Top 10%"
                data["social_summary"] = "Strong in labor standards."
            elif 40 < data["scores"]["social"] <= 70:
                data["industry_position_soc"] = "Median"
                data["social_summary"] = "Average on labor standards."
            else:
                data["industry_position_soc"] = "Below Median"
                data["social_summary"] = "Needs improvement in labor standards."
            
            # Governance position and summary
            if data["scores"]["governance"] > 70:
                data["industry_position_gov"] = "Top 10%"
                data["governance_summary"] = "Strong in transparency."
            elif 40 < data["scores"]["governance"] <= 70:
                data["industry_position_gov"] = "Median"
                data["governance_summary"] = "Average on transparency."
            else:
                data["industry_position_gov"] = "Below Median"
                data["governance_summary"] = "Needs improvement in transparency."
                
            # Total position and summary
            if data["scores"]["total"] > 70:
                data["industry_position_total"] = "Top 10%"
                data["total_summary"] = "Good Performance in ESG"
            elif 40 < data["scores"]["total"] <= 70:
                data["industry_position_total"] = "Median"
                data["total_summary"] = "Average Performance in ESG"
            else:
                data["industry_position_total"] = "Below Median"
                data["total_summary"] = "Needs improvement in ESG."

        # Call the function to update the data dictionary
        update_industry_position_and_summary(data)

        # Print the updated data dictionary to verify the updates
        df['Company Report Name'] = df['Company Report Name'].str.replace(r'(?i)report', '', regex=True)
        df['Company Report Name'] = df['Company Report Name'].str.replace('_', '', regex=True)
        company_name = df['Company Report Name'].iloc[1]
        print(company_name)

        data.update({
            "company_name": company_name,
            "upload_date": date.today().strftime("%Y-%m-%d"),
            "analysis_date": date.today().strftime("%Y-%m-%d"),
            "background": {
                "introduction": "focused on sustainable innovation in its industry...",
            },
            "highlights": {
                "strategy": "Company's multi-year strategy for sustainable growth...",
                "goals": [
                    {"indicator": "Energy Efficiency", "value": 85, "industry_avg": 78, "summary": "Above industry average."},
                    # Additional indicators here
                ]
            },
            "scores": {
                "environmental": data["scores"]["environmental"],
                "social": data["scores"]["social"],
                "governance": data["scores"]["governance"],
                "total": data["scores"]["total"],
                "industry_position_env": data["industry_position_env"],
                "industry_position_soc": data["industry_position_soc"],
                "industry_position_gov": data["industry_position_gov"],
                "industry_position_total": data["industry_position_total"],
                "environmental_summary": data["environmental_summary"],
                "social_summary": data["social_summary"],
                "governance_summary": data["governance_summary"],
                "total_summary": data["total_summary"]
            },
            "achievements_outlook": "Company's efforts align with upcoming regulatory trends...",
            "highest_rated_dimension": highest_rated_dimension,
            "lowest_rated_dimension": lowest_rated_dimension,
            "contact_info": "contact@sustainex.com"
        }  
        ) 

        # Determine which summary to use based on the total score
        high_score_summary_authority = (
            f"In conclusion, {data['company_name']} demonstrates strong ESG compliance, especially excelling in {data['highest_rated_dimension']}. "
            f"This level of performance highlights the company's proactive approach to meeting regulatory standards, aligning with best practices. "
            f"While minor enhancements could be made in {data['lowest_rated_dimension']}, the overall compliance is robust and meets expectations from regulatory perspectives."
        )

        low_score_summary_authority = (
            f"{data['company_name']} has shown commitment to ESG standards with strengths in {data['highest_rated_dimension']}. However, performance in "
            f"{data['lowest_rated_dimension']} remains below regulatory benchmarks, indicating areas for improvement. Addressing these gaps would enhance compliance "
            f"and reduce associated risks, aligning the company more closely with current regulatory standards."
        )

        high_score_summary_corporate = (
            f"{data['company_name']} has integrated ESG principles successfully, achieving strong results, particularly in {data['highest_rated_dimension']}. "
            f"This reflects the company’s commitment to sustainable practices and regulatory adherence. We will continue to strengthen areas like {data['lowest_rated_dimension']} "
            f"to further align with our strategic objectives and ensure sustained growth."
        )

        low_score_summary_corporate = (
            f"{data['company_name']} has made substantial progress in {data['highest_rated_dimension']} but acknowledges that {data['lowest_rated_dimension']} requires additional focus. "
            f"Improving this area is essential for meeting our corporate sustainability goals and enhancing our position within the industry. Focused efforts here will contribute "
            f"significantly to long-term resilience."
        )

        high_score_summary_investor = (
            f"As an investment, {data['company_name']} demonstrates exceptional ESG performance, excelling in {data['highest_rated_dimension']}. "
            f"This robust approach to sustainability reduces long-term risk and offers value to investors. Further improvements in {data['lowest_rated_dimension']} present "
            f"opportunities for even greater impact, reinforcing {data['company_name']}'s appeal as a sustainable investment."
        )

        low_score_summary_investor = (
            f"{data['company_name']} shows strengths in {data['highest_rated_dimension']} but continues to face challenges in {data['lowest_rated_dimension']}. "
            f"Strategic improvements in this area are essential to meet ESG compliance and reduce potential risks, enhancing the company’s attractiveness as a sustainable investment. "
            f"With a focus on long-term ESG commitments, we aim to build investor confidence in our sustainability trajectory."
        )

        # Define the "Achievements and Outlook" templates for each perspective
        achievements_outlook_templates = {
            "authority": {
                "achievements": (
                    f"{data['company_name']} has made significant progress in aligning with ESG compliance standards. "
                    f"The company's strong adherence to regulatory guidelines, especially in {data['highest_rated_dimension']}, "
                    f"highlights its dedication to meeting authority expectations. By implementing structured policies "
                    f"and protocols,{data['company_name']} has established a solid foundation for ongoing compliance and sustainable operations."
                
                    f"Looking forward, {data['company_name']} plans to further enhance its performance by focusing on areas such as {data['lowest_rated_dimension']}. "
                    f"These efforts will not only support its long-term growth but also improve alignment with evolving regulatory standards. "
                    f"Authorities can expect a proactive approach to sustainable practices from {data['company_name']}, positioning it as a leader in regulatory "
                    f"compliance within its industry."
                )
            },
            "corporate": {
                "achievements": (
                    f"{data['company_name']} has successfully embedded ESG principles into its corporate strategy, achieving strong results particularly "
                    f"in {data['highest_rated_dimension']}. These accomplishments demonstrate the company’s proactive commitment to corporate responsibility "
                    f"and sustainable growth, as well as its capability to integrate sustainability with operational goals."
                
                    f"Going forward, {data['company_name']} aims to advance its sustainability agenda by enhancing practices in {data['lowest_rated_dimension']}. "
                    f"By prioritizing resource allocation and innovation in this area, {data['company_name']} expects to bolster its competitive edge while "
                    f"achieving full alignment with ESG objectives. This commitment will ensure the company’s resilience and growth in an increasingly "
                    f"sustainability-focused marketplace."
                )
            },
            "investor": {
                "achievements": (
                    f"{data['company_name']} presents a compelling case for sustainable investment, particularly through its strong performance in "
                    f"{data['highest_rated_dimension']}. This area of achievement indicates that {data['company_name']} is not only aware of ESG risks but is also "
                    f"taking active steps to mitigate them, thereby reducing potential exposure and enhancing long-term value for investors."
            
                    f"Investors can expect {data['company_name']} to continue prioritizing sustainability, with a particular focus on improvement in "
                    f"{data['lowest_rated_dimension']}. Targeted efforts in this area will reinforce {data['company_name']}’s commitment to ESG principles, "
                    f"paving the way for robust, sustainable growth. This forward-thinking approach is expected to create greater value and strengthen "
                    f"investor confidence in the company’s future."
                )
            }
        }

        # Populate summaries conditionally based on the total score
        data.update({
            "summary_authority": high_score_summary_authority if data["scores"]["total"] > 70 else low_score_summary_authority,
            "summary_corporate": high_score_summary_corporate if data["scores"]["total"] > 70 else low_score_summary_corporate,
            "summary_investor": high_score_summary_investor if data["scores"]["total"] > 70 else low_score_summary_investor,
            "achievements_outlook_authority": achievements_outlook_templates["authority"]["achievements"],
            "achievements_outlook_corporate": achievements_outlook_templates["corporate"]["achievements"],
            "achievements_outlook_investor": achievements_outlook_templates["investor"]["achievements"],
            
        })
        data["indicator_data"] = indicator_data
        data["highlights"] = {"goals": indicator_data}
        
        # Define data variables, including calculated scores and visualizations
        # Extend data with additional fields after updating

        # Example of creating a sample bar plot and converting it to base64
        def create_bar_chart():
            # Generate the first bar chart
            fig, ax = plt.subplots()
            categories = ["Environmental", "Social", "Governance"]
            values = [data["scores"]["environmental"], data["scores"]["social"], data["scores"]["governance"]]
            ax.bar(categories, values, color=["#2e8b57", "#4682b4", "#d2691e"])
            ax.set_xlabel("Dimensions")
            ax.set_ylabel("Scores")
            ax.set_title("ESG Scores by Dimension")
            
            # Convert the plot to a base64 string
            img = io.BytesIO()
            fig.savefig(img, format='png')
            img.seek(0)
            img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
            
            # Close the plot to avoid conflicts
            plt.close(fig)
            
            return img_base64

        # Add the base64 image data to the data dictionary
        data["bar_chart_base64"] = create_bar_chart()

        # Template paths for each role
        templates = {
            "authority": "./template/template_authority.html",
            "corporate_executives": "./template/template_corporate_executives.html",
            "investor": "./template/template_investor.html"
        }

        # Environment setup
        env = Environment(loader=FileSystemLoader('.'))

        # Loop through each template and generate a report
        for role, template_path in templates.items():
            template = env.get_template(template_path)
            html_content = template.render(data=data)
            
            # Save the rendered HTML to a file
            output_file = f"esg_report_for_{role}_{company_name}.html"
            with open(output_file, "w") as f:
                f.write(html_content)
            print(f"Generated report for {role}: {output_file}")


        
        # Add the base64 image data to the data dictionary
        import seaborn as sns
        data["bar_chart_base64"] = create_bar_chart()
        def create_bar_chart_2(category_avg_scores):
            # 创建柱状图
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Predicted_label', y='Score', data=category_avg_scores, palette='viridis')

            # 添加标题和标签
            plt.title('ESG Scores by Category', fontsize=16)
            plt.xlabel('Category', fontsize=12)
            plt.ylabel('Score', fontsize=12)

            # 调整 x 轴标签以避免重叠
            plt.xticks(rotation=45, ha='right', fontsize=8)  # 增加旋转角度并设置水平对齐
            plt.tight_layout()

            # 将图表保存到 BytesIO
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            img_base64_2 = base64.b64encode(img.getvalue()).decode("utf-8")

            # 返回 Base64 字符串
            return img_base64_2

        # 调用函数生成 Base64 编码并添加到 data 字典中
        data = {}  # 初始化数据字典
        data["bar_chart_base64_2"] = create_bar_chart_2(category_avg_scores)
        
        return jsonify({
            'status': 'success',
            'message': 'ESG analysis completed successfully',
            'reports': {
                'authority': '/report/authority',
                'corporate': '/report/corporate_executives', 
                'investor': '/report/investor'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in ESG analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
        
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return send_file('gauge_total.html', as_attachment=False)

@app.route('/api/histogram', methods=['GET'])
def histogram():
    return send_file('bar_chart.html', as_attachment=False)

@app.route('/api/dashboard1', methods=['GET'])
def dashboard1():
    return send_file("esg_report_for_authority.html", as_attachment=False)

@app.route('/api/dashboard2', methods=['GET'])
def dashboard2():
    return send_file("esg_report_for_corporate_executives.html", as_attachment=False)

@app.route('/api/dashboard3', methods=['GET'])
def dashboard3():
    return send_file("B_Group/esg_report_for_investor.html", as_attachment=False)
    

# 路由: 提供 Authority 的报告
@app.route('/report/authority', methods=['GET'])
def report_authority():
    return send_file("esg_report_for_authority.html", as_attachment=False)

# 路由: 提供 Corporate Executives 的报告
@app.route('/report/corporate_executives', methods=['GET'])
def report_corporate_executives():
    return send_file("esg_report_for_corporate_executives.html", as_attachment=False)

# 路由: 提供 Investor 的报告
@app.route('/report/investor', methods=['GET'])
def report_investor():
    return send_file("esg_report_for_investor.html", as_attachment=False)









@app.errorhandler(413)
def request_entity_too_large(error):
    logger.error("File too large")
    return jsonify({'error': 'File too large. Maximum size is 10MB'}), 413


    
# 确保在启动时创建必要的目录
create_required_directories()

if __name__ == '__main__':
    app.run(debug=True)