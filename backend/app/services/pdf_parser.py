import io
import re
import hashlib
from typing import Tuple, Optional
import pdfplumber
import PyPDF2


class PDFParser:
    """PDF简历解析器"""
    
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """计算文件内容的MD5哈希"""
        return hashlib.md5(file_content).hexdigest()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清洗文本内容"""
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符但保留常用标点和编程语言符号（如C++、C#）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,;:!?@_#+\-]', ' ', text)
        # 移除多余空格
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    @classmethod
    def parse_pdf(cls, file_content: bytes) -> Tuple[str, str]:
        """
        解析PDF文件，提取文本内容
        
        Args:
            file_content: PDF文件字节内容
            
        Returns:
            Tuple[文件哈希, 提取的文本]
        """
        file_hash = cls.calculate_file_hash(file_content)
        
        # 尝试使用pdfplumber解析（对复杂布局支持更好）
        text = cls._parse_with_pdfplumber(file_content)
        
        # 如果pdfplumber解析失败或内容太少，尝试PyPDF2
        if len(text.strip()) < 100:
            text = cls._parse_with_pypdf2(file_content)
        
        # 清洗文本
        cleaned_text = cls.clean_text(text)
        
        return file_hash, cleaned_text
    
    @classmethod
    def _parse_with_pdfplumber(cls, file_content: bytes) -> str:
        """使用pdfplumber解析PDF"""
        text_parts = []
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            print(f"pdfplumber解析失败: {e}")
        
        return '\n'.join(text_parts)
    
    @classmethod
    def _parse_with_pypdf2(cls, file_content: bytes) -> str:
        """使用PyPDF2解析PDF"""
        text_parts = []
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        except Exception as e:
            print(f"PyPDF2解析失败: {e}")
        
        return '\n'.join(text_parts)
    
    @staticmethod
    def extract_sections(text: str) -> dict:
        """
        尝试提取简历的各个部分
        
        Args:
            text: 简历文本
            
        Returns:
            各部分的文本字典
        """
        sections = {
            'basic': '',
            'education': '',
            'experience': '',
            'projects': '',
            'skills': ''
        }
        
        # 常见的简历章节标题
        section_patterns = {
            'basic': r'(个人信息|基本信息|个人资料|简介|概况)',
            'education': r'(教育背景|学历|教育经历|毕业院校)',
            'experience': r'(工作经历|工作经验|实习经历|职业经历)',
            'projects': r'(项目经历|项目经验|项目描述)',
            'skills': r'(专业技能|技能|技术栈|掌握技能)'
        }
        
        # 简单的章节分割逻辑
        lines = text.split('\n')
        current_section = 'basic'
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # 检测章节标题
            for section, pattern in section_patterns.items():
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    current_section = section
                    break
            
            sections[current_section] += line + '\n'
        
        return sections


pdf_parser = PDFParser()
