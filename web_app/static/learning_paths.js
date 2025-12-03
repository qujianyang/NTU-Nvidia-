/**
 * Learning Paths Visualization with Cytoscape.js
 * Interactive course relationship graph
 */

// Global variables
let cy = null;
let allCourses = []; // This will now store the full catalog for filtering
let currentGraphCourses = []; // This will store the courses currently displayed in the graph
let currentFilter = 'all';
let currentDomainFilter = 'all';
let currentLayout = 'hierarchical';

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
function buildGraph(coursesToDisplay) { // Changed parameter name
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
    coursesToDisplay.forEach(course => {
        if (course.prerequisites && Array.isArray(course.prerequisites)) {
            course.prerequisites.forEach(prereqId => {
                // Ensure prerequisite course is also in the current graph courses
                if (coursesToDisplay.some(c => c.id === prereqId)) { // Use coursesToDisplay
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
function applyFilters(coursesToFilter = currentGraphCourses) { // Added coursesToFilter parameter
    if (!cy) return;

    const nodesToShow = cy.collection();
    
    coursesToFilter.forEach(course => {
        const node = cy.getElementById(course.id);
        if (!node) return; // Node might not exist if it's from allCourses but not in currentGraphCourses

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

// Filter by domain
function filterByDomain(domain) {
    if (!cy) return;

    currentDomainFilter = domain;

    // Update active button
    document.querySelectorAll('.domain-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Apply both domain and level filters
    applyFilters();
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

    // Apply both domain and level filters
    applyFilters();
}

// Apply both domain and level filters
function applyFilters() {
    if (!cy) return;

    cy.nodes().forEach(node => {
        const course = node.data('courseData');
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
            node.show();
        } else {
            node.hide();
        }
    });

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
