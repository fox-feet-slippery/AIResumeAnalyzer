import React, { useState, useEffect } from 'react';
// antd v5 导入方式
import Card from 'antd/es/card';
import Typography from 'antd/es/typography';
import Input from 'antd/es/input';
import Button from 'antd/es/button';
import Space from 'antd/es/space';
import Form from 'antd/es/form';
import Spin from 'antd/es/spin';
import Alert from 'antd/es/alert';
import Tag from 'antd/es/tag';
import Descriptions from 'antd/es/descriptions';
import message from 'antd/es/message';
import { 
  FileTextOutlined, ArrowLeftOutlined, SearchOutlined, 
  LoadingOutlined 
} from '@ant-design/icons';
import { matchingApi } from '../services/api';
import type { ApiResponse } from '../services/api';
import type { ResumeData } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { useForm } = Form;

interface JobMatchingProps {
  fileHash: string;
  resumeData: ResumeData;
  onMatchingSuccess: (result: any) => void;
  onBack: () => void;
}

// 定义关键词响应类型
interface KeywordResult {
  skills: string[];
  experience: string[];
  education: string[];
}

const JobMatching: React.FC<JobMatchingProps> = ({ fileHash, resumeData, onMatchingSuccess, onBack }) => {
  const [form] = useForm();
  const [loading, setLoading] = useState(false);
  const [keywords, setKeywords] = useState<KeywordResult | null>(null);
  const [recommendedJobs, setRecommendedJobs] = useState<string[]>([]);
  
  // 点击推荐岗位时，填充到输入框
  const handleSelectJob = (job: string) => {
    form.setFieldsValue({ jobDescription: job });
    message.success('已选择岗位');
  };
  
  // 提取关键词和推荐岗位（点击按钮后执行）
  const handleExtractKeywords = async () => {
    setLoading(true);
    try {
      // 1. 调用AI推荐多个岗位描述
      const result = await matchingApi.recommendJobDescription(fileHash);
      
      if (result.success && result.data && result.data.job_descriptions) {
        setRecommendedJobs(result.data.job_descriptions);
      } else {
        // 如果AI推荐失败，使用简历中的求职意向
        const jobIntention = resumeData?.job?.intention || '软件开发工程师';
        setRecommendedJobs([jobIntention]);
      }
      
      // 2. 从简历技能中提取关键词
      const resumeSkills = resumeData?.skills || [];
      const extractedSkills = resumeSkills.length > 0 
        ? resumeSkills.slice(0, 5) 
        : ['相关技术'];
      
      const keywordResult: KeywordResult = {
        skills: extractedSkills,
        experience: resumeData?.background?.work_years ? [`${resumeData.background.work_years}工作经验`] : [],
        education: resumeData?.background?.education ? [resumeData.background.education] : []
      };
      
      setKeywords(keywordResult);
      message.success(`成功推荐${result.data?.job_descriptions?.length || 1}个岗位，点击选择`);
    } catch (error) {
      message.error('提取失败，请重试');
      console.error('提取错误:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 提交匹配分析（使用输入框中的岗位描述）
  const handleSubmit = async () => {
    const values = form.getFieldsValue();
    const jobDescription = values.jobDescription?.trim();
    
    if (!jobDescription) {
      message.warning('请先输入岗位描述或点击推荐岗位选择');
      return;
    }
    
    if (!fileHash) {
      message.error('简历文件哈希值缺失，请重新上传简历');
      return;
    }
    
    setLoading(true);
    try {
      const result: ApiResponse<any> = await matchingApi.getMatchingScore(
        fileHash,
        jobDescription
      );
      
      if (result.success && result.data) {
        onMatchingSuccess(result.data);
        message.success('岗位匹配分析成功');
      } else {
        message.error(result.message || '匹配分析失败');
      }
    } catch (error) {
      message.error('匹配分析失败，请重试');
      console.error('匹配分析错误:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <Title level={3}>
          <SearchOutlined /> 岗位匹配分析
        </Title>
        <Text type="secondary">
          输入岗位需求描述，AI 将智能分析简历与岗位的匹配度
        </Text>
      </div>
      
      <Form
        form={form}
        onFinish={handleSubmit}
        layout="vertical"
        initialValues={{ jobDescription: '' }}
      >
        <Form.Item
          name="jobDescription"
          label={<Text strong>岗位需求描述（可选）</Text>}
        >
          <TextArea 
            rows={4} 
            placeholder="可以输入您感兴趣的岗位描述，或留空让AI根据简历推荐"
            maxLength={2000}
            showCount
          />
        </Form.Item>
        
        {/* 推荐岗位展示 */}
        {recommendedJobs.length > 0 && (
          <Alert
            message={`AI根据简历推荐的${recommendedJobs.length}个岗位（点击选择填充到输入框）`}
            description={
              <div style={{ marginTop: '8px' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {recommendedJobs.map((job, index) => (
                    <Tag
                      key={index}
                      color="blue"
                      style={{ 
                        cursor: 'pointer', 
                        padding: '8px 12px', 
                        fontSize: '14px',
                        whiteSpace: 'normal',
                        height: 'auto',
                        lineHeight: '1.5'
                      }}
                      onClick={() => handleSelectJob(job)}
                    >
                      {index + 1}. {job}
                    </Tag>
                  ))}
                </Space>
              </div>
            }
            type="success"
            showIcon
            style={{ marginBottom: '16px' }}
          />
        )}
        
        {/* 关键词展示 */}
        {keywords && (
          <Alert
            message="提取的关键词"
            description={
              <div style={{ marginTop: '8px' }}>
                <div style={{ marginBottom: '8px' }}>
                  <Text strong>技能要求：</Text>
                  <Space wrap>
                    {keywords.skills.map((skill, i) => (
                      <Tag key={i} color="blue">{skill}</Tag>
                    ))}
                  </Space>
                </div>
                <div style={{ marginBottom: '8px' }}>
                  <Text strong>经验要求：</Text>
                  <Space wrap>
                    {keywords.experience.map((exp, i) => (
                      <Tag key={i} color="green">{exp}</Tag>
                    ))}
                  </Space>
                </div>
                <div>
                  <Text strong>学历要求：</Text>
                  <Space wrap>
                    {keywords.education.map((edu, i) => (
                      <Tag key={i} color="purple">{edu}</Tag>
                    ))}
                  </Space>
                </div>
              </div>
            }
            type="info"
            showIcon
            style={{ marginBottom: '16px' }}
            closable
            onClose={() => { setKeywords(null); setRecommendedJobs([]); }}
          />
        )}
        
        <Form.Item>
          <Space size="middle">
            <Button 
              icon={<ArrowLeftOutlined />}
              onClick={onBack}
              disabled={loading}
            >
              返回
            </Button>
            <Button
              type="default"
              onClick={() => handleExtractKeywords()}
              disabled={loading}
            >
              提取关键词
            </Button>
            <Button
              type="primary"
              htmlType="submit"
              icon={loading ? <LoadingOutlined /> : <SearchOutlined />}
              loading={loading}
              size="large"
            >
              开始匹配分析
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default JobMatching;