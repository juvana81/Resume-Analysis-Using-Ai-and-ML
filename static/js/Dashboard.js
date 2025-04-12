// Dashboard.js - Handles all dashboard functionality and charts

// Global chart objects for updating
const charts = {};
let dashboardData = null;
let filteredData = null;

// Fetch dashboard data
async function fetchDashboardData() {
    try {
        const response = await fetch('static/data/dashboard_data.json');
        dashboardData = await response.json();
        filteredData = dashboardData; // Initially, all data is shown
        updateDashboard();
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        alert('Failed to load dashboard data. Please check if the data file exists.');
    }
}

// Update dashboard based on current filtered data
function updateDashboard() {
    if (!filteredData) return;
    
    updateMetrics();
    updateCharts();
}

// Update key metrics
function updateMetrics() {
    document.getElementById('total-students').textContent = filteredData.stats.total_students;
    document.getElementById('placement-rate').textContent = filteredData.stats.placement_rate + '%';
    document.getElementById('avg-cgpa').textContent = filteredData.stats.avg_cgpa;
    
    const internshipCount = filteredData.stats.with_internships;
    const internshipPercent = ((internshipCount / filteredData.stats.total_students) * 100).toFixed(1);
    document.getElementById('with-internships').textContent = `${internshipCount} (${internshipPercent}%)`;
}

// Create and update all charts
function updateCharts() {
    // Overview tab charts
    createCGPADistributionChart();
    createSkillsChart();
    createInternshipPlacementChart();
    createProjectsPlacementChart();
    
    // CGPA Analysis tab charts
    // Note: We're not implementing the scatter plot as it requires individual student data
    createPlacementByCGPAChart();
    createCGPADistributionBarChart();
    createCGPADistributionPieChart();
    
    // Skills tab charts
    createSkillsBarChart();
    createSkillsPieChart();
    
    // Placement tab charts
    createPlacementStatusPieChart();
    createPlacementCGPABarChart();
    createInternshipImpactChart();
    createProjectsImpactChart();
}

// Chart creation functions
function createCGPADistributionChart() {
    const ctx = document.getElementById('cgpa-distribution-chart').getContext('2d');
    
    const labels = Object.keys(filteredData.cgpa_distribution);
    const data = Object.values(filteredData.cgpa_distribution);
    
    if (charts.cgpaDistribution) {
        charts.cgpaDistribution.destroy();
    }
    
    charts.cgpaDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Students',
                data: data,
                backgroundColor: '#8884d8',
                borderColor: '#7464d8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createSkillsChart() {
    const ctx = document.getElementById('skills-distribution-chart').getContext('2d');
    
    const skills = filteredData.skills_data;
    const labels = Object.keys(skills);
    const data = Object.values(skills);
    
    if (charts.skillsDistribution) {
        charts.skillsDistribution.destroy();
    }
    
    charts.skillsDistribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Students',
                data: data,
                backgroundColor: '#82ca9d',
                borderColor: '#62aa7d',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createInternshipPlacementChart() {
    const ctx = document.getElementById('internship-placement-chart').getContext('2d');
    
    const internshipData = filteredData.internship_vs_placement;
    
    if (charts.internshipPlacement) {
        charts.internshipPlacement.destroy();
    }
    
    charts.internshipPlacement = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['With Internship', 'Without Internship'],
            datasets: [
                {
                    label: 'Placed',
                    data: [
                        internshipData.with_internship.placed,
                        internshipData.without_internship.placed
                    ],
                    backgroundColor: '#82ca9d'
                },
                {
                    label: 'Not Placed',
                    data: [
                        internshipData.with_internship.not_placed,
                        internshipData.without_internship.not_placed
                    ],
                    backgroundColor: '#ff7f7f'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createProjectsPlacementChart() {
    const ctx = document.getElementById('projects-placement-chart').getContext('2d');
    
    const projectsData = filteredData.projects_vs_placement;
    
    if (charts.projectsPlacement) {
        charts.projectsPlacement.destroy();
    }
    
    charts.projectsPlacement = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['With Projects', 'Without Projects'],
            datasets: [
                {
                    label: 'Placed',
                    data: [
                        projectsData.with_projects.placed,
                        projectsData.without_projects.placed
                    ],
                    backgroundColor: '#82ca9d'
                },
                {
                    label: 'Not Placed',
                    data: [
                        projectsData.with_projects.not_placed,
                        projectsData.without_projects.not_placed
                    ],
                    backgroundColor: '#ff7f7f'
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createPlacementByCGPAChart() {
    const ctx = document.getElementById('placement-by-cgpa-chart').getContext('2d');
    
    const placementByCGPA = filteredData.placement_by_cgpa;
    const labels = Object.keys(placementByCGPA);
    const data = Object.values(placementByCGPA);
    
    if (charts.placementByCGPA) {
        charts.placementByCGPA.destroy();
    }
    
    charts.placementByCGPA = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Placement Rate (%)',
                data: data,
                backgroundColor: '#82ca9d',
                borderColor: '#62aa7d',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Placement Rate (%)'
                    }
                }
            }
        }
    });
}

function createCGPADistributionBarChart() {
    const ctx = document.getElementById('cgpa-distribution-bar').getContext('2d');
    
    const labels = Object.keys(filteredData.cgpa_distribution);
    const data = Object.values(filteredData.cgpa_distribution);
    
    if (charts.cgpaDistributionBar) {
        charts.cgpaDistributionBar.destroy();
    }
    
    charts.cgpaDistributionBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Students',
                data: data,
                backgroundColor: '#8884d8',
                borderColor: '#7464d8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createCGPADistributionPieChart() {
    const ctx = document.getElementById('cgpa-distribution-pie').getContext('2d');
    
    const cgpaDistribution = filteredData.cgpa_distribution;
    const labels = Object.keys(cgpaDistribution);
    const data = Object.values(cgpaDistribution);
    
    if (charts.cgpaDistributionPie) {
        charts.cgpaDistributionPie.destroy();
    }
    
    charts.cgpaDistributionPie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createSkillsBarChart() {
    const ctx = document.getElementById('skills-bar-chart').getContext('2d');
    
    const skills = filteredData.skills_data;
    const labels = Object.keys(skills);
    const data = Object.values(skills);
    
    if (charts.skillsBar) {
        charts.skillsBar.destroy();
    }
    
    charts.skillsBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Students',
                data: data,
                backgroundColor: '#82ca9d',
                borderColor: '#62aa7d',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createSkillsPieChart() {
    const ctx = document.getElementById('skills-pie-chart').getContext('2d');
    
    const skills = filteredData.skills_data;
    const labels = Object.keys(skills);
    const data = Object.values(skills);
    
    if (charts.skillsPie) {
        charts.skillsPie.destroy();
    }
    
    charts.skillsPie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#8AC249',
                    '#EA80FC',
                    '#00E5FF',
                    '#FF5252'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createPlacementStatusPieChart() {
    const ctx = document.getElementById('placement-status-pie').getContext('2d');
    
    const placementData = filteredData.placement_status;
    
    if (charts.placementStatusPie) {
        charts.placementStatusPie.destroy();
    }
    
    charts.placementStatusPie = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Placed', 'Not Placed'],
            datasets: [{
                data: [placementData.placed, placementData.not_placed],
                backgroundColor: [
                    '#82ca9d',
                    '#ff7f7f'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createPlacementCGPABarChart() {
    const ctx = document.getElementById('placement-cgpa-bar').getContext('2d');
    
    const placementByCGPA = filteredData.placement_by_cgpa;
    const labels = Object.keys(placementByCGPA);
    const data = Object.values(placementByCGPA);
    
    if (charts.placementCGPABar) {
        charts.placementCGPABar.destroy();
    }
    
    charts.placementCGPABar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Placement Rate (%)',
                data: data,
                backgroundColor: '#8884d8',
                borderColor: '#7464d8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Placement Rate (%)'
                    }
                }
            }
        }
    });
}

function createInternshipImpactChart() {
    const ctx = document.getElementById('internship-impact-chart').getContext('2d');
    
    const internshipData = filteredData.internship_vs_placement;
    
    if (charts.internshipImpact) {
        charts.internshipImpact.destroy();
    }
    
    const withInternshipTotal = internshipData.with_internship.placed + internshipData.with_internship.not_placed;
    const withoutInternshipTotal = internshipData.without_internship.placed + internshipData.without_internship.not_placed;
    
    const withInternshipRate = withInternshipTotal > 0 ? 
        (internshipData.with_internship.placed / withInternshipTotal * 100).toFixed(1) : 0;
    const withoutInternshipRate = withoutInternshipTotal > 0 ? 
        (internshipData.without_internship.placed / withoutInternshipTotal * 100).toFixed(1) : 0;
    
    charts.internshipImpact = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['With Internship', 'Without Internship'],
            datasets: [{
                label: 'Placement Rate (%)',
                data: [withInternshipRate, withoutInternshipRate],
                backgroundColor: '#8884d8',
                borderColor: '#7464d8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Placement Rate (%)'
                    }
                }
            }
        }
    });
}

function createProjectsImpactChart() {
    const ctx = document.getElementById('projects-impact-chart').getContext('2d');
    
    const projectsData = filteredData.projects_vs_placement;
    
    if (charts.projectsImpact) {
        charts.projectsImpact.destroy();
    }
    
    const withProjectsTotal = projectsData.with_projects.placed + projectsData.with_projects.not_placed;
    const withoutProjectsTotal = projectsData.without_projects.placed + projectsData.without_projects.not_placed;
    
    const withProjectsRate = withProjectsTotal > 0 ? 
        (projectsData.with_projects.placed / withProjectsTotal * 100).toFixed(1) : 0;
    const withoutProjectsRate = withoutProjectsTotal > 0 ? 
        (projectsData.without_projects.placed / withoutProjectsTotal * 100).toFixed(1) : 0;
    
    charts.projectsImpact = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['With Projects', 'Without Projects'],
            datasets: [{
                label: 'Placement Rate (%)',
                data: [withProjectsRate, withoutProjectsRate],
                backgroundColor: '#8884d8',
                borderColor: '#7464d8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Placement Rate (%)'
                    }
                }
            }
        }
    });
}

// Filter dashboard based on selected CGPA range
function filterByCGPA(min, max) {
    // This is a simplified implementation
    // In a real application, you would filter the actual student data
    // For now, we'll just switch between the full dataset and a filtered version
    
    if (min === undefined && max === undefined) {
        // Reset filters
        filteredData = dashboardData;
    } else {
        // For demo purposes, just reduce all numbers by 30%
        // In a real application, you would filter the actual student data
        filteredData = JSON.parse(JSON.stringify(dashboardData)); // Deep clone
        
        // Simulate filtering by reducing some numbers
        filteredData.stats.total_students = Math.round(filteredData.stats.total_students * 0.7);
        filteredData.stats.with_internships = Math.round(filteredData.stats.with_internships * 0.7);
        
        // Reduce distribution numbers
        Object.keys(filteredData.cgpa_distribution).forEach(key => {
            // Only reduce numbers for CGPAs outside the specified range
            if (parseFloat(key) < min || parseFloat(key) > max) {
                filteredData.cgpa_distribution[key] = Math.round(filteredData.cgpa_distribution[key] * 0.3);
            }
        });
        
        // Reduce other metrics proportionally
        // In a real application, these would be recalculated based on filtered student data
    }
    
    updateDashboard();
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    fetchDashboardData();
    
    // Set up filter buttons
    document.getElementById('reset-filters').addEventListener('click', function() {
        filterByCGPA();
    });
    
    document.getElementById('filter-high-cgpa').addEventListener('click', function() {
        filterByCGPA(8.0, 10.0);
    });
    
    document.getElementById('filter-med-cgpa').addEventListener('click', function() {
        filterByCGPA(6.0, 8.0);
    });
    
    document.getElementById('filter-low-cgpa').addEventListener('click', function() {
        filterByCGPA(0.0, 6.0);
    });
    
    // Set up tab switching
    const tabs = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Deactivate all tabs and hide all tab contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Activate clicked tab and show corresponding content
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
});