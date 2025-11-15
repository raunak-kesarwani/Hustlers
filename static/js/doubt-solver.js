/**
 * Doubt Solver Page JavaScript
 * Handles doubt solving functionality
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDoubtSolverPage();
});

/**
 * Initialize doubt solver page event listeners
 */
function initializeDoubtSolverPage() {
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Solve doubt button
    const solveBtn = document.getElementById('solveDoubtBtn');
    if (solveBtn) {
        solveBtn.addEventListener('click', solveDoubt);
    }
}

/**
 * Solve doubt
 */
async function solveDoubt() {
    const question = document.getElementById('doubtQuestion').value.trim();
    const context = document.getElementById('doubtContext').value.trim();
    
    if (!question) {
        alert('Please enter your question');
        return;
    }
    
    // Show loading
    const loading = document.getElementById('loading');
    const answerBox = document.getElementById('doubtAnswer');
    if (loading) loading.classList.remove('hidden');
    if (answerBox) answerBox.classList.add('hidden');
    
    try {
        const response = await fetch('/doubt-solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                context: context
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (answerBox) {
                answerBox.innerHTML = `
                    <h4>Question:</h4>
                    <p>${escapeHtml(data.answer.question)}</p>
                    <h4 style="margin-top: 1rem;">Answer:</h4>
                    <p>${escapeHtml(data.answer.answer)}</p>
                `;
                answerBox.classList.remove('hidden');
            }
        } else {
            alert('Error: ' + (data.error || 'Failed to get answer'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

