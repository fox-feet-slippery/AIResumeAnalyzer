from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ResumeBasicInfo(BaseModel):
    name: Optional[str] = Field(None, description="姓名")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")


class ResumeJobInfo(BaseModel):
    intention: Optional[str] = Field(None, description="求职意向")
    expected_salary: Optional[str] = Field(None, description="期望薪资")


class ResumeBackground(BaseModel):
    work_years: Optional[str] = Field(None, description="工作年限")
    education: Optional[str] = Field(None, description="学历背景")
    projects: Optional[List[str]] = Field(None, description="项目经历")


class ResumeExtractedInfo(BaseModel):
    basic: ResumeBasicInfo = Field(default_factory=ResumeBasicInfo, description="基本信息")
    job: ResumeJobInfo = Field(default_factory=ResumeJobInfo, description="求职信息")
    background: ResumeBackground = Field(default_factory=ResumeBackground, description="背景信息")
    skills: Optional[List[str]] = Field(None, description="技能列表")
    raw_text: Optional[str] = Field(None, description="原始文本")


class ResumeParseResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="处理消息")
    data: Optional[ResumeExtractedInfo] = Field(None, description="解析结果")
    file_hash: Optional[str] = Field(None, description="文件哈希")
    cached: bool = Field(False, description="是否来自缓存")
    mock_mode: bool = Field(False, description="是否使用模拟模式")


class MatchingRequest(BaseModel):
    resume_file_hash: str = Field(..., description="简历文件哈希")
    job_description: str = Field(..., description="岗位需求描述")


class MatchingScore(BaseModel):
    overall_score: float = Field(..., description="综合匹配度评分(0-100)", ge=0, le=100)
    skill_match_rate: float = Field(..., description="技能匹配率(0-100)", ge=0, le=100)
    experience_relevance: float = Field(..., description="经验相关性(0-100)", ge=0, le=100)
    education_match: float = Field(..., description="学历匹配度(0-100)", ge=0, le=100)


class MatchingAnalysis(BaseModel):
    matched_skills: List[str] = Field(default_factory=list, description="匹配的技能")
    missing_skills: List[str] = Field(default_factory=list, description="缺失的技能")
    key_requirements: List[str] = Field(default_factory=list, description="关键需求")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")


class MatchingResponse(BaseModel):
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="处理消息")
    scores: Optional[MatchingScore] = Field(None, description="匹配评分")
    analysis: Optional[MatchingAnalysis] = Field(None, description="匹配分析")
    cached: bool = Field(False, description="是否来自缓存")


class JobKeywords(BaseModel):
    skills: List[str] = Field(default_factory=list, description="技能关键词")
    experience: List[str] = Field(default_factory=list, description="经验要求")
    education: List[str] = Field(default_factory=list, description="学历要求")
    other: List[str] = Field(default_factory=list, description="其他要求")


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
