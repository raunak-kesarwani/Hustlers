/**
 * Homework Page JavaScript
 * Handles homework generation functionality
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeHomeworkPage();
});

/**
 * Initialize homework page event listeners
 */
function initializeHomeworkPage() {
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Generate homework button
    const generateBtn = document.getElementById('generateHomeworkBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateHomework);
    }
}

/**
 * Generate homework
 */
async function generateHomework() {
    const topic = document.getElementById('homeworkTopic').value.trim();
    const difficulty = document.getElementById('homeworkDifficulty').value;
    
    if (!topic) {
        alert('Please enter a topic');
        return;
    }
    
    // Show loading
    const loading = document.getElementById('loading');
    const results = document.getElementById('homeworkResults');
    if (loading) loading.classList.remove('hidden');
    if (results) results.classList.add('hidden');
    
    try {
        const response = await fetch('/homework', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                difficulty: difficulty
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (results) {
                results.innerHTML = `
                    <h3>Homework: ${escapeHtml(topic)}</h3>
                    <pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(data.homework.homework)}</pre>
                `;
                results.classList.remove('hidden');
            }
        } else {
            alert('Error: ' + (data.error || 'Failed to generate homework'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

