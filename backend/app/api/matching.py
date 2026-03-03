from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    MatchingRequest, 
    JobKeywords
)
from app.services.ai_extractor import ai_extractor
from app.core.cache import cache_manager

router = APIRouter()


@router.post("/score")
async def calculate_matching(request: MatchingRequest):
    """
    计算简历与岗位的匹配度评分
    
    - **resume_file_hash**: 简历文件哈希值
    - **job_description**: 岗位需求描述
    """
    try:
        # 获取简历信息
        cached_resume = await cache_manager.get_resume_cache(request.resume_file_hash)
        if not cached_resume:
            raise HTTPException(
                status_code=404,
                detail="未找到该简历，请先上传简历"
            )
        
        from app.models.schemas import ResumeExtractedInfo
        resume_info = ResumeExtractedInfo(**cached_resume['data'])
        
        # 检查匹配缓存
        cached_matching = await cache_manager.get_matching_cache(
            request.resume_file_hash,
            request.job_description
        )
        
        if cached_matching:
            return {
                "success": True,
                "message": "从缓存获取匹配结果",
                "data": {
                    "scores": cached_matching['scores'],
                    "analysis": cached_matching['analysis'],
                    "cached": True
                }
            }
        
        # 提取岗位关键词
        job_keywords = await ai_extractor.extract_job_keywords(request.job_description)
        
        # 计算匹配度
        scores, analysis = await ai_extractor.calculate_matching_score(
            resume_info,
            job_keywords
        )
        
        # 缓存结果
        await cache_manager.set_matching_cache(
            request.resume_file_hash,
            request.job_description,
            {
                'scores': scores.model_dump(),
                'analysis': analysis.model_dump()
            }
        )
        
        return {
            "success": True,
            "message": "匹配度计算成功",
            "data": {
                "scores": scores.model_dump(),
                "analysis": analysis.model_dump(),
                "cached": False
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"匹配度计算失败: {str(e)}",
            "data": None
        }


@router.post("/keywords", response_model=dict)
async def extract_job_keywords(job_description: str):
    """
    从岗位描述中提取关键词
    
    - **job_description**: 岗位需求描述
    """
    try:
        keywords = await ai_extractor.extract_job_keywords(job_description)
        return {
            "success": True,
            "message": "关键词提取成功",
            "data": keywords.model_dump()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"关键词提取失败: {str(e)}",
            "data": None
        }


@router.post("/recommend-job")
async def recommend_job_description(resume_file_hash: str):
    """
    根据简历内容推荐多个岗位描述（至少10个）
    
    - **resume_file_hash**: 简历文件哈希值
    """
    try:
        # 获取简历信息
        cached_resume = await cache_manager.get_resume_cache(resume_file_hash)
        if not cached_resume:
            raise HTTPException(
                status_code=404,
                detail="未找到该简历，请先上传简历"
            )
        
        from app.models.schemas import ResumeExtractedInfo
        resume_info = ResumeExtractedInfo(**cached_resume['data'])
        
        # 使用AI生成推荐的多个岗位描述
        job_descriptions = await ai_extractor.generate_job_descriptions(resume_info)
        
        return {
            "success": True,
            "message": f"成功推荐{len(job_descriptions)}个岗位",
            "data": {
                "job_descriptions": job_descriptions,
                "based_on": {
                    "skills": resume_info.skills,
                    "intention": resume_info.job.intention,
                    "work_years": resume_info.background.work_years
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "message": f"岗位描述推荐失败: {str(e)}",
            "data": None
        }
