# %%
import configparser
import os
import fitz  # PyMuPDF
from PIL import Image

# 读取配置文件
config = configparser.ConfigParser()
current_path = os.getcwd()
config.read(os.path.join(current_path, 'config.ini'))

input_path = config['DEFAULT']['Input-Path']
output_path = config['DEFAULT']['Output-Path']
debug = config['DEFAULT'].getboolean('Debug')

# 确保输入和输出路径存在
if not os.path.exists(input_path):
    print(f"Input path does not exist: {input_path}")
    raise FileNotFoundError(f"Input path does not exist: {input_path}")

if not os.path.exists(output_path):
    os.makedirs(output_path)
    print(f"Created output directory: {output_path}")

# 定义提取图片的函数
def extract_images_from_pdf(pdf_path, output_folder):
    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF file {pdf_path}: {e}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        if debug:
            print(f"Created folder: {output_folder}")

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        if not image_list:
            if debug:
                print(f"No images found on page {page_num + 1}.")
            continue

        for image_index, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                # 使用 page_num 和 image_index 确保文件名唯一
                image_name = f"image_{page_num + 1}_{image_index + 1}.{image_ext}"
                image_path = os.path.join(output_folder, image_name)

                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                print(f"Saved image: {image_path}")

            except Exception as e:
                print(f"Failed to extract image {image_index + 1} on page {page_num + 1}: {e}")

# 定义渲染页面为图像的函数
def render_pdf_page_as_image(pdf_path, output_folder, zoom=2):
    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF file {pdf_path}: {e}")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        if debug:
            print(f"Created folder: {output_folder}")

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)  # 放大倍率
        try:
            pix = page.get_pixmap(matrix=mat)
            image_name = f"page_{page_num + 1}.png"
            image_path = os.path.join(output_folder, image_name)
            pix.save(image_path)
            print(f"Rendered page {page_num + 1} as image: {image_path}")
        except Exception as e:
            print(f"Failed to render page {page_num + 1}: {e}")

# 获取 input_path 目录中的所有 PDF 文件
pdf_files = [f for f in os.listdir(input_path) if f.lower().endswith('.pdf')]

if not pdf_files:
    print("No PDF files found in the input directory.")
else:
    print(f"Found {len(pdf_files)} PDF file(s) in the input directory.")

# 对每个 PDF 文件进行图片提取和页面渲染
for pdf_file in pdf_files:
    pdf_path = os.path.join(input_path, pdf_file)

    # 为每个 PDF 创建单独的文件夹
    pdf_base_name = os.path.splitext(pdf_file)[0]
    images_output_folder = os.path.join(output_path, pdf_base_name, "extracted_images")
    rendered_pages_folder = os.path.join(output_path, pdf_base_name, "rendered_pages")

    print(f"\nProcessing PDF: {pdf_file}")

    # 提取图片
    print("Extracting images...")
    extract_images_from_pdf(pdf_path, images_output_folder)

    # 渲染页面为图像
    print("Rendering pages as images...")
    render_pdf_page_as_image(pdf_path, rendered_pages_folder, zoom=2)

    print(f"Completed processing {pdf_file}\n")

print("All PDF files have been processed.")



# %%
import os
import base64
import json
from dotenv import load_dotenv
import openai
import re

from openai import OpenAI

# Load environment variables if needed
load_dotenv()

# API setup
client = OpenAI(
    api_key=os.getenv("API_KEY", "your_default_api_key"),
    base_url=os.getenv("BASE_URL", "https://api.openai.com/v1")
)

model_name = "gpt-4o"

# Create output directory if it doesn't exist
os.makedirs(model_name, exist_ok=True)
json_output_path = f"{model_name}/CDL Hospitality report 2021.json"

# Path to your extracted images
extracted_images_dir = r'.\output\CDL Hospitality report 2021\rendered_pages'


def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None


system_prompt = 'You are an OCR engineer'
text_content = 'Extract all data content from the document'
text_content2 = '''Extract data information with numbers from the text and convert it into JSON format, remember that only the data with numbers is needed.'''


extracted_data_list = []

if os.path.exists(extracted_images_dir):
    file_names = [file_name for file_name in os.listdir(extracted_images_dir) if
                  re.match(r'page_(\d+)\.png', file_name)]
    sorted_file_names = sorted(file_names, key=lambda x: int(re.search(r'(\d+)', x).group()))

    for file_name in sorted_file_names:
        image_path = os.path.join(extracted_images_dir, file_name)
        print(f"Processing file: {file_name}")  # Print the current page being processed

        if not os.path.isfile(image_path):
            print(f"File not found: {image_path}")
            continue

        base64_image = encode_image(image_path)
        if not base64_image:
            print(f"Skipping {file_name} due to encoding error.")
            continue

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

        except Exception as e:
            print(f"Error during completion for {file_name}: {e}")
            continue

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
            print(f"Extracted JSON for {file_name}: {extracted_data_json}")  # Print the content of extracted_data_json
            data = json.loads(extracted_data_json)
            extracted_data_list.append({file_name: data})  # Append to list for JSON file saving

        except Exception as e:
            print(f"Error processing JSON for {file_name}: {e}")
            continue

# Save extracted data as JSON file
with open(json_output_path, 'w', encoding='utf-8') as json_file:
    json.dump(extracted_data_list, json_file, ensure_ascii=False, indent=4)

print(f"JSON data saved to {json_output_path}")



