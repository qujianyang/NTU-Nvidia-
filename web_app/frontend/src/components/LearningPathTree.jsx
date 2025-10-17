import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  Position,
} from 'reactflow';
import { Card, Tag, Typography, Space } from 'antd';
import { ClockCircleOutlined, BookOutlined, TrophyOutlined } from '@ant-design/icons';
import 'reactflow/dist/style.css';

const { Title, Text } = Typography;

// Custom node component
const CourseNode = ({ data }) => {
  const getLevelColor = (level) => {
    if (!level) return '#e0e0e0';
    const levelLower = level.toLowerCase();
    if (levelLower.includes('beginner')) return '#52c41a';
    if (levelLower.includes('intermediate')) return '#faad14';
    if (levelLower.includes('advanced')) return '#f5222d';
    return '#1890ff';
  };

  const borderColor = getLevelColor(data.level);

  return (
    <Card
      size="small"
      hoverable
      style={{
        width: 280,
        border: `2px solid ${borderColor}`,
        borderRadius: 8,
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      }}
      bodyStyle={{ padding: 12 }}
      onClick={() => window.openChatWithCourse?.(data)}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Title level={5} style={{ margin: 0, fontSize: 14 }}>
          {data.title}
        </Title>

        <Space wrap>
          <Tag color={getLevelColor(data.level)} style={{ margin: 0 }}>
            <BookOutlined /> {data.level || 'General'}
          </Tag>
          <Tag style={{ margin: 0 }}>
            <ClockCircleOutlined /> {data.duration || 'N/A'}
          </Tag>
        </Space>

        {data.price === 'Free' && (
          <Tag color="green" icon={<TrophyOutlined />}>
            Free Course
          </Tag>
        )}
      </Space>
    </Card>
  );
};

const nodeTypes = {
  courseNode: CourseNode,
};

const LearningPathTree = ({ courses }) => {
  // Build nodes and edges from course relationships
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const nodes = [];
    const edges = [];
    const levelMap = new Map();
    const courseMap = new Map();

    // Create course map for quick lookup
    courses.forEach(course => {
      courseMap.set(course.id, course);
    });

    // Determine levels based on prerequisites
    const getLevelForCourse = (courseId, visited = new Set()) => {
      if (visited.has(courseId)) return 0;
      visited.add(courseId);

      const course = courseMap.get(courseId);
      if (!course || !course.prerequisites || course.prerequisites.length === 0) {
        return 0;
      }

      const maxPrereqLevel = Math.max(
        ...course.prerequisites.map(prereqId =>
          getLevelForCourse(prereqId, visited) + 1
        )
      );
      return maxPrereqLevel;
    };

    // Calculate levels for all courses
    courses.forEach(course => {
      const level = getLevelForCourse(course.id);
      if (!levelMap.has(level)) {
        levelMap.set(level, []);
      }
      levelMap.get(level).push(course);
    });

    // Create nodes positioned by level
    const xSpacing = 350;
    const ySpacing = 120;

    levelMap.forEach((coursesAtLevel, level) => {
      coursesAtLevel.forEach((course, index) => {
        const yOffset = (index - coursesAtLevel.length / 2) * ySpacing;

        nodes.push({
          id: course.id,
          type: 'courseNode',
          position: {
            x: level * xSpacing,
            y: 300 + yOffset
          },
          data: course,
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
        });
      });
    });

    // Create edges from prerequisites and leads_to relationships
    courses.forEach(course => {
      if (course.prerequisites) {
        course.prerequisites.forEach(prereqId => {
          if (courseMap.has(prereqId)) {
            edges.push({
              id: `${prereqId}-${course.id}`,
              source: prereqId,
              target: course.id,
              type: 'smoothstep',
              animated: true,
              style: { stroke: '#76b900', strokeWidth: 2 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#76b900',
              },
            });
          }
        });
      }
    });

    return { nodes, edges };
  }, [courses]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: '100%', height: 'calc(100vh - 64px)' }}>
      <Card
        title="Interactive Learning Paths"
        extra={
          <Text type="secondary">
            Click and drag to explore • Click a course to learn more
          </Text>
        }
        bodyStyle={{ padding: 0, height: 'calc(100% - 57px)' }}
        style={{ height: '100%' }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <MiniMap
            style={{
              height: 120,
              backgroundColor: '#f0f0f0',
            }}
            nodeColor={(node) => {
              const level = node.data?.level?.toLowerCase() || '';
              if (level.includes('beginner')) return '#52c41a';
              if (level.includes('intermediate')) return '#faad14';
              if (level.includes('advanced')) return '#f5222d';
              return '#1890ff';
            }}
          />
          <Controls />
          <Background variant="dots" gap={12} size={1} color="#e0e0e0" />
        </ReactFlow>
      </Card>
    </div>
  );
};

export default LearningPathTree;