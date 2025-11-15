/**
 * Quiz Page JavaScript
 * Handles quiz generation and display functionality
 */

// Global variables to store quiz data and current question index
let currentQuiz = null;
let currentQuestionIndex = 0;
let userAnswers = {}; // Store user's answers for each question
let skippedQuestions = []; // Track indices of skipped questions
let isReviewingSkipped = false; // Flag to know if we're reviewing skipped questions

// Timer variables for quiz timing
let quizTimer = null; // Timer interval reference
let timeRemaining = 0; // Time remaining in seconds
let totalTimeLimit = 0; // Total time limit in seconds (0 = no limit)

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
    const quizTimeMinutes = parseInt(document.getElementById('quizTime').value) || 0;
    
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
            // Store quiz data globally
            currentQuiz = data.quiz;
            currentQuestionIndex = 0;
            userAnswers = {}; // Reset answers
            skippedQuestions = []; // Reset skipped questions
            isReviewingSkipped = false; // Reset review flag
            
            // Initialize timer if time limit is set
            totalTimeLimit = quizTimeMinutes * 60; // Convert minutes to seconds
            if (totalTimeLimit > 0) {
                timeRemaining = totalTimeLimit;
                startQuizTimer();
            } else {
                timeRemaining = 0;
                stopQuizTimer(); // Clear any existing timer
            }
            
            if (results) {
                // Display first question
                results.innerHTML = formatQuiz(currentQuiz, 0);
                results.classList.remove('hidden');
                
                // Set up event listeners for buttons
                setupQuizNavigation();
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
 * Format quiz for display - shows one question at a time
 */
function formatQuiz(quiz, questionIndex) {
    if (!quiz.questions || !Array.isArray(quiz.questions)) {
        return '<p>Quiz data format error</p>';
    }
    
    if (questionIndex < 0 || questionIndex >= quiz.questions.length) {
        return '<p>Question not found</p>';
    }
    
    const question = quiz.questions[questionIndex];
    const totalQuestions = quiz.questions.length;
    
    // Determine if this is the last question in the current phase
    // If reviewing skipped questions, check if it's the last skipped question
    // Otherwise, check if it's the last question in the main quiz
    let isLastQuestion;
    if (isReviewingSkipped) {
        isLastQuestion = skippedQuestions.indexOf(questionIndex) === skippedQuestions.length - 1;
    } else {
        isLastQuestion = questionIndex === totalQuestions - 1;
    }
    
    // Build progress text - show different text if reviewing skipped questions
    let progressText;
    if (isReviewingSkipped) {
        const skippedIndex = skippedQuestions.indexOf(questionIndex) + 1;
        progressText = `Reviewing Skipped Questions: ${skippedIndex} of ${skippedQuestions.length}`;
    } else {
        progressText = `Question ${questionIndex + 1} of ${totalQuestions}`;
    }
    
    // Build timer display HTML if timer is active
    let timerHtml = '';
    if (totalTimeLimit > 0 && !isReviewingSkipped) {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        // Add warning class if time is running low (less than 1 minute)
        const timerClass = timeRemaining < 60 ? 'timer-warning' : '';
        timerHtml = `<div class="quiz-timer ${timerClass}">
            <span class="timer-icon">⏱️</span>
            <span class="timer-text">Time Remaining: <strong>${timeString}</strong></span>
        </div>`;
    }
    
    // Build HTML for current question
    let html = `
        <div class="quiz-progress">
            <p>${progressText}</p>
            ${timerHtml}
        </div>
        <div class="quiz-question" data-question-index="${questionIndex}">
            <h4>Question ${questionIndex + 1}: ${escapeHtml(question.question)}</h4>
            <ul class="quiz-options">
                ${question.options.map((opt, i) => {
                    // Check if this option was previously selected
                    const isSelected = userAnswers[questionIndex] === i;
                    return `
                        <li data-correct="${i === question.correct}" 
                            data-option-index="${i}"
                            ${isSelected ? 'class="selected"' : ''}>
                            ${escapeHtml(opt)}
                        </li>
                    `;
                }).join('')}
            </ul>
            <div class="quiz-explanation hidden" id="explanation-${questionIndex}">
                <strong>Explanation:</strong> ${escapeHtml(question.explanation || 'No explanation provided')}
            </div>
        </div>
        <div class="quiz-navigation">
    `;
    
    // Add Skip button (only show during main quiz, not when reviewing skipped questions)
    if (!isReviewingSkipped) {
        html += `<button id="skipBtn" class="btn-secondary">Skip</button>`;
    }
    
    // Add Next button (show for all questions except the last one)
    if (!isLastQuestion) {
        html += `<button id="nextBtn" class="btn-primary">Next</button>`;
    }
    
    // Add Confirm button (show on last question, or show on all questions if preferred)
    html += `<button id="confirmBtn" class="btn-primary">${isLastQuestion ? (isReviewingSkipped ? 'View Results' : 'Submit Quiz') : 'Confirm Answer'}</button>`;
    
    html += `</div>`;
    
    return html;
}

/**
 * Set up event listeners for quiz navigation buttons
 */
function setupQuizNavigation() {
    // Skip button - skip current question and move to next
    const skipBtn = document.getElementById('skipBtn');
    if (skipBtn) {
        skipBtn.addEventListener('click', function() {
            // Add current question to skipped list if not already there
            if (skippedQuestions.indexOf(currentQuestionIndex) === -1) {
                skippedQuestions.push(currentQuestionIndex);
            }
            
            // Move to next question
            moveToNextQuestion();
        });
    }
    
    // Next button - move to next question
    const nextBtn = document.getElementById('nextBtn');
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            // Save current answer if selected (but don't require it)
            const selectedOption = document.querySelector('.quiz-options li.selected');
            if (selectedOption) {
                const optionIndex = parseInt(selectedOption.dataset.optionIndex);
                userAnswers[currentQuestionIndex] = optionIndex;
            }
            
            // Move to next question
            moveToNextQuestion();
        });
    }
    
    // Confirm button - confirm answer and show result, or submit quiz
    const confirmBtn = document.getElementById('confirmBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            // Check if answer has already been confirmed
            const questionDiv = document.querySelector('.quiz-question');
            const isAlreadyConfirmed = questionDiv.classList.contains('answered');
            
            // If already confirmed, move to next question
            if (isAlreadyConfirmed) {
                // If reviewing skipped questions, check if there are more
                if (isReviewingSkipped) {
                    const currentSkippedIndex = skippedQuestions.indexOf(currentQuestionIndex);
                    if (currentSkippedIndex < skippedQuestions.length - 1) {
                        // Move to next skipped question
                        currentQuestionIndex = skippedQuestions[currentSkippedIndex + 1];
                        const results = document.getElementById('quizResults');
                        if (results) {
                            results.innerHTML = formatQuiz(currentQuiz, currentQuestionIndex);
                            setupQuizNavigation();
                        }
                        return;
                    } else {
                        // Last skipped question, show results
                        showQuizResults();
                        return;
                    }
                } else if (currentQuestionIndex < currentQuiz.questions.length - 1) {
                    // Normal flow - move to next question
                    currentQuestionIndex++;
                    const results = document.getElementById('quizResults');
                    if (results) {
                        results.innerHTML = formatQuiz(currentQuiz, currentQuestionIndex);
                        setupQuizNavigation();
                    }
                    return;
                }
            }
            
            const selectedOption = document.querySelector('.quiz-options li.selected');
            
            if (!selectedOption) {
                alert('Please select an answer before confirming.');
                return;
            }
            
            // Save the answer
            const optionIndex = parseInt(selectedOption.dataset.optionIndex);
            userAnswers[currentQuestionIndex] = optionIndex;
            
            // Mark question as answered
            questionDiv.classList.add('answered');
            
            // Show correct/incorrect feedback
            const options = questionDiv.querySelectorAll('.quiz-options li');
            const explanation = questionDiv.querySelector('.quiz-explanation');
            const isCorrect = selectedOption.dataset.correct === 'true';
            
            // Mark all options
            options.forEach(opt => {
                opt.classList.remove('correct', 'incorrect');
                if (opt.dataset.correct === 'true') {
                    opt.classList.add('correct');
                } else if (opt === selectedOption && !isCorrect) {
                    opt.classList.add('incorrect');
                }
            });
            
            // Show explanation
            if (explanation) {
                explanation.classList.remove('hidden');
            }
            
            // Update button text and behavior based on current state
            if (isReviewingSkipped) {
                // We're reviewing skipped questions
                const currentSkippedIndex = skippedQuestions.indexOf(currentQuestionIndex);
                const isLastSkipped = currentSkippedIndex === skippedQuestions.length - 1;
                
                if (isLastSkipped) {
                    confirmBtn.textContent = 'View Results';
                    confirmBtn.onclick = function() {
                        showQuizResults();
                    };
                } else {
                    confirmBtn.textContent = 'Next Question';
                    // Hide the Next button since Confirm now handles navigation
                    const nextBtn = document.getElementById('nextBtn');
                    if (nextBtn) {
                        nextBtn.style.display = 'none';
                    }
                }
            } else {
                // Normal quiz flow
                if (currentQuestionIndex < currentQuiz.questions.length - 1) {
                    confirmBtn.textContent = 'Next Question';
                    // Hide the Next button since Confirm now handles navigation
                    const nextBtn = document.getElementById('nextBtn');
                    if (nextBtn) {
                        nextBtn.style.display = 'none';
                    }
                } else {
                    // Last question of main quiz - check if there are skipped questions
                    if (skippedQuestions.length > 0) {
                        confirmBtn.textContent = 'Review Skipped Questions';
                        confirmBtn.onclick = function() {
                            startReviewingSkippedQuestions();
                        };
                    } else {
                        confirmBtn.textContent = 'View Results';
                        confirmBtn.onclick = function() {
                            showQuizResults();
                        };
                    }
                }
            }
        });
    }
    
    // Add click handlers for quiz options with smooth highlighting microinteraction
    // The CSS transitions handle the smooth animation when options are selected/deselected
    setTimeout(() => {
        document.querySelectorAll('.quiz-options li').forEach(li => {
            li.addEventListener('click', function() {
                // Remove selected class from all options
                // CSS transition will smoothly animate the deselection
                const questionDiv = this.closest('.quiz-question');
                const options = questionDiv.querySelectorAll('.quiz-options li');
                options.forEach(opt => opt.classList.remove('selected'));
                
                // Add selected class to clicked option
                // CSS will animate the selection with pulse effect and gradient background
                this.classList.add('selected');
            });
        });
    }, 100);
}

/**
 * Move to the next question in the quiz
 * Handles both main quiz and skipped questions review
 */
function moveToNextQuestion() {
    const results = document.getElementById('quizResults');
    if (!results || !currentQuiz) {
        return;
    }
    
    // If we're reviewing skipped questions
    if (isReviewingSkipped) {
        // Find the current position in skipped questions array
        const currentSkippedIndex = skippedQuestions.indexOf(currentQuestionIndex);
        
        // If there's a next skipped question, move to it
        if (currentSkippedIndex < skippedQuestions.length - 1) {
            currentQuestionIndex = skippedQuestions[currentSkippedIndex + 1];
            results.innerHTML = formatQuiz(currentQuiz, currentQuestionIndex);
            setupQuizNavigation();
        } else {
            // No more skipped questions, show results
            showQuizResults();
        }
    } else {
        // Normal quiz flow - move to next question
        if (currentQuestionIndex < currentQuiz.questions.length - 1) {
            currentQuestionIndex++;
            results.innerHTML = formatQuiz(currentQuiz, currentQuestionIndex);
            setupQuizNavigation();
        } else {
            // Reached end of main quiz - check for skipped questions
            if (skippedQuestions.length > 0) {
                // Start reviewing skipped questions
                startReviewingSkippedQuestions();
            } else {
                // No skipped questions, show results directly
                showQuizResults();
            }
        }
    }
}

/**
 * Start reviewing skipped questions
 * Shows skipped questions one by one before showing results
 */
function startReviewingSkippedQuestions() {
    if (!skippedQuestions || skippedQuestions.length === 0) {
        // No skipped questions, show results directly
        showQuizResults();
        return;
    }
    
    // Set flag to indicate we're reviewing skipped questions
    isReviewingSkipped = true;
    
    // Start with the first skipped question
    currentQuestionIndex = skippedQuestions[0];
    
    const results = document.getElementById('quizResults');
    if (results) {
        results.innerHTML = formatQuiz(currentQuiz, currentQuestionIndex);
        setupQuizNavigation();
    }
}

/**
 * Start the quiz timer
 * Updates every second and auto-submits when time runs out
 */
function startQuizTimer() {
    // Clear any existing timer first
    stopQuizTimer();
    
    // Update timer every second
    quizTimer = setInterval(function() {
        if (timeRemaining > 0) {
            timeRemaining--;
            updateTimerDisplay();
            
            // Show warning when less than 1 minute remains
            if (timeRemaining === 60) {
                // Update timer display with warning class
                updateTimerDisplay();
            }
            
            // Auto-submit when time runs out
            if (timeRemaining === 0) {
                stopQuizTimer();
                alert('Time is up! Your quiz will be submitted automatically.');
                // Save any current answer before submitting
                const selectedOption = document.querySelector('.quiz-options li.selected');
                if (selectedOption) {
                    const optionIndex = parseInt(selectedOption.dataset.optionIndex);
                    userAnswers[currentQuestionIndex] = optionIndex;
                }
                // Show results
                showQuizResults();
            }
        } else {
            stopQuizTimer();
        }
    }, 1000);
    
    // Initial display update
    updateTimerDisplay();
}

/**
 * Stop the quiz timer
 */
function stopQuizTimer() {
    if (quizTimer) {
        clearInterval(quizTimer);
        quizTimer = null;
    }
}

/**
 * Update the timer display in the quiz progress section
 */
function updateTimerDisplay() {
    if (totalTimeLimit > 0 && !isReviewingSkipped) {
        const timerElement = document.querySelector('.quiz-timer');
        if (timerElement) {
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Update timer text
            const timerText = timerElement.querySelector('.timer-text');
            if (timerText) {
                timerText.innerHTML = `Time Remaining: <strong>${timeString}</strong>`;
            }
            
            // Add/remove warning class based on time remaining
            if (timeRemaining < 60) {
                timerElement.classList.add('timer-warning');
            } else {
                timerElement.classList.remove('timer-warning');
            }
        }
    }
}

/**
 * Show quiz results summary with detailed review of all questions
 * Shows previously asked questions, correct answers, and wrong answers
 */
function showQuizResults() {
    // Stop timer when showing results
    stopQuizTimer();
    
    if (!currentQuiz || !currentQuiz.questions) {
        return;
    }
    
    let correctCount = 0;
    let totalQuestions = currentQuiz.questions.length;
    
    // Calculate score by checking each answer
    currentQuiz.questions.forEach((question, index) => {
        if (userAnswers[index] === question.correct) {
            correctCount++;
        }
    });
    
    const score = Math.round((correctCount / totalQuestions) * 100);
    
    // Build results HTML with enhanced review section
    let html = `
        <div class="quiz-results">
            <h3>Quiz Results</h3>
            <div class="score-display">
                <p class="score-text">Your Score: ${correctCount} / ${totalQuestions}</p>
                <p class="score-percentage">${score}%</p>
            </div>
            
            <!-- Detailed Review Section -->
            <div class="quiz-review">
                <h4 class="review-title">📋 Question Review - All Questions with Answers</h4>
                <p class="review-subtitle">Review all questions, your answers, and the correct answers below.</p>
    `;
    
    // Show all questions with detailed answer information
    currentQuiz.questions.forEach((question, index) => {
        const userAnswer = userAnswers[index];
        const isCorrect = userAnswer === question.correct;
        const userAnswerText = userAnswer !== undefined ? question.options[userAnswer] : 'Not answered';
        const correctAnswerText = question.options[question.correct];
        
        // Build question review card
        html += `
            <div class="review-question ${isCorrect ? 'correct-answer' : 'incorrect-answer'}">
                <div class="review-question-header">
                    <h5>Question ${index + 1}: ${escapeHtml(question.question)}</h5>
                    <span class="answer-status ${isCorrect ? 'status-correct' : 'status-incorrect'}">
                        ${isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </span>
                </div>
                
                <div class="review-answer-details">
                    <!-- Show user's answer -->
                    <div class="answer-item ${isCorrect ? 'answer-correct' : 'answer-wrong'}">
                        <strong class="answer-label">Your Answer:</strong>
                        <span class="answer-text">${escapeHtml(userAnswerText)}</span>
                        ${!isCorrect ? '<span class="wrong-indicator">(Wrong)</span>' : ''}
                    </div>
                    
                    <!-- Always show correct answer for clarity -->
                    <div class="answer-item answer-correct-answer">
                        <strong class="answer-label">Correct Answer:</strong>
                        <span class="answer-text">${escapeHtml(correctAnswerText)}</span>
                    </div>
                    
                    <!-- Show explanation -->
                    <div class="answer-explanation">
                        <strong class="explanation-label">Explanation:</strong>
                        <p class="explanation-text">${escapeHtml(question.explanation || 'No explanation provided')}</p>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="quiz-results-actions">
                <button id="restartQuizBtn" class="btn-primary">Take Another Quiz</button>
            </div>
        </div>
    `;
    
    const results = document.getElementById('quizResults');
    if (results) {
        results.innerHTML = html;
        
        // Add event listener for restart button
        const restartBtn = document.getElementById('restartQuizBtn');
        if (restartBtn) {
            restartBtn.addEventListener('click', function() {
                // Reset quiz state
                currentQuiz = null;
                currentQuestionIndex = 0;
                userAnswers = {};
                skippedQuestions = [];
                isReviewingSkipped = false;
                totalTimeLimit = 0;
                timeRemaining = 0;
                stopQuizTimer(); // Stop any running timer
                results.classList.add('hidden');
                results.innerHTML = '';
            });
        }
    }
}

