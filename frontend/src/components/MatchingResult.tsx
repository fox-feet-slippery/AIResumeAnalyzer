import React from 'react';
import { 
  Card, Typography, Row, Col, Progress, Tag, 
  Button, Space, Badge, Divider, List
} from 'antd';
import { 
  CheckCircleOutlined, CloseCircleOutlined,
  ReloadOutlined, TrophyOutlined, StarOutlined,
  ToolOutlined, FileTextOutlined, BulbOutlined
} from '@ant-design/icons';
import { MatchingResult as MatchingResultType } from '../types';

const { Title, Text } = Typography;

interface MatchingResultProps {
  result: MatchingResultType;
  onReset: () => void;
}

const MatchingResult: React.FC<MatchingResultProps> = ({ result, onReset }) => {
  const { scores, analysis, cached } = result;

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const getScoreText = (score: number) => {
    if (score >= 80) return '优秀';
    if (score >= 60) return '良好';
    return '待提升';
  };

  return (
    <Card className="animate-fade-in">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={3}>
            <TrophyOutlined /> 匹配分析结果
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
          </Title>
        </div>

        {/* 综合评分 */}
        <Card 
          style={{ 
            textAlign: 'center',
            background: `linear-gradient(135deg, ${getScoreColor(scores.overall_score)}20 0%, ${getScoreColor(scores.overall_score)}05 100%)`,
            border: `2px solid ${getScoreColor(scores.overall_score)}`
          }}
        >
          <Row justify="center" align="middle">
            <Col>
              <div style={{ position: 'relative', display: 'inline-block' }}>
                <Progress
                  type="circle"
                  percent={Math.round(scores.overall_score)}
                  strokeColor={getScoreColor(scores.overall_score)}
                  strokeWidth={10}
                  width={180}
                  format={(percent) => (
                    <div>
                      <div style={{ fontSize: '48px', fontWeight: 'bold', color: getScoreColor(scores.overall_score) }}>
                        {percent}
                      </div>
                      <div style={{ fontSize: '16px', color: '#666' }}>
                        综合匹配度
                      </div>
                    </div>
                  )}
                />
                <div style={{ marginTop: '12px' }}>
                  <Tag 
                    color={getScoreColor(scores.overall_score)}
                    style={{ fontSize: '16px', padding: '4px 16px' }}
                  >
                    {getScoreText(scores.overall_score)}
                  </Tag>
                </div>
              </div>
            </Col>
          </Row>
        </Card>

        {/* 详细评分 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Card type="inner" title={<><ToolOutlined /> 技能匹配率</>}>
              <Progress 
                percent={Math.round(scores.skill_match_rate)} 
                strokeColor={getScoreColor(scores.skill_match_rate)}
                status={scores.skill_match_rate >= 60 ? 'success' : 'exception'}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card type="inner" title={<><FileTextOutlined /> 经验相关性</>}>
              <Progress 
                percent={Math.round(scores.experience_relevance)} 
                strokeColor={getScoreColor(scores.experience_relevance)}
                status={scores.experience_relevance >= 60 ? 'success' : 'exception'}
              />
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card type="inner" title={<><StarOutlined /> 学历匹配度</>}>
              <Progress 
                percent={Math.round(scores.education_match)} 
                strokeColor={getScoreColor(scores.education_match)}
                status={scores.education_match >= 60 ? 'success' : 'exception'}
              />
            </Card>
          </Col>
        </Row>

        {/* 技能分析 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} md={12}>
            <Card 
              type="inner" 
              title={<><CheckCircleOutlined style={{ color: '#52c41a' }} /> 匹配的技能</>}
            >
              {analysis.matched_skills.length > 0 ? (
                <Space wrap>
                  {analysis.matched_skills.map((skill, index) => (
                    <Tag key={index} color="success" style={{ fontSize: '14px' }}>
                      ✓ {skill}
                    </Tag>
                  ))}
                </Space>
              ) : (
                <Text type="secondary">暂无匹配技能</Text>
              )}
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card 
              type="inner" 
              title={<><CloseCircleOutlined style={{ color: '#ff4d4f' }} /> 缺失的技能</>}
            >
              {analysis.missing_skills.length > 0 ? (
                <Space wrap>
                  {analysis.missing_skills.map((skill, index) => (
                    <Tag key={index} color="error" style={{ fontSize: '14px' }}>
                      ✗ {skill}
                    </Tag>
                  ))}
                </Space>
              ) : (
                <Text type="secondary">技能匹配度很高！</Text>
              )}
            </Card>
          </Col>
        </Row>

        {/* 关键需求 */}
        {analysis.key_requirements.length > 0 && (
          <Card type="inner" title={<><FileTextOutlined /> 岗位关键需求</>}>
            <List
              size="small"
              dataSource={analysis.key_requirements}
              renderItem={(req, index) => (
                <List.Item>
                  <Text>{index + 1}. {req}</Text>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* 改进建议 */}
        {analysis.suggestions.length > 0 && (
          <Card 
            type="inner" 
            title={<><BulbOutlined style={{ color: '#faad14' }} /> AI改进建议</>}
            style={{ background: '#fffbe6', border: '1px solid #ffe58f' }}
          >
            <List
              size="small"
              dataSource={analysis.suggestions}
              renderItem={(suggestion, index) => (
                <List.Item>
                  <Space>
                    <StarOutlined style={{ color: '#faad14' }} />
                    <Text>{suggestion}</Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        )}

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Button 
            type="primary" 
            size="large"
            icon={<ReloadOutlined />}
            onClick={onReset}
          >
            分析新简历
          </Button>
        </div>
      </Space>
    </Card>
  );
};

export default MatchingResult;
