from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import ResumeParseResponse, ResumeExtractedInfo
# 尝试导入PDF解析器，如果失败则使用简化版
try:
    from app.services.pdf_parser import pdf_parser
except ImportError:
    from app.services.pdf_parser_simple import pdf_parser
from app.services.ai_extractor import ai_extractor
from app.core.cache import cache_manager
from app.core.config import settings

router = APIRouter()


@router.post("/upload", response_model=ResumeParseResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    上传并解析PDF简历
    
    - **file**: PDF格式的简历文件
    """
    # 验证文件类型
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if f".{file_ext}" not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型。请上传PDF文件。"
        )
    
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 验证文件大小
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大{settings.MAX_FILE_SIZE / 1024 / 1024}MB）"
            )
        
        # 解析PDF
        file_hash, resume_text = pdf_parser.parse_pdf(file_content)
        
        # 检查缓存
        cached_result = await cache_manager.get_resume_cache(file_hash)
        if cached_result:
            return ResumeParseResponse(
                success=True,
                message="从缓存获取解析结果",
                data=ResumeExtractedInfo(**cached_result['data']),
                file_hash=file_hash,
                cached=True,
                mock_mode=False
            )
        
        # 提取关键信息
        extracted_info = await ai_extractor.extract_resume_info(resume_text)
        
        # 检查是否使用了模拟模式
        is_mock_mode = ai_extractor.provider == "mock"
        
        # 缓存结果
        await cache_manager.set_resume_cache(
            file_hash, 
            {'data': extracted_info.model_dump()}
        )
        
        return ResumeParseResponse(
            success=True,
            message="简历解析成功" if not is_mock_mode else "简历解析成功（模拟模式）",
            data=extracted_info,
            file_hash=file_hash,
            cached=False,
            mock_mode=is_mock_mode
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ResumeParseResponse(
            success=False,
            message=f"简历解析失败: {str(e)}",
            data=None,
            file_hash=None,
            cached=False
        )


@router.get("/info/{file_hash}", response_model=ResumeParseResponse)
async def get_resume_info(file_hash: str):
    """
    根据文件哈希获取已解析的简历信息
    
    - **file_hash**: 简历文件哈希值
    """
    cached_result = await cache_manager.get_resume_cache(file_hash)
    
    if not cached_result:
        raise HTTPException(
            status_code=404,
            detail="未找到该简历的解析结果，请重新上传"
        )
    
    return ResumeParseResponse(
        success=True,
        message="获取成功",
        data=ResumeExtractedInfo(**cached_result['data']),
        file_hash=file_hash,
        cached=True,
        mock_mode=False
    )
