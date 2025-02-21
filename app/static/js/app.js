let currentIndex = 0;
let words = [];
let typingMode = false;
let streakCount = 0;
let correctCharsTyped = 0;
let totalCharsTyped = 0;
let filteredWords = []; // New array to hold search results

document.addEventListener('DOMContentLoaded', () => {
    loadWords();
    setupEventListeners();
    updateAccuracy();
});

function setupEventListeners() {
    document.getElementById('previous').addEventListener('click', previousWord);
    document.getElementById('next').addEventListener('click', nextWord);
    document.getElementById('remove').addEventListener('click', removeWord);
    document.getElementById('download').addEventListener('click', downloadWords);
    document.getElementById('toggleTyping').addEventListener('click', toggleTypingMode);
    document.getElementById('pronounce-icon').addEventListener('click', pronounceWord);
    document.getElementById('typingInput').addEventListener('input', checkTyping);
    document.getElementById('languageSelector').addEventListener('change', changeLanguage);
    document.getElementById('searchInput').addEventListener('input', handleSearch); // New search handler
}

async function loadWords() {
    try {
        const response = await fetch('/api/words');
        words = await response.json();
        filteredWords = [...words]; // Initialize filtered words
        if (words.length > 0) {
            currentIndex = 0;
            updateWordDisplay();
        } else {
            document.getElementById('word').textContent = 'No words available. Add some!';
            document.getElementById('sentence').textContent = '';
        }
        updateWordCount(); // Update the word count display
    } catch (error) {
        console.error('Failed to load words:', error);
        document.getElementById('word').textContent = 'Failed to load words.';
        document.getElementById('sentence').textContent = 'Check the console for errors.';
    }
}

function updateWordCount() {
    const totalCount = words.length;
    const filteredCount = filteredWords.length;
    const countText = filteredCount === totalCount ? 
        `Total words: ${totalCount}` : 
        `Showing ${filteredCount} of ${totalCount} words`;
    document.getElementById('wordCount').textContent = countText;
}

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    if (searchTerm === '') {
        filteredWords = [...words];
    } else {
        filteredWords = words.filter(word => 
            word.word.toLowerCase().includes(searchTerm) || 
            word.sentence.toLowerCase().includes(searchTerm)
        );
    }
    currentIndex = 0; // Reset to first matching word
    updateWordDisplay();
    updateWordCount();
}

function updateWordDisplay() {
    if (filteredWords.length === 0) {
        document.getElementById('word').textContent = 'No matching words';
        document.getElementById('sentence').textContent = '';
        return;
    }

    const currentWord = filteredWords[currentIndex];
    document.getElementById('word').textContent = currentWord.word;
    document.getElementById('sentence').textContent = currentWord.sentence;
}

function previousWord() {
    if (filteredWords.length === 0) return;
    currentIndex = (currentIndex - 1 + filteredWords.length) % filteredWords.length;
    updateWordDisplay();
    resetTyping();
}

function nextWord() {
    if (filteredWords.length === 0) return;
    currentIndex = (currentIndex + 1) % filteredWords.length;
    updateWordDisplay();
    resetTyping();
}

async function removeWord() {
    if (words.length === 0) return;

    const confirmed = confirm(`Are you sure you want to remove the word "${words[currentIndex].word}"?`);
    if (!confirmed) return;

    try {
        const response = await fetch(`/api/words/${currentIndex}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            words.splice(currentIndex, 1);
            // Adjust currentIndex if deleting the last word
            if (currentIndex >= words.length && words.length > 0) {
                currentIndex = words.length - 1;
            }
            loadWords(); // Reload words to update the display
            showMessage("Word removed successfully!");
        } else {
            const errorData = await response.json();
            showMessage(`Failed to remove word: ${errorData.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error removing word:', error);
        showMessage("Failed to remove word. Check console for errors.");
    }
}


async function downloadWords() {
    try {
        const response = await fetch('/api/download');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'words.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Download failed:', error);
        showMessage('Download failed.  Check console for details.');
    }
}


function toggleTypingMode() {
    typingMode = !typingMode;
    const typingContainer = document.getElementById('typingContainer');
    typingContainer.classList.toggle('hidden', !typingMode);
    const typingInput = document.getElementById('typingInput');

    if (typingMode) {
        typingInput.focus();  // Automatically focus the input field
        typingInput.value = ''; // Clear the input field
        document.getElementById('feedback').textContent = ''; // Clear feedback
    }

    // Optionally, update the button's appearance or text
    const toggleButton = document.getElementById('toggleTyping');
    toggleButton.innerHTML = typingMode ? '<i class="fas fa-book"></i>' : '<i class="fas fa-keyboard"></i>'; // Example: change icon
    toggleButton.title = typingMode ? 'Exit Typing Practice' : 'Enter Typing Practice'; // Example: change title
}

function pronounceWord() {
    if (words.length === 0) return;
    const word = document.getElementById('word').textContent;
    const language = document.getElementById('languageSelector').value;
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = language;
    speechSynthesis.speak(utterance);
}

function checkTyping() {
    const input = document.getElementById('typingInput').value;
    const currentWord = words[currentIndex].word;
    const feedback = document.getElementById('feedback');

    totalCharsTyped++;

    if (currentWord.startsWith(input)) {
        feedback.textContent = "Keep going...";
        feedback.className = 'correct';
        correctCharsTyped++; // Increment correct chars typed

        if (input === currentWord) {
            streakCount++;
            feedback.textContent = "Correct! Next word!";
            feedback.className = 'correct';
            updateStreak();
            setTimeout(nextWord, 1000);
            resetTyping();
        }
    } else {
        feedback.textContent = "Incorrect. Try again.";
        feedback.className = 'incorrect';
        streakCount = 0;
        updateStreak();
    }
    updateAccuracy(); // Update accuracy on each keypress
}

function resetTyping() {
    document.getElementById('typingInput').value = '';
    document.getElementById('feedback').textContent = '';
}

function updateStreak() {
    document.getElementById('streak').textContent = `Streak: ${streakCount}`;
}

function updateAccuracy() {
    let accuracy = totalCharsTyped > 0 ? (correctCharsTyped / totalCharsTyped) * 100 : 0;
    document.getElementById('accuracy').textContent = `Accuracy: ${accuracy.toFixed(2)}%`;
}

function showMessage(message, duration = 3000) {
    const messageArea = document.getElementById('message');
    messageArea.textContent = message;
    messageArea.style.display = 'block';

    setTimeout(() => {
        messageArea.style.display = 'none';
    }, duration);
}


function changeLanguage() {
    updateWordDisplay(); // Re-render the word display
}
