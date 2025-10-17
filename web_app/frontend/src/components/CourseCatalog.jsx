import React, { useState } from 'react';
import { Card, Row, Col, Tag, Badge, Button, Input, Select, Space, Typography, Tooltip } from 'antd';
import { ClockCircleOutlined, TagOutlined, ArrowRightOutlined, LockOutlined, SearchOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;

const CourseCatalog = ({ courses }) => {
  const [filteredCourses, setFilteredCourses] = useState(courses);
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState('all');

  const handleSearch = (value) => {
    setSearchTerm(value);
    filterCourses(value, levelFilter);
  };

  const handleLevelFilter = (value) => {
    setLevelFilter(value);
    filterCourses(searchTerm, value);
  };

  const filterCourses = (search, level) => {
    let filtered = courses;

    if (search) {
      filtered = filtered.filter(course =>
        course.title.toLowerCase().includes(search.toLowerCase()) ||
        course.description?.toLowerCase().includes(search.toLowerCase())
      );
    }

    if (level !== 'all') {
      filtered = filtered.filter(course =>
        course.level?.toLowerCase().includes(level)
      );
    }

    setFilteredCourses(filtered);
  };

  const getLevelColor = (level) => {
    if (!level) return 'default';
    const levelLower = level.toLowerCase();
    if (levelLower.includes('beginner')) return 'green';
    if (levelLower.includes('intermediate')) return 'orange';
    if (levelLower.includes('advanced')) return 'red';
    return 'blue';
  };

  const CourseCard = ({ course, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Badge.Ribbon
        text={course.price || 'Free'}
        color={course.price === 'Free' || !course.price ? 'green' : 'gold'}
      >
        <Card
          hoverable
          className="course-card"
          style={{ height: '100%', borderRadius: 12 }}
          actions={[
            <Button
              type="primary"
              icon={<ArrowRightOutlined />}
              onClick={() => window.openChatWithCourse?.(course)}
            >
              Learn More
            </Button>
          ]}
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Title level={4} style={{ marginBottom: 0 }}>
              {course.title}
            </Title>

            <Space wrap>
              <Tag color={getLevelColor(course.level)}>
                {course.level || 'General'}
              </Tag>
              <Tag icon={<ClockCircleOutlined />}>
                {course.duration || 'N/A'}
              </Tag>
              {course.cost_usd > 0 && (
                <Tag icon={<TagOutlined />} color="gold">
                  ${course.cost_usd}
                </Tag>
              )}
            </Space>

            <Paragraph
              ellipsis={{ rows: 3, expandable: true, symbol: 'more' }}
              style={{ marginBottom: 12 }}
            >
              {course.description || 'No description available'}
            </Paragraph>

            {/* Prerequisites */}
            {course.prerequisites && course.prerequisites.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <Text type="secondary" strong>
                  <LockOutlined /> Prerequisites:
                </Text>
                <Space wrap style={{ marginTop: 4 }}>
                  {course.prerequisites.map(prereq => (
                    <Tag key={prereq} color="purple">
                      {prereq}
                    </Tag>
                  ))}
                </Space>
              </div>
            )}

            {/* Leads To */}
            {course.leads_to && course.leads_to.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <Text type="secondary" strong>
                  <ArrowRightOutlined /> Next Steps:
                </Text>
                <Space wrap style={{ marginTop: 4 }}>
                  {course.leads_to.map(next => (
                    <Tag key={next} color="cyan">
                      {next}
                    </Tag>
                  ))}
                </Space>
              </div>
            )}
          </Space>
        </Card>
      </Badge.Ribbon>
    </motion.div>
  );

  return (
    <div style={{ padding: 24 }}>
      {/* Filters */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large" wrap>
          <Search
            placeholder="Search courses..."
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={handleSearch}
            style={{ width: 300 }}
          />

          <Select
            defaultValue="all"
            style={{ width: 200 }}
            size="large"
            onChange={handleLevelFilter}
            options={[
              { value: 'all', label: '🎯 All Levels' },
              { value: 'beginner', label: '🌱 Beginner' },
              { value: 'intermediate', label: '📈 Intermediate' },
              { value: 'advanced', label: '🚀 Advanced' },
            ]}
          />
        </Space>

        <Text type="secondary" style={{ marginLeft: 16 }}>
          Showing {filteredCourses.length} of {courses.length} courses
        </Text>
      </Card>

      {/* Course Grid */}
      <Row gutter={[24, 24]}>
        {filteredCourses.map((course, index) => (
          <Col key={course.id} xs={24} sm={24} md={12} lg={8} xl={8}>
            <CourseCard course={course} index={index} />
          </Col>
        ))}
      </Row>

      {filteredCourses.length === 0 && (
        <Card style={{ textAlign: 'center', padding: 48 }}>
          <Title level={4}>No courses found</Title>
          <Text type="secondary">Try adjusting your filters</Text>
        </Card>
      )}
    </div>
  );
};

export default CourseCatalog;