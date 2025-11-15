/**
 * Lesson Plan Page JavaScript
 * Handles lesson plan generation functionality
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeLessonPlanPage();
});

/**
 * Initialize lesson plan page event listeners
 */
function initializeLessonPlanPage() {
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Generate lesson plan button
    const generateBtn = document.getElementById('generateLessonPlanBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateLessonPlan);
    }
}

/**
 * Generate lesson plan
 */
async function generateLessonPlan() {
    const topic = document.getElementById('lessonTopic').value.trim();
    const duration = parseInt(document.getElementById('lessonDuration').value) || 60;
    const gradeLevel = document.getElementById('gradeLevel').value;
    
    if (!topic) {
        alert('Please enter a topic');
        return;
    }
    
    // Show loading
    const loading = document.getElementById('loading');
    const results = document.getElementById('lessonPlanResults');
    if (loading) loading.classList.remove('hidden');
    if (results) results.classList.add('hidden');
    
    try {
        const response = await fetch('/lesson-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                duration: duration,
                grade_level: gradeLevel
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (results) {
                results.innerHTML = `
                    <h3>Lesson Plan: ${escapeHtml(topic)}</h3>
                    <pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(data.lesson_plan.plan)}</pre>
                `;
                results.classList.remove('hidden');
            }
        } else {
            alert('Error: ' + (data.error || 'Failed to generate lesson plan'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

