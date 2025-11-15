/**
 * Flashcards Page JavaScript
 * Handles flashcard generation and display functionality
 */

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFlashcardsPage();
});

/**
 * Initialize flashcards page event listeners
 */
function initializeFlashcardsPage() {
    // Initialize mobile menu
    initializeMobileMenu();
    
    // Generate flashcards button
    const generateBtn = document.getElementById('generateFlashcardsBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateFlashcards);
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
    
    // Show loading
    const loading = document.getElementById('loading');
    const results = document.getElementById('flashcardResults');
    if (loading) loading.classList.remove('hidden');
    if (results) results.classList.add('hidden');
    
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
            if (results) {
                results.innerHTML = formatFlashcards(data.flashcards);
                results.classList.remove('hidden');
            }
        } else {
            alert('Error: ' + (data.error || 'Failed to generate flashcards'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

/**
 * Format flashcards for display
 */
function formatFlashcards(flashcards) {
    if (!flashcards.cards || !Array.isArray(flashcards.cards)) {
        return '<p>Flashcard data format error</p>';
    }
    
    let html = '';
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
    
    return html;
}

/**
 * Flip flashcard
 */
function flipCard(element) {
    element.classList.toggle('flipped');
}

