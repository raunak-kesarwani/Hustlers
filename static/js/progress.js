/**
 * Progress Page JavaScript
 * Handles progress tracking and display functionality
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeProgressPage();
});

/**
 * Initialize progress page event listeners
 */
function initializeProgressPage() {
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Load progress on page load
    loadProgress();
    
    // Update progress button
    const updateBtn = document.getElementById('updateProgressBtn');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateProgress);
    }
}

/**
 * Load progress from server
 */
async function loadProgress() {
    const progressDisplay = document.getElementById('progressDisplay');
    
    if (!progressDisplay) return;
    
    try {
        const response = await fetch('/progress');
        const data = await response.json();
        
        if (data.success) {
            if (data.progress && data.progress.length > 0) {
                let html = '';
                data.progress.forEach(item => {
                    html += `
                        <div class="progress-item">
                            <div>
                                <strong>${escapeHtml(item.topic)}</strong>
                                <p style="color: #6b7280; margin-top: 0.25rem;">Difficulty: ${item.difficulty}</p>
                                ${item.completed_at ? `<p style="color: #6b7280; font-size: 0.9rem;">Completed: ${new Date(item.completed_at).toLocaleDateString()}</p>` : ''}
                            </div>
                            <div>
                                <strong>Score: ${item.score}%</strong>
                            </div>
                        </div>
                    `;
                });
                progressDisplay.innerHTML = html;
            } else {
                progressDisplay.innerHTML = '<p>No progress recorded yet. Complete quizzes or activities to track your progress!</p>';
            }
        } else {
            progressDisplay.innerHTML = '<p>Error loading progress. Please try again later.</p>';
        }
    } catch (error) {
        console.error('Error loading progress:', error);
        progressDisplay.innerHTML = '<p>Error loading progress. Please try again later.</p>';
    }
}

/**
 * Update progress
 */
async function updateProgress() {
    const topic = document.getElementById('progressTopic').value.trim();
    const score = parseFloat(document.getElementById('progressScore').value) || 0;
    const difficulty = document.getElementById('progressDifficulty').value;
    
    if (!topic) {
        alert('Please enter a topic');
        return;
    }
    
    if (score < 0 || score > 100) {
        alert('Score must be between 0 and 100');
        return;
    }
    
    try {
        const response = await fetch('/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                score: score,
                difficulty: difficulty
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear form
            document.getElementById('progressTopic').value = '';
            document.getElementById('progressScore').value = '0';
            document.getElementById('progressDifficulty').value = 'medium';
            
            // Reload progress
            loadProgress();
            
            alert('Progress updated successfully!');
        } else {
            alert('Error: ' + (data.error || 'Failed to update progress'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

