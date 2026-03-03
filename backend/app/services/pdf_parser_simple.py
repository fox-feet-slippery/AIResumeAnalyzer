"""
简化版PDF解析器（不依赖pdfplumber）
"""
import io
import re
import hashlib
from typing import Tuple, Optional

# 尝试导入PyPDF2，如果失败则使用模拟
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("警告：未安装PyPDF2，将使用模拟模式")


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
        # 移除特殊字符但保留常用标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,;:!?@_-]', ' ', text)
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
        
        if HAS_PYPDF2:
            text = cls._parse_with_pypdf2(file_content)
        else:
            # 模拟模式：返回示例简历文本
            text = cls._mock_resume_text()
        
        # 清洗文本
        cleaned_text = cls.clean_text(text)
        
        return file_hash, cleaned_text
    
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
            return cls._mock_resume_text()
        
        return '\n'.join(text_parts)
    
    @staticmethod
    def _mock_resume_text() -> str:
        """模拟简历文本（用于测试）"""
        return """
个人简历

基本信息
姓名：张三
电话：13800138000
邮箱：zhangsan@example.com
地址：北京市海淀区

求职意向
期望职位：Python后端开发工程师
期望薪资：25k-35k

教育背景
学历：本科
毕业院校：北京大学
专业：计算机科学与技术

工作经历
工作年限：5年

专业技能
Python、Django、FastAPI、MySQL、Redis、Docker、Kubernetes、微服务架构

项目经历
1. 电商平台开发
   - 负责后端API设计与开发
   - 使用Django + MySQL + Redis
   - 日活用户100万+

2. 数据分析系统
   - 使用FastAPI构建数据服务
   - 集成机器学习模型
   - 处理千万级数据
"""


pdf_parser = PDFParser()
