// Utility functions for managing best time records.
function saveBestTime(difficulty, time) {
    const bestTime = localStorage.getItem(`best-time-${difficulty}`);
    if (!bestTime || time < bestTime) {
        localStorage.setItem(`best-time-${difficulty}`, time);
    }
}

function getBestTime(difficulty) {
    return localStorage.getItem(`best-time-${difficulty}`) || 'Дані завантажуються...';
}
