/**
 * EduMentor AI - Main JavaScript
 * Handles all frontend interactions and API calls
 */

// Global state
let currentContent = null;
let currentContentId = null;
let selectedContentType = 'notes';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeMobileMenu();
    loadProgress();
    // Initialize field visibility based on default content type
    updateFieldVisibility();
});

/**
 * Update field visibility based on selected content type
 */
function updateFieldVisibility() {
    const numQuestionsGroup = document.getElementById('numQuestionsGroup');
    const languageGroup = document.getElementById('languageGroup');
    const useInternetGroup = document.getElementById('useInternetGroup');
    
    if (selectedContentType === 'quiz') {
        // Show number of questions field for quiz
        if (numQuestionsGroup) numQuestionsGroup.style.display = 'block';
        // Hide language and internet options for quiz (not applicable)
        if (languageGroup) languageGroup.style.display = 'none';
        if (useInternetGroup) useInternetGroup.style.display = 'none';
    } else {
        // Hide number of questions for other content types
        if (numQuestionsGroup) numQuestionsGroup.style.display = 'none';
        // Show language and internet options for other content types
        if (languageGroup) languageGroup.style.display = 'block';
        if (useInternetGroup) useInternetGroup.style.display = 'flex';
    }
}

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Content type selection
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedContentType = this.dataset.type;
            
            // Update field visibility when content type changes
            updateFieldVisibility();
        });
    });

    // Generate content button
    document.getElementById('generateBtn').addEventListener('click', generateContent);
    
    // Generate quiz button
    document.getElementById('generateQuizBtn').addEventListener('click', generateQuiz);
    
    // Generate flashcards button
    document.getElementById('generateFlashcardsBtn').addEventListener('click', generateFlashcards);
    
    // Solve doubt button
    document.getElementById('solveDoubtBtn').addEventListener('click', solveDoubt);
    
    // Teacher tools
    document.getElementById('generateLessonPlanBtn').addEventListener('click', generateLessonPlan);
    document.getElementById('generateHomeworkBtn').addEventListener('click', generateHomework);
    
    // Export buttons
    document.querySelectorAll('.btn-export').forEach(btn => {
        btn.addEventListener('click', function() {
            exportContent(this.dataset.format);
        });
    });
}

/**
 * Generate learning content
 */
async function generateContent() {
    const topic = document.getElementById('topic').value.trim();
    const difficulty = document.getElementById('difficulty').value;
    const language = document.getElementById('language').value;
    // Check if user wants to generate from internet sources
    const useInternet = document.getElementById('useInternet') ? document.getElementById('useInternet').checked : false;
    // Get number of questions for quiz
    const numQuestions = selectedContentType === 'quiz' ? 
        (parseInt(document.getElementById('numQuestions').value) || 10) : 10;
    
    if (!topic) {
        alert('Please enter a topic');
        return;
    }
    
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    try {
        // Build request body
        const requestBody = {
            topic: topic,
            content_type: selectedContentType,
            difficulty: difficulty,
            language: language,
            use_internet: useInternet
        };
        
        // Add number of questions for quiz
        if (selectedContentType === 'quiz') {
            requestBody.num_questions = numQuestions;
        }
        
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentContent = data.content;
            currentContentId = data.content_id;
            displayContent(data.content);
        } else {
            alert('Error: ' + (data.error || 'Failed to generate content'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

/**
 * Display generated content
 */
function displayContent(content) {
    const display = document.getElementById('contentDisplay');
    const results = document.getElementById('results');
    
    // Format content based on type
    let html = '';
    
    if (content.type === 'quiz') {
        // Handle quiz display
        html = formatQuiz(content);
    } else if (content.type === 'flashcards') {
        // Handle flashcards display
        html = formatFlashcards(content);
    } else {
        // Regular content
        const contentText = content.content || content.script || content.description || JSON.stringify(content);
        html = `<h4>${content.topic || 'Generated Content'}</h4>`;
        
        // Show if generated from internet
        if (content.generated_from_internet) {
            html += '<p style="color: #10b981; font-size: 0.875rem; margin-bottom: 1rem;">✓ Generated from internet sources</p>';
        }
        
        html += `<div style="white-space: pre-wrap; line-height: 1.6;">${escapeHtml(contentText)}</div>`;
        
        // Show sources if available
        if (content.sources && content.sources.length > 0) {
            html += '<div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">';
            html += '<h5 style="margin-bottom: 0.5rem;">Sources:</h5>';
            html += '<ul style="list-style: none; padding: 0;">';
            content.sources.forEach(source => {
                if (source) {
                    html += `<li style="margin-bottom: 0.5rem;"><a href="${escapeHtml(source)}" target="_blank" style="color: #3b82f6; text-decoration: underline;">${escapeHtml(source)}</a></li>`;
                }
            });
            html += '</ul></div>';
        }
    }
    
    display.innerHTML = html;
    results.classList.remove('hidden');
}

/**
 * Format quiz for display
 */
function formatQuiz(quiz) {
    if (!quiz.questions || !Array.isArray(quiz.questions)) {
        return '<p>Quiz data format error</p>';
    }
    
    // Display the topic at the top to confirm questions are about the entered topic
    const topic = quiz.topic || 'the selected topic';
    let html = `<div class="quiz-container">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; text-align: center;">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem;">📚 Quiz: ${escapeHtml(topic)}</h3>
            <p style="margin: 0; opacity: 0.9; font-size: 0.95rem;">${quiz.questions.length} question${quiz.questions.length !== 1 ? 's' : ''} about ${escapeHtml(topic)}</p>
        </div>`;
    
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
    html += '</div>';
    
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

/**
 * Format flashcards for display
 */
function formatFlashcards(flashcards) {
    if (!flashcards.cards || !Array.isArray(flashcards.cards)) {
        return '<p>Flashcard data format error</p>';
    }
    
    let html = '<div class="flashcard-container">';
    flashcards.cards.forEach((card, index) => {
        html += `
            <div class="flashcard" onclick="flipCard(this)">
                <div class="flashcard-front">
                    <h4>${escapeHtml(card.front)}</h4>
                    <p style="margin-top: 1rem; color: #6b7280;">Click to flip</p>
                </div>
                <div class="flashcard-back">
                    <h4>Answer:</h4>
                    <p>${escapeHtml(card.back)}</p>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    return html;
}

/**
 * Flip flashcard
 */
function flipCard(element) {
    element.classList.toggle('flipped');
}

/**
 * Generate quiz
 */
async function generateQuiz() {
    const topic = document.getElementById('quizTopic').value.trim();
    const numQuestions = parseInt(document.getElementById('numQuestions').value) || 10;
    
    if (!topic) {
        alert('Please enter a topic for the quiz');
        return;
    }
    
    const difficulty = document.getElementById('difficulty').value;
    
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
            const quizContainer = document.getElementById('quizResults');
            quizContainer.innerHTML = formatQuiz(data.quiz);
            quizContainer.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Failed to generate quiz'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

/**
 * Generate flashcards
 */
async function generateFlashcards() {
    const topic = document.getElementById('flashcardTopic').value.trim();
    const numCards = parseInt(document.getElementById('numCards').value) || 20;
    
    if (!topic) {
        alert('Please enter a topic for flashcards');
        return;
    }
    
    try {
        const response = await fetch('/flashcards', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                num_cards: numCards
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const flashcardContainer = document.getElementById('flashcardResults');
            flashcardContainer.innerHTML = formatFlashcards(data.flashcards);
            flashcardContainer.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Failed to generate flashcards'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
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
            const answerBox = document.getElementById('doubtAnswer');
            answerBox.innerHTML = `
                <h4>Question:</h4>
                <p>${escapeHtml(data.answer.question)}</p>
                <h4 style="margin-top: 1rem;">Answer:</h4>
                <p>${escapeHtml(data.answer.answer)}</p>
            `;
            answerBox.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Failed to get answer'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
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
            const resultsDiv = document.getElementById('teacherResults');
            resultsDiv.innerHTML = `
                <h3>Lesson Plan: ${escapeHtml(topic)}</h3>
                <pre>${escapeHtml(data.lesson_plan.plan)}</pre>
            `;
            resultsDiv.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Failed to generate lesson plan'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
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
            const resultsDiv = document.getElementById('teacherResults');
            resultsDiv.innerHTML = `
                <h3>Homework: ${escapeHtml(topic)}</h3>
                <pre>${escapeHtml(data.homework.homework)}</pre>
            `;
            resultsDiv.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.error || 'Failed to generate homework'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

/**
 * Export content
 */
async function exportContent(format) {
    if (!currentContent && !currentContentId) {
        alert('No content to export. Please generate content first.');
        return;
    }
    
    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_id: currentContentId,
                format: format,
                content: currentContent
            })
        });
        
        if (response.ok) {
            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `edumentor_export.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            alert('Error: ' + (data.error || 'Failed to export'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during export.');
    }
}

/**
 * Load progress
 */
async function loadProgress() {
    try {
        const response = await fetch('/progress');
        const data = await response.json();
        
        if (data.success && data.progress.length > 0) {
            const progressDisplay = document.getElementById('progressDisplay');
            let html = '';
            data.progress.forEach(item => {
                html += `
                    <div class="progress-item">
                        <div>
                            <strong>${escapeHtml(item.topic)}</strong>
                            <p style="color: #6b7280; margin-top: 0.25rem;">Difficulty: ${item.difficulty}</p>
                        </div>
                        <div>
                            <strong>Score: ${item.score}%</strong>
                        </div>
                    </div>
                `;
            });
            progressDisplay.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading progress:', error);
    }
}

/**
 * Initialize mobile menu toggle functionality
 */
function initializeMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuToggle && navLinks) {
        // Toggle menu on button click
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        
        // Close menu when clicking on a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navLinks.contains(event.target);
            const isClickOnToggle = mobileMenuToggle.contains(event.target);
            
            if (!isClickInsideNav && !isClickOnToggle && navLinks.classList.contains('active')) {
                mobileMenuToggle.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

