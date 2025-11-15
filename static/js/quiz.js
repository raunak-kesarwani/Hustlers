/**
 * Quiz Page JavaScript
 * Handles quiz generation and display functionality
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeQuizPage();
});

/**
 * Initialize quiz page event listeners
 */
function initializeQuizPage() {
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Generate quiz button
    const generateBtn = document.getElementById('generateQuizBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateQuiz);
    }
}

/**
 * Generate quiz
 */
async function generateQuiz() {
    const topic = document.getElementById('quizTopic').value.trim();
    const numQuestions = parseInt(document.getElementById('numQuestions').value) || 10;
    const difficulty = document.getElementById('difficulty').value;
    
    if (!topic) {
        alert('Please enter a topic for the quiz');
        return;
    }
    
    // Show loading
    const loading = document.getElementById('loading');
    const results = document.getElementById('quizResults');
    if (loading) loading.classList.remove('hidden');
    if (results) results.classList.add('hidden');
    
    try {
        const response = await fetch('/quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                num_questions: numQuestions,
                difficulty: difficulty
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (results) {
                results.innerHTML = formatQuiz(data.quiz);
                results.classList.remove('hidden');
            }
        } else {
            alert('Error: ' + (data.error || 'Failed to generate quiz'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

/**
 * Format quiz for display
 */
function formatQuiz(quiz) {
    if (!quiz.questions || !Array.isArray(quiz.questions)) {
        return '<p>Quiz data format error</p>';
    }
    
    let html = '';
    quiz.questions.forEach((q, index) => {
        html += `
            <div class="quiz-question">
                <h4>Question ${index + 1}: ${escapeHtml(q.question)}</h4>
                <ul class="quiz-options">
                    ${q.options.map((opt, i) => `
                        <li data-correct="${i === q.correct}">
                            ${escapeHtml(opt)}
                        </li>
                    `).join('')}
                </ul>
                <div class="quiz-explanation hidden" id="explanation-${index}">
                    <strong>Explanation:</strong> ${escapeHtml(q.explanation || 'No explanation provided')}
                </div>
            </div>
        `;
    });
    
    // Add click handlers for quiz options
    setTimeout(() => {
        document.querySelectorAll('.quiz-options li').forEach(li => {
            li.addEventListener('click', function() {
                const isCorrect = this.dataset.correct === 'true';
                const questionDiv = this.closest('.quiz-question');
                const options = questionDiv.querySelectorAll('.quiz-options li');
                const explanation = questionDiv.querySelector('.quiz-explanation');
                
                // Mark all options
                options.forEach(opt => {
                    opt.classList.remove('correct', 'incorrect');
                    if (opt.dataset.correct === 'true') {
                        opt.classList.add('correct');
                    } else if (opt === this && !isCorrect) {
                        opt.classList.add('incorrect');
                    }
                });
                
                // Show explanation
                if (explanation) {
                    explanation.classList.remove('hidden');
                }
            });
        });
    }, 100);
    
    return html;
}

