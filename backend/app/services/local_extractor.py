import re
from typing import Dict, Optional, List

from app.models.schemas import (
    ResumeExtractedInfo, 
    ResumeBasicInfo, 
    ResumeJobInfo, 
    ResumeBackground
)


class LocalExtractor:
    """本地简历信息提取器（不依赖外部AI API）"""
    
    # 常见的学校名称关键词，用于排除
    SCHOOL_KEYWORDS = [
        '大学', '学院', '学校', '中学', '小学', '幼儿园',
        'University', 'College', 'School', 'Institute',
        '清华', '北大', '复旦', '交大', '浙大', '南大', '武大', '中大',
        '韶关学院', '北京大学', '清华大学', '复旦大学', '浙江大学'
    ]
    
    # 常见的公司关键词，用于排除
    COMPANY_KEYWORDS = [
        '公司', '集团', '企业', '科技', '网络', '软件', '信息',
        'Corp', 'Inc', 'Ltd', 'Company', 'Technology', 'Software'
    ]
    
    # 常见的职位关键词，用于排除
    JOB_KEYWORDS = [
        '工程师', '经理', '主管', '总监', '助理', '专员', '顾问',
        'Engineer', 'Manager', 'Director', 'Assistant', 'Specialist'
    ]
    
    @staticmethod
    def extract_resume_info(text: str) -> ResumeExtractedInfo:
        """
        从简历文本中提取关键信息
        
        Args:
            text: 简历文本内容
            
        Returns:
            ResumeExtractedInfo对象
        """
        # 提取各部分
        sections = LocalExtractor._extract_sections(text)
        
        # 提取基本信息
        basic_info = LocalExtractor._extract_basic_info(sections.get('basic', '') + ' ' + text)
        
        # 提取求职信息
        job_info = LocalExtractor._extract_job_info(sections.get('basic', '') + ' ' + text)
        
        # 提取背景信息
        background_info = LocalExtractor._extract_background_info(sections)
        
        # 提取技能
        skills = LocalExtractor._extract_skills(sections.get('skills', '') + ' ' + text)
        
        return ResumeExtractedInfo(
            basic=basic_info,
            job=job_info,
            background=background_info,
            skills=skills,
            raw_text=text[:1000]  # 保存前1000字符作为原始文本
        )
    
    @staticmethod
    def _extract_sections(text: str) -> Dict[str, str]:
        """
        提取简历的各个部分
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
    
    @staticmethod
    def _extract_basic_info(text: str) -> ResumeBasicInfo:
        """
        提取基本信息
        """
        # 提取姓名
        name = LocalExtractor._extract_name(text)
        
        # 提取电话
        phone = LocalExtractor._extract_phone(text)
        
        # 提取邮箱
        email = LocalExtractor._extract_email(text)
        
        # 提取地址
        address = LocalExtractor._extract_address(text)
        
        return ResumeBasicInfo(
            name=name,
            phone=phone,
            email=email,
            address=address
        )
    
    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """
        提取姓名 - 改进版本，避免误识别
        """
        # 首先尝试明确的姓名标签
        name_patterns = [
            r'姓名[:：]\s*([\u4e00-\u9fa5]{2,6})',
            r'Name[:：]\s*([A-Za-z\s]{2,20})',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                candidate = match.group(1).strip()
                # 验证不是学校或公司名称
                if LocalExtractor._is_valid_name(candidate):
                    return candidate
        
        # 如果没有明确的标签，尝试在个人信息部分查找
        # 查找2-3个汉字的名字，排除常见学校/公司/职位关键词
        personal_info_section = LocalExtractor._extract_personal_info_section(text)
        if personal_info_section:
            # 在个人信息部分查找名字
            name_candidates = re.findall(r'[\u4e00-\u9fa5]{2,3}', personal_info_section)
            for candidate in name_candidates:
                if LocalExtractor._is_valid_name(candidate):
                    return candidate
        
        return None
    
    @staticmethod
    def _is_valid_name(name: str) -> bool:
        """
        验证是否为有效的姓名（排除学校、公司、职位等）
        """
        if not name or len(name) < 2:
            return False
        
        # 检查是否包含学校关键词
        for keyword in LocalExtractor.SCHOOL_KEYWORDS:
            if keyword in name:
                return False
        
        # 检查是否包含公司关键词
        for keyword in LocalExtractor.COMPANY_KEYWORDS:
            if keyword in name:
                return False
        
        # 检查是否包含职位关键词
        for keyword in LocalExtractor.JOB_KEYWORDS:
            if keyword in name:
                return False
        
        # 检查是否包含数字（姓名通常不包含数字）
        if re.search(r'\d', name):
            return False
        
        # 检查是否包含英文字母（纯中文姓名通常不包含英文）
        if re.search(r'[a-zA-Z]', name):
            return False
        
        return True
    
    @staticmethod
    def _extract_personal_info_section(text: str) -> str:
        """
        提取个人信息部分
        """
        # 查找个人信息部分
        patterns = [
            r'个人信息[：:]?(.*?)(?=教育背景|工作经历|项目经历|专业技能|$)',
            r'基本信息[：:]?(.*?)(?=教育背景|工作经历|项目经历|专业技能|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到明确的个人信息部分，返回前500字符
        return text[:500]
    
    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """
        提取电话
        """
        # 常见的电话号码模式
        phone_patterns = [
            r'电话[:：]\s*(1[3-9]\d{9})',
            r'手机[:：]\s*(1[3-9]\d{9})',
            r'Phone[:：]\s*(\+?\d{8,15})',
            r'\b1[3-9]\d{9}\b',  # 简单的中国手机号
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """
        提取邮箱
        """
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0).strip()
        return None
    
    @staticmethod
    def _extract_address(text: str) -> Optional[str]:
        """
        提取地址
        """
        # 简单的地址提取
        address_patterns = [
            r'地址[:：]\s*(.+?)[\n,，]',
            r'Address[:：]\s*(.+?)[\n,，]',
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def _extract_job_info(text: str) -> ResumeJobInfo:
        """
        提取求职信息
        """
        # 提取求职意向
        intention = LocalExtractor._extract_intention(text)
        
        # 提取期望薪资
        expected_salary = LocalExtractor._extract_salary(text)
        
        return ResumeJobInfo(
            intention=intention,
            expected_salary=expected_salary
        )
    
    @staticmethod
    def _extract_intention(text: str) -> Optional[str]:
        """
        提取求职意向
        """
        intention_patterns = [
            r'求职意向[:：]\s*(.+?)[\n,，]',
            r'意向岗位[:：]\s*(.+?)[\n,，]',
            r'应聘职位[:：]\s*(.+?)[\n,，]',
        ]
        
        for pattern in intention_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def _extract_salary(text: str) -> Optional[str]:
        """
        提取期望薪资
        """
        salary_patterns = [
            r'期望薪资[:：]\s*(.+?)[\n,，]',
            r'薪资要求[:：]\s*(.+?)[\n,，]',
            r'薪酬[:：]\s*(.+?)[\n,，]',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def _extract_background_info(sections: Dict[str, str]) -> ResumeBackground:
        """
        提取背景信息
        """
        # 提取工作年限
        work_years = LocalExtractor._extract_work_years(sections.get('experience', '') + ' ' + sections.get('basic', ''))
        
        # 提取学历
        education = LocalExtractor._extract_education(sections.get('education', ''))
        
        # 提取项目经历
        projects = LocalExtractor._extract_projects(sections.get('projects', ''))
        
        return ResumeBackground(
            work_years=work_years,
            education=education,
            projects=projects
        )
    
    @staticmethod
    def _extract_work_years(text: str) -> Optional[str]:
        """
        提取工作年限
        """
        work_years_patterns = [
            r'工作年限[:：]\s*(.+?)[\n,，]',
            r'工作经验[:：]\s*(.+?)[\n,，]',
            r'(\d+年以上|\d+年经验|\d+年工作经验)',
        ]
        
        for pattern in work_years_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
        
        return None
    
    @staticmethod
    def _extract_education(text: str) -> Optional[str]:
        """
        提取学历
        """
        education_patterns = [
            r'学历[:：]\s*(.+?)[\n,，]',
            r'教育背景[:：]\s*(.+?)[\n,，]',
            r'(本科|硕士|博士|大专|高中|中专)',
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
        
        return None
    
    @staticmethod
    def _extract_projects(text: str) -> List[str]:
        """
        提取项目经历
        """
        projects = []
        
        # 简单的项目提取逻辑
        lines = text.split('\n')
        current_project = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if current_project:
                    projects.append(' '.join(current_project))
                    current_project = []
                continue
            
            # 检测项目标题（通常以数字或项目名称开头）
            if re.match(r'^[0-9]+[.、]', line_stripped) or re.match(r'^[项目|Project]', line_stripped):
                if current_project:
                    projects.append(' '.join(current_project))
                current_project = [line_stripped]
            else:
                current_project.append(line_stripped)
        
        if current_project:
            projects.append(' '.join(current_project))
        
        # 限制项目数量，避免过多
        return projects[:5]
    
    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """
        提取技能
        """
        skills = []
        
        # 常见的技能提取模式
        skill_patterns = [
            r'技能[:：]\s*(.+?)[\n,，]',
            r'技术栈[:：]\s*(.+?)[\n,，]',
            r'专业技能[:：]\s*(.+?)[\n,，]',
        ]
        
        for pattern in skill_patterns:
            match = re.search(pattern, text)
            if match:
                skill_text = match.group(1)
                # 分割技能
                skills.extend([s.strip() for s in re.split(r'[,，、;；]', skill_text) if s.strip()])
        
        # 从文本中提取常见的技术技能
        common_skills = [
            'Python', 'Java', 'C++', 'JavaScript', 'HTML', 'CSS', 'React', 'Vue',
            'Node.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'MySQL', 'PostgreSQL',
            'MongoDB', 'Redis', 'Docker', 'Git', 'Linux', 'AWS', 'Azure', 'SQL'
        ]
        
        for skill in common_skills:
            if skill.lower() in text.lower() and skill not in skills:
                skills.append(skill)
        
        return skills[:10]  # 限制技能数量
