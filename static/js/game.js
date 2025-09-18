// Common game functionality
class GameManager {
    constructor() {
        this.inactivityTimer = null;
        this.inactivityTimeout = 120000; // 2 minutes
        this.setupInactivityTimer();
        this.setupCommonEvents();
    }

    // Inactivity timer management
    setupInactivityTimer() {
        this.resetInactivityTimer();
        
        // Reset timer on user activity
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
            document.addEventListener(event, () => this.resetInactivityTimer(), true);
        });
    }

    resetInactivityTimer() {
        clearTimeout(this.inactivityTimer);
        this.inactivityTimer = setTimeout(() => {
            this.handleInactivity();
        }, this.inactivityTimeout);
    }

    handleInactivity() {
        // Show warning first
        this.showInactivityWarning();
        
        // Reset to welcome screen after additional 30 seconds
        setTimeout(() => {
            window.location.href = '/welcome';
        }, 30000);
    }

    showInactivityWarning() {
        const warning = document.createElement('div');
        warning.className = 'inactivity-warning';
        warning.innerHTML = `
            <div class="warning-content">
                <h3>Are you still there?</h3>
                <p>The game will restart in 30 seconds due to inactivity.</p>
                <button onclick="gameManager.dismissWarning()" class="btn btn-primary">Continue Playing</button>
            </div>
        `;
        document.body.appendChild(warning);
    }

    dismissWarning() {
        const warning = document.querySelector('.inactivity-warning');
        if (warning) {
            warning.remove();
            this.resetInactivityTimer();
        }
    }

    // Common event handlers
    setupCommonEvents() {
        // Prevent right-click context menu
        document.addEventListener('contextmenu', e => e.preventDefault());
        
        // Prevent certain keyboard shortcuts
        document.addEventListener('keydown', e => {
            if (e.key === 'F12' || 
                (e.ctrlKey && e.shiftKey && e.key === 'I') ||
                (e.ctrlKey && e.shiftKey && e.key === 'C') ||
                (e.ctrlKey && e.key === 'u')) {
                e.preventDefault();
            }
        });
    }

    // Navigation helpers
    navigateTo(url, delay = 0) {
        setTimeout(() => {
            window.location.href = url;
        }, delay);
    }

    // Animation helpers
    addRippleEffect(element) {
        element.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    }

    // Form validation helpers
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    validatePhone(phone) {
        const re = /^[\+]?[1-9][\d]{0,15}$/;
        return re.test(phone.replace(/\s/g, ''));
    }

    // API helpers
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    }

    // Local storage helpers
    saveGameData(key, data) {
        try {
            localStorage.setItem(`etciso_${key}`, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save game data:', error);
        }
    }

    getGameData(key) {
        try {
            const data = localStorage.getItem(`etciso_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Failed to get game data:', error);
            return null;
        }
    }

    clearGameData() {
        try {
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('etciso_')) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.error('Failed to clear game data:', error);
        }
    }

    // Timer functionality
    startTimer(duration, callback, updateCallback) {
        let timeLeft = duration;
        const timer = setInterval(() => {
            timeLeft--;
            
            if (updateCallback) {
                updateCallback(timeLeft);
            }
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                if (callback) {
                    callback();
                }
            }
        }, 1000);
        
        return timer;
    }

    // Format time helper
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // Show loading state
    showLoading(message = 'Loading...') {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(loading);
    }

    hideLoading() {
        const loading = document.querySelector('.loading-overlay');
        if (loading) {
            loading.remove();
        }
    }

    // Show error message
    showError(message, duration = 5000) {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        document.body.appendChild(error);
        
        setTimeout(() => {
            error.remove();
        }, duration);
    }

    // Show success message
    showSuccess(message, duration = 3000) {
        const success = document.createElement('div');
        success.className = 'success-message';
        success.textContent = message;
        document.body.appendChild(success);
        
        setTimeout(() => {
            success.remove();
        }, duration);
    }
}

// Initialize game manager
const gameManager = new GameManager();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameManager;
}