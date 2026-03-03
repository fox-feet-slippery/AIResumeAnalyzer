import json
import re
from typing import Optional, List, Dict, Tuple
import os

from app.models.schemas import (
    ResumeExtractedInfo, 
    ResumeBasicInfo, 
    ResumeJobInfo, 
    ResumeBackground,
    JobKeywords,
    MatchingScore,
    MatchingAnalysis
)
from app.core.config import settings
from app.services.local_extractor import LocalExtractor


class AIExtractor:
    """AI信息提取器"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self.provider = "mock"  # 默认使用模拟模式
        self._init_client()
    
    def _init_client(self):
        """初始化AI客户端"""
        # 优先使用百度千帆AI
        qianfan_key = settings.QIANFAN_API_KEY or os.getenv("QIANFAN_API_KEY")
        if qianfan_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(
                    api_key=qianfan_key,
                    base_url=settings.QIANFAN_BASE_URL
                )
                self.model = "ernie-3.5-8k"
                self.provider = "qianfan"
                print("使用百度千帆AI")
                return
            except ImportError:
                pass
        
        # 其次使用DashScope（通义千问）
        dashscope_key = settings.DASHSCOPE_API_KEY or os.getenv("DASHSCOPE_API_KEY")
        if dashscope_key:
            try:
                import dashscope
                dashscope.api_key = dashscope_key
                self.client = dashscope
                self.model = "qwen-turbo"
                self.provider = "dashscope"
                print("使用DashScope API")
                return
            except ImportError:
                pass
        
        # 如果没有配置API，使用模拟模式
        self.provider = "mock"
        print("使用模拟模式（无AI API配置）")
    
    async def _call_ai(self, prompt: str, system_prompt: str = None) -> str:
        """调用AI模型"""
        if self.provider == "mock":
            return self._mock_response(prompt)
        
        try:
            if self.provider == "dashscope":
                from dashscope import Generation
                response = Generation.call(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt or "你是一个专业的简历分析助手。"},
                        {"role": "user", "content": prompt}
                    ],
                    result_format='message'
                )
                if response.status_code == 200:
                    return response.output.choices[0].message.content
                else:
                    raise Exception(f"API调用失败: {response.message}")
            
            elif self.provider == "qianfan":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt or "你是一个专业的简历分析助手。"},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
        
        except Exception as e:
            print(f"AI调用失败: {e}")
            # 标记为模拟模式，以便上层知道使用了模拟数据
            self.provider = "mock"
            return self._mock_response(prompt)
        
        return ""
    
    def _mock_response(self, prompt: str) -> str:
        """模拟AI响应（用于测试）"""
        if "提取关键信息" in prompt:
            return json.dumps({
                "name": "张三",
                "phone": "13800138000",
                "email": "zhangsan@example.com",
                "address": "北京市",
                "intention": "Python后端开发工程师",
                "expected_salary": "25k-35k",
                "work_years": "5年",
                "education": "本科",
                "projects": ["电商平台开发", "数据分析系统"],
                "skills": ["Python", "Django", "FastAPI", "MySQL", "Redis", "Docker"]
            }, ensure_ascii=False)
        elif "提取关键词" in prompt:
            return json.dumps({
                "skills": ["Python", "Java", "微服务", "MySQL"],
                "experience": ["3年以上", "后端开发经验"],
                "education": ["本科及以上", "计算机相关专业"],
                "other": ["良好的沟通能力", "团队合作"]
            }, ensure_ascii=False)
        elif "匹配度" in prompt or "评估以下简历与岗位" in prompt:
            return json.dumps({
                "overall_score": 85,
                "skill_match_rate": 90,
                "experience_relevance": 80,
                "education_match": 85,
                "matched_skills": ["Python", "MySQL"],
                "missing_skills": ["Java", "微服务"],
                "key_requirements": ["Python开发", "3年经验"],
                "suggestions": ["补充Java技能", "学习微服务架构"]
            }, ensure_ascii=False)
        return "{}"
    
    def _extract_json(self, text: str) -> dict:
        """从文本中提取JSON"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except:
            pass
        
        # 尝试从代码块中提取
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 尝试提取花括号内容
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return {}
    
    def _safe_get_string(self, data: dict, key: str, default: str = None) -> Optional[str]:
        """安全获取字符串值"""
        value = data.get(key, default)
        if value is None:
            return default
        if isinstance(value, str):
            return value
        if isinstance(value, (list, dict)):
            # 如果是列表或字典，转换为字符串
            return json.dumps(value, ensure_ascii=False)
        return str(value)
    
    def _safe_get_list(self, data: dict, key: str, default: list = None) -> List[str]:
        """安全获取列表值"""
        if default is None:
            default = []
        value = data.get(key, default)
        if value is None:
            return default
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            # 如果是字符串，尝试分割
            return [item.strip() for item in value.split(',') if item.strip()]
        return default
    
    async def extract_resume_info(self, resume_text: str) -> ResumeExtractedInfo:
        """
        从简历文本中提取关键信息
        
        Args:
            resume_text: 简历文本内容
            
        Returns:
            ResumeExtractedInfo对象
        """
        # 首先尝试使用AI提取
        system_prompt = """你是一个专业的简历分析助手。请从简历文本中提取以下信息，并以JSON格式返回：
{
    "name": "姓名（字符串）",
    "phone": "电话（字符串）",
    "email": "邮箱（字符串）",
    "address": "地址（字符串）",
    "intention": "求职意向（字符串）",
    "expected_salary": "期望薪资（字符串）",
    "work_years": "工作年限（字符串，如'3年'）",
    "education": "学历（字符串，如'本科'、'硕士'）",
    "projects": ["项目1", "项目2"],
    "skills": ["技能1", "技能2"]
}

重要提示：
1. 所有字段都必须是字符串或字符串数组
2. 如果某项信息未找到，设为null或空数组
3. education字段只返回学历等级（如本科、硕士），不要返回对象
4. 保留技能名称中的特殊符号，如"C++"、"C#"、"Node.js"等，不要省略或修改
5. 求职意向要完整提取，包括"C++开发实习生"这样的完整职位名称"""

        prompt = f"请从以下简历中提取关键信息，严格按照JSON格式返回：\n\n{resume_text[:3000]}"
        
        try:
            response = await self._call_ai(prompt, system_prompt)
            data = self._extract_json(response)
            
            # 检查是否使用了模拟模式（AI调用失败）
            if self.provider == "mock":
                print("AI调用失败，使用本地提取器提取真实简历信息")
                return LocalExtractor.extract_resume_info(resume_text)
            
            # 使用AI提取的信息，进行数据验证和转换
            return ResumeExtractedInfo(
                basic=ResumeBasicInfo(
                    name=self._safe_get_string(data, "name"),
                    phone=self._safe_get_string(data, "phone"),
                    email=self._safe_get_string(data, "email"),
                    address=self._safe_get_string(data, "address")
                ),
                job=ResumeJobInfo(
                    intention=self._safe_get_string(data, "intention"),
                    expected_salary=self._safe_get_string(data, "expected_salary")
                ),
                background=ResumeBackground(
                    work_years=self._safe_get_string(data, "work_years"),
                    education=self._safe_get_string(data, "education"),
                    projects=self._safe_get_list(data, "projects")
                ),
                skills=self._safe_get_list(data, "skills"),
                raw_text=resume_text[:1000]
            )
        except Exception as e:
            print(f"AI提取失败: {e}，使用本地提取器")
            return LocalExtractor.extract_resume_info(resume_text)
    
    async def extract_job_keywords(self, job_description: str) -> JobKeywords:
        """
        从岗位描述中提取关键词
        
        Args:
            job_description: 岗位描述文本
            
        Returns:
            JobKeywords对象
        """
        # 直接使用本地规则提取关键词，避免AI返回示例数据
        print("使用本地规则提取岗位关键词")
        skills = self._extract_skills_locally(job_description)
        experience = self._extract_experience_locally(job_description)
        education = self._extract_education_locally(job_description)
        
        return JobKeywords(
            skills=skills,
            experience=experience,
            education=education,
            other=[]
        )
    
    def _extract_skills_locally(self, job_description: str) -> list:
        """本地规则提取技能关键词"""
        # 常见技能关键词映射
        skill_keywords = {
            'c++': ['C++', 'CPP', 'C Plus Plus'],
            'python': ['Python'],
            'java': ['Java'],
            'javascript': ['JavaScript', 'JS'],
            'react': ['React', 'React.js'],
            'vue': ['Vue', 'Vue.js'],
            'angular': ['Angular'],
            'typescript': ['TypeScript'],
            'node': ['Node.js', 'Nodejs'],
            'sql': ['SQL', 'MySQL', 'PostgreSQL'],
            'linux': ['Linux'],
            'git': ['Git'],
            'docker': ['Docker'],
            'aws': ['AWS', 'Amazon Web Services'],
            'azure': ['Azure'],
        }
        
        job_lower = job_description.lower()
        found_skills = []
        
        for keyword, skills in skill_keywords.items():
            if keyword in job_lower:
                found_skills.extend(skills)
        
        # 如果没有找到任何技能，返回原始描述中的大写单词（可能是技术名词）
        if not found_skills:
            import re
            # 提取可能的技术名词（大写字母组合或C++这种特殊格式）
            tech_patterns = re.findall(r'\b[A-Z][a-zA-Z]*\+{0,2}\b|\bC\+\+\b|\bC#\b', job_description)
            found_skills = list(set(tech_patterns)) if tech_patterns else [job_description.strip()]
        
        return found_skills
    
    def _extract_experience_locally(self, job_description: str) -> list:
        """本地规则提取经验要求"""
        import re
        experience_patterns = [
            r'(\d+)\s*年\s*以上',
            r'(\d+)\s*年\s*经验',
            r'(\d+)\+?\s*年',
        ]
        
        found_experience = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_description)
            for match in matches:
                found_experience.append(f"{match}年以上经验")
        
        # 检查是否有"大型项目经验"等描述
        if '大型项目' in job_description or '项目经验' in job_description:
            found_experience.append("有大型项目经验")
        
        if '团队' in job_description or '协作' in job_description:
            found_experience.append("团队协作能力")
        
        return found_experience if found_experience else []
    
    def _extract_education_locally(self, job_description: str) -> list:
        """本地规则提取学历要求"""
        education_keywords = {
            '本科': ['本科及以上', '本科'],
            '硕士': ['硕士及以上', '硕士', '研究生'],
            '博士': ['博士', '博士研究生'],
            '大专': ['大专及以上', '大专'],
            '计算机': ['计算机相关专业', '计算机'],
            '软件工程': ['软件工程'],
        }
        
        found_education = []
        for keyword, variants in education_keywords.items():
            if keyword in job_description:
                found_education.extend(variants)
        
        return found_education if found_education else []
    
    async def generate_job_descriptions(self, resume_info: ResumeExtractedInfo) -> list:
        """
        根据简历内容生成推荐的多个岗位描述（至少10个）
        
        Args:
            resume_info: 简历信息
            
        Returns:
            推荐的岗位描述列表
        """
        skills = resume_info.skills or []
        work_years = resume_info.background.work_years
        education = resume_info.background.education
        intention = resume_info.job.intention or ""
        
        # 基础技能列表
        skill_str = ", ".join(skills[:5]) if skills else "相关技术"
        exp_str = f"{work_years}工作经验" if work_years else "相关工作经验"
        edu_str = f"{education}及以上学历" if education else "本科及以上学历"
        
        # 根据简历技能判断主要方向
        has_cpp = any('c++' in s.lower() for s in skills)
        has_python = any('python' in s.lower() for s in skills)
        has_java = any('java' in s.lower() for s in skills)
        has_frontend = any('前端' in s or 'javascript' in s.lower() or 'react' in s.lower() or 'vue' in s.lower() for s in skills)
        has_go = any('go' in s.lower() or 'golang' in s.lower() for s in skills)
        has_rust = any('rust' in s.lower() for s in skills)
        
        jobs = []
        
        # 根据技能生成相关岗位（确保至少10个）
        if has_cpp or 'c++' in intention.lower():
            jobs.extend([
                f"C++开发工程师，熟悉C++11/14/17标准，{skill_str}，{exp_str}，{edu_str}",
                f"C++后端开发工程师，精通STL、多线程编程，{skill_str}，{exp_str}，{edu_str}",
                f"嵌入式C++工程师，熟悉嵌入式开发，{skill_str}，{exp_str}，{edu_str}",
                f"游戏客户端开发工程师（C++），熟悉游戏引擎，{skill_str}，{exp_str}，{edu_str}",
                f"高性能计算工程师（C++），熟悉算法优化，{skill_str}，{exp_str}，{edu_str}",
                f"C++系统开发工程师，熟悉Linux系统编程，{skill_str}，{exp_str}，{edu_str}",
                f"量化交易系统开发（C++），熟悉金融系统，{skill_str}，{exp_str}，{edu_str}",
                f"音视频开发工程师（C++），熟悉编解码技术，{skill_str}，{exp_str}，{edu_str}",
                f"C++架构师，负责系统架构设计，{skill_str}，{exp_str}，{edu_str}",
                f"区块链开发工程师（C++），熟悉区块链技术，{skill_str}，{exp_str}，{edu_str}",
            ])
        
        if has_python or 'python' in intention.lower():
            jobs.extend([
                f"Python开发工程师，熟悉Django/Flask，{skill_str}，{exp_str}，{edu_str}",
                f"Python后端工程师，精通Web开发，{skill_str}，{exp_str}，{edu_str}",
                f"Python数据工程师，熟悉数据处理，{skill_str}，{exp_str}，{edu_str}",
                f"Python算法工程师，熟悉机器学习，{skill_str}，{exp_str}，{edu_str}",
                f"Python自动化测试工程师，熟悉测试框架，{skill_str}，{exp_str}，{edu_str}",
            ])
        
        if has_java or 'java' in intention.lower():
            jobs.extend([
                f"Java开发工程师，熟悉Spring Boot，{skill_str}，{exp_str}，{edu_str}",
                f"Java后端工程师，精通微服务架构，{skill_str}，{exp_str}，{edu_str}",
                f"Java架构师，负责系统设计，{skill_str}，{exp_str}，{edu_str}",
            ])
        
        if has_frontend:
            jobs.extend([
                f"前端开发工程师，熟悉React/Vue，{skill_str}，{exp_str}，{edu_str}",
                f"高级前端工程师，精通前端架构，{skill_str}，{exp_str}，{edu_str}",
                f"全栈工程师（前端方向），熟悉前后端技术，{skill_str}，{exp_str}，{edu_str}",
            ])
        
        if has_go:
            jobs.extend([
                f"Go开发工程师，熟悉Golang，{skill_str}，{exp_str}，{edu_str}",
                f"Go后端工程师，精通微服务，{skill_str}，{exp_str}，{edu_str}",
            ])
        
        if has_rust:
            jobs.extend([
                f"Rust开发工程师，熟悉系统编程，{skill_str}，{exp_str}，{edu_str}",
                f"区块链Rust工程师，熟悉智能合约，{skill_str}，{exp_str}，{edu_str}",
            ])
        
        # 如果没有匹配到特定技能，添加通用岗位
        if not jobs:
            jobs = [
                f"软件开发工程师，{skill_str}，{exp_str}，{edu_str}",
                f"后端开发工程师，熟悉服务端开发，{skill_str}，{exp_str}，{edu_str}",
                f"全栈开发工程师，熟悉前后端技术，{skill_str}，{exp_str}，{edu_str}",
                f"系统开发工程师，熟悉系统设计，{skill_str}，{exp_str}，{edu_str}",
                f"应用开发工程师，熟悉应用开发，{skill_str}，{exp_str}，{edu_str}",
                f"软件工程师（初级），{skill_str}，{exp_str}，{edu_str}",
                f"软件工程师（中级），{skill_str}，{exp_str}，{edu_str}",
                f"软件工程师（高级），{skill_str}，{exp_str}，{edu_str}",
                f"技术专家，精通相关技术，{skill_str}，{exp_str}，{edu_str}",
                f"研发工程师，{skill_str}，{exp_str}，{edu_str}",
            ]
        
        # 确保至少返回10个岗位
        while len(jobs) < 10:
            jobs.append(f"软件开发工程师（方向{len(jobs)+1}），{skill_str}，{exp_str}，{edu_str}")
        
        return jobs[:15]  # 最多返回15个岗位
    
    async def calculate_matching_score(
        self, 
        resume_info: ResumeExtractedInfo, 
        job_keywords: JobKeywords
    ) -> Tuple[MatchingScore, MatchingAnalysis]:
        """
        计算简历与岗位的匹配度
        
        Args:
            resume_info: 简历信息
            job_keywords: 岗位关键词
            
        Returns:
            (匹配分数, 分析结果)
        """
        system_prompt = """你是一个专业的HR评估助手。请根据简历信息和岗位要求，评估匹配度并以JSON格式返回：
{
    "overall_score": 85,
    "skill_match_rate": 90,
    "experience_relevance": 80,
    "education_match": 85,
    "matched_skills": ["匹配技能1", "匹配技能2"],
    "missing_skills": ["缺失技能1", "缺失技能2"],
    "key_requirements": ["关键要求1", "关键要求2"],
    "suggestions": ["建议1", "建议2"]
}"""

        prompt = f"""请评估以下简历与岗位的匹配度：

简历信息：
- 技能：{', '.join(resume_info.skills or [])}
- 工作年限：{resume_info.background.work_years or '未提供'}
- 学历：{resume_info.background.education or '未提供'}
- 求职意向：{resume_info.job.intention or '未提供'}

岗位要求：
- 技能要求：{', '.join(job_keywords.skills)}
- 经验要求：{', '.join(job_keywords.experience)}
- 学历要求：{', '.join(job_keywords.education)}
"""
        
        response = await self._call_ai(prompt, system_prompt)
        data = self._extract_json(response)
        
        score = MatchingScore(
            overall_score=data.get("overall_score", 0),
            skill_match_rate=data.get("skill_match_rate", 0),
            experience_relevance=data.get("experience_relevance", 0),
            education_match=data.get("education_match", 0)
        )
        
        analysis = MatchingAnalysis(
            matched_skills=self._safe_get_list(data, "matched_skills"),
            missing_skills=self._safe_get_list(data, "missing_skills"),
            key_requirements=self._safe_get_list(data, "key_requirements"),
            suggestions=self._safe_get_list(data, "suggestions")
        )
        
        return score, analysis


# 创建全局实例
ai_extractor = AIExtractor()
