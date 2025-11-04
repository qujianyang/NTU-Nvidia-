/**
 * Learning Paths Visualization with Cytoscape.js
 * Interactive course relationship graph
 */

// Global variables
let cy = null;
let allCourses = [];
let currentFilter = 'all';
let currentLayout = 'hierarchical';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Register dagre layout
    if (typeof cytoscape !== 'undefined' && typeof dagre !== 'undefined') {
        cytoscape.use(cytoscapeDagre);
        console.log('Cytoscape.js and Dagre loaded successfully');
    }
    loadCoursesAndBuildGraph();
});

// Load courses and build the graph
async function loadCoursesAndBuildGraph() {
    const loadingEl = document.getElementById('graph-loading');
    const containerEl = document.getElementById('graph-container');

    try {
        console.log('Fetching courses from API...');
        const response = await fetch('/api/courses');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        allCourses = await response.json();
        console.log('Courses loaded:', allCourses.length, 'courses');

        if (!allCourses || allCourses.length === 0) {
            loadingEl.innerHTML = '<p style="color: #d32f2f;">No courses found in database.</p>';
            return;
        }

        // Hide loading, show graph container
        loadingEl.style.display = 'none';
        containerEl.classList.add('show');
        containerEl.style.display = 'block';

        console.log('Building graph with Cytoscape.js...');
        buildGraph(allCourses);
        console.log('Graph built successfully');
    } catch (error) {
        console.error('Error loading courses:', error);
        loadingEl.innerHTML = `<p style="color: #d32f2f;">Error loading courses: ${error.message}<br>Please check console for details.</p>`;
    }
}

// Build the Cytoscape.js graph
function buildGraph(courses) {
    console.log('Building graph with', courses.length, 'courses');

    // Check if Cytoscape is loaded
    if (typeof cytoscape === 'undefined') {
        console.error('Cytoscape.js library is not loaded!');
        alert('Graph library failed to load. Please refresh the page.');
        return;
    }

    // Create nodes
    const elements = [];

    courses.forEach(course => {
        const level = getLevelFromCourse(course);
        const color = getLevelColor(level);

        elements.push({
            data: {
                id: course.id,
                label: course.title,
                level: level,
                courseData: course
            },
            classes: level
        });
    });

    console.log('Created', elements.length, 'nodes');

    // Create edges from prerequisites
    let edgeCount = 0;
    courses.forEach(course => {
        if (course.prerequisites && Array.isArray(course.prerequisites)) {
            course.prerequisites.forEach(prereqId => {
                elements.push({
                    data: {
                        id: `${prereqId}-${course.id}`,
                        source: prereqId,
                        target: course.id
                    }
                });
                edgeCount++;
            });
        }
    });

    console.log('Created', edgeCount, 'edges');

    // Create Cytoscape instance
    const container = document.getElementById('network');
    if (!container) {
        console.error('Network container element not found!');
        return;
    }

    console.log('Container found:', container);
    console.log('Container dimensions:', container.offsetWidth, 'x', container.offsetHeight);

    try {
        cy = cytoscape({
            container: container,
            elements: elements,
            style: getCytoscapeStyle(),
            layout: getLayoutOptions(currentLayout),
            minZoom: 0.3,
            maxZoom: 3,
            wheelSensitivity: 0.2
        });

        console.log('Cytoscape graph created successfully');
        console.log('Nodes:', cy.nodes().length, 'Edges:', cy.edges().length);

        // Add event listeners
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const course = node.data('courseData');
            if (course) {
                showCoursePanel(course);
            }
        });

        cy.on('tap', function(evt) {
            if (evt.target === cy) {
                closeCoursePanel();
            }
        });

        // Fit to viewport after layout
        setTimeout(() => {
            cy.fit(null, 50);
            console.log('Graph fitted to viewport');
        }, 100);

    } catch (error) {
        console.error('Error creating Cytoscape graph:', error);
    }
}

// Get Cytoscape style
function getCytoscapeStyle() {
    return [
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-wrap': 'wrap',
                'text-max-width': '150px',
                'font-size': '12px',
                'font-weight': 'bold',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#ffffff',
                'background-color': '#1890ff',
                'border-width': 2,
                'border-color': '#0050b3',
                'width': 'label',
                'height': 'label',
                'padding': '10px',
                'shape': 'roundrectangle'
            }
        },
        {
            selector: 'node.beginner',
            style: {
                'background-color': '#52c41a',
                'border-color': '#237804'
            }
        },
        {
            selector: 'node.intermediate',
            style: {
                'background-color': '#faad14',
                'border-color': '#d46b08'
            }
        },
        {
            selector: 'node.advanced',
            style: {
                'background-color': '#f5222d',
                'border-color': '#a8071a'
            }
        },
        {
            selector: 'node.general',
            style: {
                'background-color': '#1890ff',
                'border-color': '#0050b3'
            }
        },
        {
            selector: 'node:selected',
            style: {
                'border-width': 4,
                'border-color': '#76b900'
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#999',
                'target-arrow-color': '#999',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'arrow-scale': 1.5
            }
        },
        {
            selector: 'edge:selected',
            style: {
                'line-color': '#76b900',
                'target-arrow-color': '#76b900',
                'width': 3
            }
        }
    ];
}

// Get layout options
function getLayoutOptions(layout) {
    if (layout === 'hierarchical') {
        return {
            name: 'dagre',
            rankDir: 'TB', // Top to bottom
            nodeSep: 100,
            rankSep: 150,
            animate: true,
            animationDuration: 500
        };
    } else if (layout === 'circular') {
        return {
            name: 'circle',
            animate: true,
            animationDuration: 500
        };
    } else {
        // Network (force-directed)
        return {
            name: 'cose',
            animate: true,
            animationDuration: 500,
            nodeRepulsion: 8000,
            idealEdgeLength: 150,
            nodeOverlap: 20,
            gravity: 1
        };
    }
}

// Filter by level
function filterByLevel(level) {
    if (!cy) return;

    currentFilter = level;

    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Filter nodes
    if (level === 'all') {
        cy.nodes().show();
    } else {
        cy.nodes().forEach(node => {
            const course = node.data('courseData');
            const courseLevel = getLevelFromCourse(course);
            if (courseLevel.toLowerCase().includes(level)) {
                node.show();
            } else {
                node.hide();
            }
        });
    }

    cy.fit(cy.nodes(':visible'), 50);
}

// Search courses
function searchCourses(query) {
    if (!cy) return;

    if (!query || query.trim() === '') {
        cy.nodes().show();
        cy.fit(null, 50);
        return;
    }

    query = query.toLowerCase();

    cy.nodes().forEach(node => {
        const course = node.data('courseData');
        const matchesTitle = course.title.toLowerCase().includes(query);
        const matchesId = course.id.toLowerCase().includes(query);

        if (matchesTitle || matchesId) {
            node.show();
        } else {
            node.hide();
        }
    });

    cy.fit(cy.nodes(':visible'), 50);
}

// Change layout
function changeLayout(layout) {
    if (!cy) return;

    currentLayout = layout;
    console.log('Changing layout to:', layout);

    const layoutOptions = getLayoutOptions(layout);
    const cyLayout = cy.layout(layoutOptions);
    cyLayout.run();

    setTimeout(() => {
        cy.fit(cy.nodes(':visible'), 50);
    }, 600);
}

// Reset view
function resetView() {
    if (!cy) return;

    currentFilter = 'all';
    document.getElementById('search-input').value = '';

    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.filter-btn').classList.add('active');

    // Show all nodes
    cy.nodes().show();
    cy.fit(null, 50);
}

// Fit graph to screen
function fitGraph() {
    if (!cy) return;

    cy.fit(cy.nodes(':visible'), 50);
}

// Show course info panel
function showCoursePanel(course) {
    const panel = document.getElementById('course-info-panel');
    const content = document.getElementById('course-info-content');

    content.innerHTML = createCourseInfoHTML(course);
    panel.classList.add('show');
}

// Close course panel
function closeCoursePanel() {
    const panel = document.getElementById('course-info-panel');
    panel.classList.remove('show');
}

// Create course info HTML
function createCourseInfoHTML(course) {
    const level = course.level || 'General Interest';
    const duration = course.duration || 'N/A';
    const price = course.price || 'Free';
    const isFree = price.toLowerCase() === 'free';

    let html = `
        <div class="course-info-header">
            <h3>${escapeHtml(course.title)}</h3>
            <div>
                <span class="course-badge level">${escapeHtml(level)}</span>
                <span class="course-badge duration">
                    <i class="fas fa-clock"></i> ${escapeHtml(duration)}
                </span>
                <span class="course-badge ${isFree ? 'free' : 'price'}">
                    ${isFree ? '<i class="fas fa-gift"></i>' : '<i class="fas fa-dollar-sign"></i>'}
                    ${escapeHtml(price)}
                </span>
            </div>
        </div>
    `;

    if (course.description) {
        html += `
            <div class="course-section">
                <h4><i class="fas fa-align-left"></i> Description</h4>
                <p>${escapeHtml(course.description)}</p>
            </div>
        `;
    }

    if (course.prerequisites && course.prerequisites.length > 0) {
        html += `
            <div class="course-section">
                <h4><i class="fas fa-arrow-left"></i> Prerequisites</h4>
                <ul class="course-list">
        `;
        course.prerequisites.forEach(prereqId => {
            const prereq = allCourses.find(c => c.id === prereqId);
            if (prereq) {
                html += `<li><i class="fas fa-check-circle"></i> ${escapeHtml(prereq.title)}</li>`;
            } else {
                html += `<li><i class="fas fa-check-circle"></i> ${escapeHtml(prereqId)}</li>`;
            }
        });
        html += `
                </ul>
            </div>
        `;
    }

    if (course.leads_to && course.leads_to.length > 0) {
        html += `
            <div class="course-section">
                <h4><i class="fas fa-arrow-right"></i> Leads To</h4>
                <ul class="course-list">
        `;
        course.leads_to.forEach(nextId => {
            const nextCourse = allCourses.find(c => c.id === nextId);
            if (nextCourse) {
                html += `<li><i class="fas fa-graduation-cap"></i> ${escapeHtml(nextCourse.title)}</li>`;
            } else {
                html += `<li><i class="fas fa-graduation-cap"></i> ${escapeHtml(nextId)}</li>`;
            }
        });
        html += `
                </ul>
            </div>
        `;
    }

    if (course.url) {
        html += `
            <a href="${escapeHtml(course.url)}" target="_blank" class="course-link">
                <i class="fas fa-external-link-alt"></i> View on NVIDIA Learn
            </a>
        `;
    }

    return html;
}

// Utility Functions

function getLevelFromCourse(course) {
    if (!course.level) return 'general';
    const level = course.level.toLowerCase();
    if (level.includes('beginner')) return 'beginner';
    if (level.includes('intermediate')) return 'intermediate';
    if (level.includes('advanced')) return 'advanced';
    return 'general';
}

function getLevelColor(level) {
    switch (level) {
        case 'beginner':
            return '#52c41a'; // Green
        case 'intermediate':
            return '#faad14'; // Orange
        case 'advanced':
            return '#f5222d'; // Red
        default:
            return '#1890ff'; // Blue
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
