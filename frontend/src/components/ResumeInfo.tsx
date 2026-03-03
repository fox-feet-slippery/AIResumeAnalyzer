import React from 'react';
import { 
  Card, Typography, Row, Col, Tag, Button, Space, 
  Descriptions, Badge, Divider, List 
} from 'antd';
import { 
  UserOutlined, PhoneOutlined, MailOutlined, 
  EnvironmentOutlined, DollarOutlined, AimOutlined,
  ClockCircleOutlined, BookOutlined, ProjectOutlined,
  ToolOutlined, ArrowRightOutlined, ReloadOutlined
} from '@ant-design/icons';
import { ResumeData } from '../types';

const { Title, Text } = Typography;

interface ResumeInfoProps {
  data: ResumeData;
  onProceed: () => void;
  onReset: () => void;
}

const ResumeInfo: React.FC<ResumeInfoProps> = ({ data, onProceed, onReset }) => {
  const { basic, job, background, skills, cached, mock_mode } = data;

  return (
    <Card className="animate-fade-in">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={3}>
            <UserOutlined /> 简历解析结果
            {cached && (
              <Badge 
                count="缓存" 
                style={{ 
                  backgroundColor: '#52c41a',
                  marginLeft: '12px',
                  fontSize: '12px'
                }} 
              />
            )}
            {mock_mode && (
              <Badge 
                count="模拟模式" 
                style={{ 
                  backgroundColor: '#faad14',
                  marginLeft: '12px',
                  fontSize: '12px'
                }} 
              />
            )}
          </Title>
          <Text type="secondary">
            {mock_mode 
              ? '⚠️ 当前使用模拟模式，显示的是示例数据。请检查OpenAI API配置以解析真实简历。'
              : 'AI已成功提取以下关键信息'}
          </Text>
        </div>

        <Row gutter={[24, 24]}>
          <Col xs={24} md={12}>
            <Card 
              title={<><UserOutlined /> 基本信息</>} 
              type="inner"
              bordered
            >
              <Descriptions column={1} size="small">
                <Descriptions.Item label={<><UserOutlined /> 姓名</>}>
                  {basic.name || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
                <Descriptions.Item label={<><PhoneOutlined /> 电话</>}>
                  {basic.phone || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
                <Descriptions.Item label={<><MailOutlined /> 邮箱</>}>
                  {basic.email || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
                <Descriptions.Item label={<><EnvironmentOutlined /> 地址</>}>
                  {basic.address || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>

          <Col xs={24} md={12}>
            <Card 
              title={<><AimOutlined /> 求职意向</>} 
              type="inner"
              bordered
            >
              <Descriptions column={1} size="small">
                <Descriptions.Item label={<><AimOutlined /> 意向岗位</>}>
                  {job.intention || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
                <Descriptions.Item label={<><DollarOutlined /> 期望薪资</>}>
                  {job.expected_salary || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
                <Descriptions.Item label={<><ClockCircleOutlined /> 工作年限</>}>
                  {background.work_years || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
                <Descriptions.Item label={<><BookOutlined /> 学历背景</>}>
                  {background.education || <Text type="secondary">未识别</Text>}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>

          {skills && skills.length > 0 && (
            <Col xs={24}>
              <Card title={<><ToolOutlined /> 专业技能</>} type="inner" bordered>
                <Space wrap>
                  {skills.map((skill, index) => (
                    <Tag 
                      key={index} 
                      color="blue"
                      style={{ fontSize: '14px', padding: '4px 12px' }}
                    >
                      {skill}
                    </Tag>
                  ))}
                </Space>
              </Card>
            </Col>
          )}

          {background.projects && background.projects.length > 0 && (
            <Col xs={24}>
              <Card title={<><ProjectOutlined /> 项目经历</>} type="inner" bordered>
                <List
                  size="small"
                  dataSource={background.projects}
                  renderItem={(project, index) => (
                    <List.Item>
                      <Text>{index + 1}. {project}</Text>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          )}
        </Row>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Space size="large">
            <Button 
              icon={<ReloadOutlined />}
              onClick={onReset}
            >
              重新上传
            </Button>
            <Button 
              type="primary" 
              size="large"
              icon={<ArrowRightOutlined />}
              onClick={onProceed}
            >
              进行岗位匹配
            </Button>
          </Space>
        </div>
      </Space>
    </Card>
  );
};

export default ResumeInfo;
