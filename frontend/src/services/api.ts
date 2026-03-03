// 1. 所有导入必须放在文件最顶部（修复 import/first 错误）
import axios, { AxiosInstance } from 'axios';

// 2. 定义所有类型接口
export interface ApiResponse<T> {
  code?: number;
  success?: boolean;
  message: string;
  data: T;
  file_hash?: string;
  cached?: boolean;
  mock_mode?: boolean;
}

export interface ResumeData {
  file_hash: string;
  basic: {
    name?: string;
    phone?: string;
    email?: string;
    address?: string;
  };
  job: {
    intention?: string;
    expected_salary?: string;
  };
  background: {
    work_years?: string;
    education?: string;
    projects?: string[];
  };
  skills?: string[];
  raw_text?: string;
  cached: boolean;
  mock_mode?: boolean;
}

export interface MatchingResult {
  scores: {
    overall_score: number;
    skill_match_rate: number;
    experience_relevance: number;
    education_match: number;
  };
  analysis: {
    matched_skills: string[];
    missing_skills: string[];
    key_requirements: string[];
    suggestions: string[];
  };
  cached: boolean;
}

// 3. 创建带类型的 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 60000, // 增加到60秒
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API 请求错误:', error);
    return Promise.reject(error);
  }
);

// 4. 修复泛型使用方式（核心修复 TS2347 错误）
export const resumeApi = {
  // 上传简历 - 移除直接泛型，改用类型断言
  uploadResume: async (file: File): Promise<ApiResponse<ResumeData>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    // 修复：不使用 post<T> 泛型，而是对响应结果进行类型断言
    const response = await api.post('/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 上传文件需要更长的超时时间
    });
    // 使用类型断言替代泛型参数
    return (response.data) as ApiResponse<ResumeData>;
  },
  
  // 获取简历信息
  getResumeInfo: async (fileHash: string): Promise<ApiResponse<ResumeData>> => {
    // 修复：移除 get<T> 泛型
    const response = await api.get(`/resume/info/${fileHash}`);
    return (response.data) as ApiResponse<ResumeData>;
  },
};

// 匹配相关 API
export const matchingApi = {
  // 获取匹配分数
  getMatchingScore: async (
    resumeFileHash: string,
    jobDescription: string
  ): Promise<ApiResponse<MatchingResult>> => {
    // 修复：移除 post<T> 泛型
    const response = await api.post('/matching/score', {
      resume_file_hash: resumeFileHash,
      job_description: jobDescription,
    });
    return (response.data) as ApiResponse<MatchingResult>;
  },
  
  // 推荐岗位描述（返回多个岗位）
  recommendJobDescription: async (
    resumeFileHash: string
  ): Promise<ApiResponse<{ job_descriptions: string[]; based_on: any }>> => {
    const response = await api.post('/matching/recommend-job', null, {
      params: { resume_file_hash: resumeFileHash }
    });
    return (response.data) as ApiResponse<{ job_descriptions: string[]; based_on: any }>;
  },
};
