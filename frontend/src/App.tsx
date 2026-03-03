import React from 'react';
import { useState } from 'react';
import { Layout, Typography, Steps, Card, message } from 'antd';
import ResumeUpload from './components/ResumeUpload';
import ResumeInfo from './components/ResumeInfo';
import JobMatching from './components/JobMatching';
import MatchingResult from './components/MatchingResult';

import { ResumeData, MatchingResult as MatchingResultType } from './types';

const { Header, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [matchingResult, setMatchingResult] = useState<MatchingResultType | null>(null);

  const steps = [
    {
      title: '上传简历',
      description: '上传PDF格式简历',
    },
    {
      title: '简历解析',
      description: 'AI提取关键信息',
    },
    {
      title: '岗位匹配',
      description: '输入岗位需求',
    },
    {
      title: '匹配结果',
      description: '查看匹配评分',
    },
  ];

  const handleUploadSuccess = (data: ResumeData) => {
    console.log('Upload success, data:', data);
    setResumeData(data);
    setCurrentStep(1);
    message.success('简历解析成功！');
  };

  const handleProceedToMatching = () => {
    setCurrentStep(2);
  };

  const handleMatchingSuccess = (result: MatchingResultType) => {
    setMatchingResult(result);
    setCurrentStep(3);
    message.success('匹配分析完成！');
  };

  const handleReset = () => {
    setCurrentStep(0);
    setResumeData(null);
    setMatchingResult(null);
  };

  return (
    <Layout style={{ minHeight: '100vh', padding: '20px' }}>
      <Header style={{ 
        background: 'transparent', 
        textAlign: 'center',
        marginBottom: '20px'
      }}>
        <Title style={{ color: 'white', margin: 0 }}>
          🤖 AI智能简历分析系统
        </Title>
      </Header>
      
      <Content style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Card style={{ marginBottom: '20px' }}>
          <Steps current={currentStep} items={steps} />
        </Card>

        {currentStep === 0 && (
          <ResumeUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {currentStep === 1 && resumeData && (
          <ResumeInfo 
            data={resumeData} 
            onProceed={handleProceedToMatching}
            onReset={handleReset}
          />
        )}

        {currentStep === 1 && !resumeData && (
          <Card style={{ textAlign: 'center', padding: '40px' }}>
            <Title level={4}>数据加载中...</Title>
          </Card>
        )}

        {currentStep === 2 && resumeData && (
          <JobMatching 
            fileHash={resumeData.file_hash}
            resumeData={resumeData}
            onMatchingSuccess={handleMatchingSuccess}
            onBack={() => setCurrentStep(1)}
          />
        )}

        {currentStep === 3 && matchingResult && (
          <MatchingResult 
            result={matchingResult}
            onReset={handleReset}
          />
        )}
      </Content>
    </Layout>
  );
};

export default App;
