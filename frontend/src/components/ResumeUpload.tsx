import React, { useState } from 'react';
import { Upload, Card, Typography, Space, message, Progress } from 'antd';
import { FilePdfOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { resumeApi } from '../services/api';
import { ResumeData } from '../types';

const { Dragger } = Upload;
const { Title, Text } = Typography;

interface ResumeUploadProps {
  onUploadSuccess: (data: ResumeData) => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const customRequest = async ({ file }: any) => {
    const pdfFile = file as File;
    
    // 验证文件类型
    if (!pdfFile.name.toLowerCase().endsWith('.pdf')) {
      message.error('请上传PDF格式的文件！');
      return;
    }

    // 验证文件大小（10MB）
    if (pdfFile.size > 10 * 1024 * 1024) {
      message.error('文件大小不能超过10MB！');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    // 模拟进度
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const result = await resumeApi.uploadResume(pdfFile);
      clearInterval(progressInterval);
      setUploadProgress(100);

      if ((result.code === 200 || result.success === true) && result.data) {
        const resumeData: ResumeData = {
          ...result.data,
          file_hash: result.file_hash || '',
          cached: result.cached || false,
          mock_mode: result.mock_mode || false,
        };
        
        // 如果是模拟模式，显示警告
        if (result.mock_mode) {
          message.warning('当前使用模拟模式，显示的是示例数据而非真实简历内容');
        } else {
          message.success('简历解析成功！');
        }
        
        onUploadSuccess(resumeData);
      } else {
        message.error(result.message || '解析失败');
      }
    } catch (error: any) {
      clearInterval(progressInterval);
      message.error(error.response?.data?.detail || '上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card className="animate-fade-in">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={3}>📄 上传简历</Title>
          <Text type="secondary">
            支持 PDF 格式，文件大小不超过 10MB
          </Text>
        </div>

        <Dragger
          customRequest={customRequest}
          accept=".pdf"
          showUploadList={false}
          disabled={uploading}
          style={{ 
            padding: '40px',
            background: '#fafafa',
            border: '2px dashed #d9d9d9',
            borderRadius: '12px'
          }}
        >
          <Space direction="vertical" size="large">
            <FilePdfOutlined style={{ fontSize: '64px', color: '#ff4d4f' }} />
            <div>
              <Title level={4} style={{ margin: '0 0 8px 0' }}>
                点击或拖拽文件到此处上传
              </Title>
              <Text type="secondary">
                系统将自动解析简历内容并提取关键信息
              </Text>
            </div>
          </Space>
        </Dragger>

        {uploading && (
          <div style={{ padding: '0 20px' }}>
            <Text>正在解析简历...</Text>
            <Progress 
              percent={uploadProgress} 
              status="active"
              strokeColor={{ from: '#108ee9', to: '#87d068' }}
            />
          </div>
        )}

        <div style={{ 
          background: '#f6ffed', 
          border: '1px solid #b7eb8f',
          borderRadius: '8px',
          padding: '16px'
        }}>
          <Space>
            <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '20px' }} />
            <Text>
              <strong>AI 将自动提取：</strong>
              姓名、电话、邮箱、地址、求职意向、期望薪资、工作年限、学历背景、项目经历、技能等
            </Text>
          </Space>
        </div>
      </Space>
    </Card>
  );
};

export default ResumeUpload;
