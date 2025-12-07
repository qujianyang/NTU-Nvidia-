/**
 * Learning Paths Visualization with Cytoscape.js
 * Interactive course relationship graph - Enhanced Aesthetics
 */

// Global variables
let cy = null;
let allCourses = []; // This will now store the full catalog for filtering
let currentGraphCourses = []; // This will store the courses currently displayed in the graph
let currentFilter = 'all';
let currentDomainFilter = 'all';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Register dagre layout
    if (typeof cytoscape !== 'undefined' && typeof dagre !== 'undefined') {
        cytoscape.use(cytoscapeDagre);
        console.log('Cytoscape.js and Dagre loaded successfully');
    }
    loadInitialCatalog(); // Load the full catalog initially

    // Event listener for the new Generate Path button
    const generateButton = document.getElementById('generate-path-btn');
    if (generateButton) {
        generateButton.addEventListener('click', generateLearningPath);
    }
});

// Load the full course catalog for initial display and filtering
async function loadInitialCatalog() {
    const loadingEl = document.getElementById('graph-loading');
    const containerEl = document.getElementById('graph-container');

    loadingEl.style.display = 'block'; // Ensure loading indicator is visible
    containerEl.style.display = 'none'; // Hide graph container

    try {
        console.log('Fetching full course catalog from API...');
        const response = await fetch('/api/courses');

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        allCourses = await response.json();
        console.log('Full catalog loaded:', allCourses.length, 'courses');

        if (!allCourses || allCourses.length === 0) {
            loadingEl.innerHTML = '<p style="color: #d32f2f;">No courses found in database.</p>';
            return;
        }

        // Hide loading, show graph container
        loadingEl.style.display = 'none';
        containerEl.classList.add('show');
        containerEl.style.display = 'block';

        currentGraphCourses = allCourses; // Display full catalog initially
        console.log('Building initial graph with Cytoscape.js...');
        buildGraph(currentGraphCourses);
        console.log('Initial graph built successfully');
    } catch (error) {
        console.error('Error loading initial catalog:', error);
        loadingEl.innerHTML = `<p style="color: #d32f2f;">Error loading initial catalog: ${error.message}<br>Please check console for details.</p>`;
    }
}

// Function to generate learning path dynamically
async function generateLearningPath() {
    const goalInput = document.getElementById('user-goal-input');
    const pathLoadingEl = document.getElementById('path-loading');
    const pathErrorEl = document.getElementById('path-error');
    const userGoal = goalInput.value.trim();

    // Clear previous results/errors
    pathErrorEl.style.display = 'none';
    pathErrorEl.textContent = '';
    
    if (!userGoal) {
        pathErrorEl.textContent = 'Please enter a learning goal.';
        pathErrorEl.style.display = 'block';
        return;
    }

    pathLoadingEl.style.display = 'block';
    if (cy) {
        cy.destroy(); // Clear existing graph before showing new one
        cy = null;
    }

    try {
        console.log('Generating learning path for goal:', userGoal);
        const response = await fetch('/api/generate_learning_path', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_goal: userGoal })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const learningPath = data.learning_path;

        if (!learningPath || learningPath.length === 0) {
            pathErrorEl.textContent = 'Could not generate a learning path for your goal. Please try a different goal.';
            pathErrorEl.style.display = 'block';
            // If path generation fails, rebuild the initial catalog graph
            buildGraph(allCourses);
        } else {
            console.log('Generated Learning Path:', learningPath);
            currentGraphCourses = learningPath; // Set generated path as current courses to display
            buildGraph(currentGraphCourses); // Build graph with the generated path
        }
    } catch (error) {
        console.error('Error generating learning path:', error);
        pathErrorEl.textContent = `Error: ${error.message}`;
        pathErrorEl.style.display = 'block';
        // If path generation fails, rebuild the initial catalog graph
        buildGraph(allCourses);
    } finally {
        pathLoadingEl.style.display = 'none';
    }
}

// Build the Cytoscape.js graph
function buildGraph(coursesToDisplay) { 
    console.log('Building graph with', coursesToDisplay.length, 'courses');

    // Check if Cytoscape is loaded
    if (typeof cytoscape === 'undefined') {
        console.error('Cytoscape.js library is not loaded!');
        alert('Graph library failed to load. Please refresh the page.');
        return;
    }

    // Destroy existing instance if it exists
    if (cy) {
        cy.destroy();
    }

    // Create nodes
    const elements = [];

    coursesToDisplay.forEach(course => {
        const level = getLevelFromCourse(course);
        // We use classes for styling now instead of hardcoded colors in data
        
        elements.push({
            data: {
                id: course.id,
                label: breakLabel(course.title), // Break long labels
                level: level,
                courseData: course,
                domain: course.domain || 'LLM'
            },
            classes: `${level} ${course.domain === 'Robotics' ? 'robotics' : 'llm'}`
        });
    });

    // Create edges from prerequisites
    let edgeCount = 0;
    coursesToDisplay.forEach(course => {
        if (course.prerequisites && Array.isArray(course.prerequisites)) {
            course.prerequisites.forEach(prereqId => {
                if (coursesToDisplay.some(c => c.id === prereqId)) { 
                    elements.push({
                        data: {
                            id: `${prereqId}-${course.id}`,
                            source: prereqId,
                            target: course.id
                        }
                    });
                    edgeCount++;
                }
            });
        }
    });

    const container = document.getElementById('network');
    
    try {
        cy = cytoscape({
            container: container,
            elements: elements,
            style: getCytoscapeStyle(),
            layout: {
                name: 'dagre',
                rankDir: 'TB', 
                nodeSep: 80,
                rankSep: 120,
                padding: 50,
                animate: true,
                animationDuration: 800,
                animationEasing: 'ease-out-cubic'
            },
            minZoom: 0.3,
            maxZoom: 2,
            wheelSensitivity: 0.3
        });

        // Interactive events
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const course = node.data('courseData');
            
            // Highlight interaction
            cy.elements().removeClass('highlighted');
            node.addClass('highlighted');
            node.predecessors().addClass('highlighted');
            node.successors().addClass('highlighted');
            
            if (course) {
                showCoursePanel(course);
            }
        });

        cy.on('tap', function(evt) {
            if (evt.target === cy) {
                closeCoursePanel();
                cy.elements().removeClass('highlighted');
            }
        });

        cy.on('mouseover', 'node', function(evt) {
            document.body.style.cursor = 'pointer';
            evt.target.addClass('hover');
        });

        cy.on('mouseout', 'node', function(evt) {
            document.body.style.cursor = 'default';
            evt.target.removeClass('hover');
        });

        // Fit to viewport after layout
        // setTimeout(() => {
        //     cy.fit(null, 50);
        // }, 200);

    } catch (error) {
        console.error('Error creating Cytoscape graph:', error);
    }
}

// Helper to break long labels
function breakLabel(label) {
    if (label.length > 25) {
        const words = label.split(' ');
        let lines = [];
        let currentLine = words[0];
        
        for (let i = 1; i < words.length; i++) {
            if (currentLine.length + words[i].length < 20) {
                currentLine += ' ' + words[i];
            } else {
                lines.push(currentLine);
                currentLine = words[i];
            }
        }
        lines.push(currentLine);
        return lines.join('\n');
    }
    return label;
}

// Get Cytoscape style - Enhanced aesthetics
function getCytoscapeStyle() {
    return [
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-wrap': 'wrap',
                'font-size': '14px',
                'font-weight': '600',
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#333',
                'background-color': '#ffffff',
                'border-width': 0,
                'width': 180,
                'height': 80,
                'shape': 'round-rectangle',
                'corner-radius': 12,
                'text-max-width': 160,
                'line-height': 1.2,
                'shadow-blur': 15,
                'shadow-color': 'rgba(0,0,0,0.1)',
                'shadow-offset-y': 5,
                'shadow-opacity': 1,
                'overlay-opacity': 0 // Remove default selection overlay
            }
        },
        // Level-based borders (subtle indicator)
        {
            selector: 'node.beginner',
            style: {
                'border-width': 4,
                'border-color': '#52c41a', // Green
                'border-opacity': 0.8
            }
        },
        {
            selector: 'node.intermediate',
            style: {
                'border-width': 4,
                'border-color': '#faad14', // Orange
                'border-opacity': 0.8
            }
        },
        {
            selector: 'node.advanced',
            style: {
                'border-width': 4,
                'border-color': '#f5222d', // Red
                'border-opacity': 0.8
            }
        },
        {
            selector: 'node.general',
            style: {
                'border-width': 4,
                'border-color': '#1890ff', // Blue
                'border-opacity': 0.8
            }
        },
        // Domain specific styling (icons/backgrounds could be added here if we had images)
        {
            selector: 'node.robotics',
            style: {
                // Robotics specific styling if needed
            }
        },
        // Interaction states
        {
            selector: 'node.hover',
            style: {
                'shadow-blur': 25,
                'shadow-offset-y': 8,
                'shadow-color': 'rgba(118, 185, 0, 0.3)',
                'width': 190, // slight scale up
                'height': 90,
                'z-index': 999
            }
        },
        {
            selector: 'node:selected',
            style: {
                'border-width': 4,
                'border-color': '#76b900',
                'background-color': '#f6ffed'
            }
        },
        // Edge styling
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#d9d9d9',
                'target-arrow-color': '#d9d9d9',
                'target-arrow-shape': 'triangle-backcurve', // modernized arrow
                'curve-style': 'bezier',
                'arrow-scale': 1.2,
                'opacity': 0.8
            }
        },
        {
            selector: 'edge.highlighted',
            style: {
                'line-color': '#76b900',
                'target-arrow-color': '#76b900',
                'width': 3,
                'opacity': 1,
                'z-index': 100
            }
        },
        {
            selector: 'node.highlighted',
            style: {
                'border-color': '#76b900',
                'border-width': 4,
                'shadow-color': 'rgba(118, 185, 0, 0.4)',
                'shadow-blur': 20
            }
        }
    ];
}

// Filter by domain
function filterByDomain(domain) {
    if (!cy) return;

    currentDomainFilter = domain;

    // Update active button (assuming 'event.target' exists, if not, find by ID)
    document.querySelectorAll('.domain-filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(domain.toLowerCase()) || (domain === 'all' && btn.textContent.toLowerCase().includes('all domains'))) {
            btn.classList.add('active');
        }
    });

    // Apply both domain and level filters on the current graph courses
    applyFilters(currentGraphCourses);
}

// Filter by level
function filterByLevel(level) {
    if (!cy) return;

    currentFilter = level;

    // Update active button (assuming 'event.target' exists, if not, find by ID)
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(level.toLowerCase()) || (level === 'all' && btn.textContent.toLowerCase().includes('all courses'))) {
            btn.classList.add('active');
        }
    });

    // Apply both domain and level filters on the current graph courses
    applyFilters(currentGraphCourses);
}

// Apply both domain and level filters
function applyFilters(coursesToFilter = currentGraphCourses) { 
    if (!cy) return;

    const nodesToShow = cy.collection();
    
    coursesToFilter.forEach(course => {
        const node = cy.getElementById(course.id);
        if (!node) return; 

        const courseLevel = getLevelFromCourse(course);
        const courseDomain = course.domain || 'LLM';

        let showNode = true;

        // Check domain filter
        if (currentDomainFilter !== 'all') {
            if (courseDomain !== currentDomainFilter) {
                showNode = false;
            }
        }

        // Check level filter
        if (currentFilter !== 'all') {
            if (!courseLevel.toLowerCase().includes(currentFilter)) {
                showNode = false;
            }
        }

        if (showNode) {
            nodesToShow.merge(node);
        }
    });

    // Show/hide nodes based on filter and ensure edges are handled
    cy.nodes().hide();
    cy.edges().hide(); // Hide all edges first

    nodesToShow.show();
    nodesToShow.connectedEdges().show(); // Show edges connected to visible nodes
    
    cy.fit(nodesToShow, 50); // Fit to only visible nodes
}

// Search courses
function searchCourses(query) {
    if (!cy) return;

    if (!query || query.trim() === '') {
        applyFilters(currentGraphCourses); // Re-apply existing filters if search is cleared
        return;
    }

    query = query.toLowerCase();
    const nodesToShow = cy.collection();

    currentGraphCourses.forEach(course => {
        const node = cy.getElementById(course.id);
        if (!node) return;

        const matchesTitle = course.title.toLowerCase().includes(query);
        const matchesId = course.id.toLowerCase().includes(query);

        if (matchesTitle || matchesId) {
            nodesToShow.merge(node);
        }
    });
    
    // Show/hide nodes based on search and ensure edges are handled
    cy.nodes().hide();
    cy.edges().hide();
    
    nodesToShow.show();
    nodesToShow.connectedEdges().show();
    
    cy.fit(nodesToShow, 50);
}


// Reset view
function resetView() {
    if (!cy) return;

    currentFilter = 'all';
    currentDomainFilter = 'all';
    document.getElementById('search-input').value = '';

    // Update level filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.filter-btn').classList.add('active');

    // Update domain filter buttons
    document.querySelectorAll('.domain-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.domain-filter-btn').classList.add('active');

    // Rebuild graph with allCourses (full catalog)
    currentGraphCourses = allCourses;
    buildGraph(currentGraphCourses);

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
    const domain = course.domain || 'LLM';
    const isFree = price.toLowerCase() === 'free';

    let html = `
        <div class="course-info-header">
            <h3>${escapeHtml(course.title)}</h3>
            <div>
                <span class="course-badge domain" style="background: ${domain === 'Robotics' ? '#722ed1' : '#1890ff'};">
                    <i class="fas fa-${domain === 'Robotics' ? 'robot' : 'brain'}"></i> ${escapeHtml(domain)}
                </span>
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
            const prereq = allCourses.find(c => c.id === prereqId); // Use allCourses here
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
            const nextCourse = allCourses.find(c => c.id === nextId); // Use allCourses here
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
