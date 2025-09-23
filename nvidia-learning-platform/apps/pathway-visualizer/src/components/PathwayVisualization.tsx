import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Course } from '../types';
import coursesData from '../../../packages/shared/src/data/courses.json';

interface Props {
  role: 'developer' | 'administrator' | null;
  selectedSkills: string[];
  onCourseSelect: (courseId: string) => void;
  userProgress: Map<string, number>;
}

export const PathwayVisualization: React.FC<Props> = ({
  role,
  selectedSkills,
  onCourseSelect,
  userProgress
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  useEffect(() => {
    if (!svgRef.current || !role) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Filter courses based on role
    const filteredCourses = coursesData.courses.filter(course =>
      course.role === role || course.role === 'both'
    );

    // Create nodes and links
    const nodes = filteredCourses.map(course => ({
      id: course.id,
      title: course.title,
      category: course.category,
      difficulty: course.difficulty,
      duration: course.duration,
      price: course.price,
      skills: course.skills,
      x: 0,
      y: 0
    }));

    const links: any[] = [];
    filteredCourses.forEach(course => {
      if (course.prerequisites) {
        course.prerequisites.forEach(prereqId => {
          links.push({
            source: prereqId,
            target: course.id,
            type: 'prerequisite'
          });
        });
      }
    });

    // Create force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(60));

    const g = svg.append("g");

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 2])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom as any);

    // Create gradient definitions
    const defs = svg.append("defs");

    // Create gradients for different difficulty levels
    const difficultyColors = {
      beginner: ["#10b981", "#34d399"],
      intermediate: ["#3b82f6", "#60a5fa"],
      advanced: ["#8b5cf6", "#a78bfa"]
    };

    Object.entries(difficultyColors).forEach(([level, colors]) => {
      const gradient = defs.append("linearGradient")
        .attr("id", `gradient-${level}`)
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "100%");

      gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", colors[0]);

      gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", colors[1]);
    });

    // Draw links
    const link = g.append("g")
      .selectAll("path")
      .data(links)
      .enter().append("path")
      .attr("stroke", "#4ade80")
      .attr("stroke-opacity", 0.3)
      .attr("stroke-width", 2)
      .attr("fill", "none")
      .attr("marker-end", "url(#arrowhead)");

    // Add arrow marker
    defs.append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#4ade80");

    // Draw nodes
    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .enter().append("g")
      .attr("cursor", "pointer")
      .on("click", (event, d: any) => onCourseSelect(d.id))
      .on("mouseenter", (event, d: any) => setHoveredNode(d.id))
      .on("mouseleave", () => setHoveredNode(null));

    // Add circles for nodes
    node.append("circle")
      .attr("r", 40)
      .attr("fill", (d: any) => `url(#gradient-${d.difficulty})`)
      .attr("stroke", (d: any) => {
        const progress = userProgress.get(d.id);
        if (progress === 100) return "#10b981";
        if (progress && progress > 0) return "#f59e0b";
        return "#374151";
      })
      .attr("stroke-width", 3)
      .attr("opacity", (d: any) => {
        if (selectedSkills.length === 0) return 1;
        const hasMatchingSkill = d.skills.some((skill: string) =>
          selectedSkills.includes(skill)
        );
        return hasMatchingSkill ? 1 : 0.3;
      });

    // Add progress arc
    const arc = d3.arc()
      .innerRadius(38)
      .outerRadius(42)
      .startAngle(0);

    node.each(function(d: any) {
      const progress = userProgress.get(d.id) || 0;
      if (progress > 0 && progress < 100) {
        d3.select(this).append("path")
          .datum({ endAngle: (progress / 100) * 2 * Math.PI })
          .style("fill", "#10b981")
          .attr("d", arc as any);
      }
    });

    // Add icons
    node.append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "24")
      .attr("fill", "white")
      .text((d: any) => {
        const categoryIcons: Record<string, string> = {
          "Accelerated Computing": "⚡",
          "Deep Learning": "🧠",
          "Generative AI and LLMs": "🤖",
          "Computer Vision": "👁️",
          "Data Center and Cloud": "☁️"
        };
        return categoryIcons[d.category] || "📚";
      });

    // Add labels
    const label = node.append("g")
      .attr("transform", "translate(0, 55)");

    label.append("rect")
      .attr("x", -60)
      .attr("y", -10)
      .attr("width", 120)
      .attr("height", 20)
      .attr("fill", "black")
      .attr("opacity", 0.7)
      .attr("rx", 4);

    label.append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "10")
      .attr("fill", "white")
      .text((d: any) => {
        const title = d.title;
        return title.length > 20 ? title.substring(0, 20) + "..." : title;
      });

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link.attr("d", (d: any) => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [role, selectedSkills, userProgress, onCourseSelect]);

  return (
    <div className="relative">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-white">Learning Pathway Map</h3>
        <div className="flex space-x-2">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-green-500 to-green-400"></div>
            <span className="text-xs text-gray-300">Beginner</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-blue-500 to-blue-400"></div>
            <span className="text-xs text-gray-300">Intermediate</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-gradient-to-r from-purple-500 to-purple-400"></div>
            <span className="text-xs text-gray-300">Advanced</span>
          </div>
        </div>
      </div>
      <svg
        ref={svgRef}
        width="100%"
        height="600"
        className="bg-black/20 rounded-lg"
      />
      {hoveredNode && (
        <div className="absolute top-4 right-4 bg-black/90 p-4 rounded-lg max-w-xs">
          <p className="text-white text-sm">
            Click on a course to view details and enroll
          </p>
        </div>
      )}
    </div>
  );
};