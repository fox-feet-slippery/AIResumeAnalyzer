export interface ResumeBasicInfo {
  name?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface ResumeJobInfo {
  intention?: string;
  expected_salary?: string;
}

export interface ResumeBackground {
  work_years?: string;
  education?: string;
  projects?: string[];
}

export interface ResumeData {
  basic: ResumeBasicInfo;
  job: ResumeJobInfo;
  background: ResumeBackground;
  skills?: string[];
  raw_text?: string;
  file_hash: string;
  cached: boolean;
  mock_mode?: boolean;
}

export interface MatchingScore {
  overall_score: number;
  skill_match_rate: number;
  experience_relevance: number;
  education_match: number;
}

export interface MatchingAnalysis {
  matched_skills: string[];
  missing_skills: string[];
  key_requirements: string[];
  suggestions: string[];
}

export interface MatchingResult {
  scores: MatchingScore;
  analysis: MatchingAnalysis;
  cached: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
  file_hash?: string;
  cached?: boolean;
}
