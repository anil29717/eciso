// Admin Panel JavaScript Functionality
class AdminManager {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.setupAutoRefresh();
    }

    setupEventListeners() {
        // Modal handlers
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-modal]')) {
                this.openModal(e.target.dataset.modal);
            }
            if (e.target.matches('.modal-close') || e.target.matches('.modal-overlay')) {
                this.closeModal();
            }
        });

        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.matches('#addQuestionForm')) {
                e.preventDefault();
                this.handleAddQuestion(e.target);
            }
            if (e.target.matches('#addUserForm')) {
                e.preventDefault();
                this.handleAddUser(e.target);
            }
        });

        // Export buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#exportUsers')) {
                this.exportUsers();
            }
            if (e.target.matches('#exportSessions')) {
                this.exportSessions();
            }
            if (e.target.matches('#exportQuestions')) {
                this.exportQuestions();
            }
        });

        // Search and filter
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.matches('.page-btn')) {
                this.changePage(parseInt(e.target.dataset.page));
            }
        });

        // Delete handlers
        document.addEventListener('click', (e) => {
            if (e.target.matches('.delete-question')) {
                this.deleteQuestion(e.target.dataset.id);
            }
            if (e.target.matches('.delete-user')) {
                this.deleteUser(e.target.dataset.id);
            }
        });

        // Edit handlers
        document.addEventListener('click', (e) => {
            if (e.target.matches('.edit-question')) {
                this.editQuestion(e.target.dataset.id);
            }
            if (e.target.matches('.edit-user')) {
                this.editUser(e.target.dataset.id);
            }
        });
    }

    async loadDashboardData() {
        try {
            this.showLoading('Loading dashboard data...');
            
            const [stats, recentSessions, questions, users] = await Promise.all([
                this.fetchStats(),
                this.fetchRecentSessions(),
                this.fetchQuestions(),
                this.fetchUsers()
            ]);

            this.updateStats(stats);
            this.updateRecentSessions(recentSessions);
            this.updateQuestionsTable(questions);
            this.updateUsersTable(users);
            
            this.hideLoading();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('Failed to load dashboard data');
            this.hideLoading();
        }
    }

    async fetchStats() {
        const response = await fetch('/admin/api/stats');
        return await response.json();
    }

    async fetchRecentSessions() {
        const response = await fetch('/admin/api/recent-sessions');
        return await response.json();
    }

    async fetchQuestions(page = 1, search = '') {
        const response = await fetch(`/admin/api/questions?page=${page}&search=${search}`);
        return await response.json();
    }

    async fetchUsers(page = 1, search = '') {
        const response = await fetch(`/admin/api/users?page=${page}&search=${search}`);
        return await response.json();
    }

    updateStats(stats) {
        document.getElementById('totalUsers').textContent = stats.total_users || 0;
        document.getElementById('totalSessions').textContent = stats.total_sessions || 0;
        document.getElementById('totalQuestions').textContent = stats.total_questions || 0;
        document.getElementById('avgScore').textContent = `${stats.avg_score || 0}%`;
    }

    updateRecentSessions(sessions) {
        const container = document.getElementById('recentSessions');
        if (!container) return;

        container.innerHTML = sessions.map(session => `
            <div class="activity-item">
                <div class="activity-info">
                    <strong>${session.user_name}</strong>
                    <span class="activity-meta">${session.company} - ${session.industry}</span>
                    <span class="activity-time">${this.formatDate(session.created_at)}</span>
                </div>
                <div class="activity-score ${session.is_correct ? 'correct' : 'incorrect'}">
                    ${session.is_correct ? '✓' : '✗'}
                </div>
            </div>
        `).join('');
    }

    updateQuestionsTable(data) {
        const tbody = document.getElementById('questionsTableBody');
        if (!tbody) return;

        tbody.innerHTML = data.questions.map(question => `
            <tr>
                <td>${question.id}</td>
                <td>${question.category}</td>
                <td class="question-text">${question.question_text}</td>
                <td class="correct-answer">${question.correct_answer}</td>
                <td>
                    <button class="btn btn-sm btn-outline edit-question" data-id="${question.id}">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-danger delete-question" data-id="${question.id}">
                        Delete
                    </button>
                </td>
            </tr>
        `).join('');

        this.updatePagination(data.total_pages, data.current_page, 'questions');
    }

    updateUsersTable(data) {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;

        tbody.innerHTML = data.users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.company}</td>
                <td>${user.industry}</td>
                <td>
                    <button class="btn btn-sm btn-outline edit-user" data-id="${user.id}">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-danger delete-user" data-id="${user.id}">
                        Delete
                    </button>
                </td>
            </tr>
        `).join('');

        this.updatePagination(data.total_pages, data.current_page, 'users');
    }

    updatePagination(totalPages, currentPage, type) {
        const container = document.getElementById(`${type}Pagination`);
        if (!container) return;

        let paginationHTML = '';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `<button class="page-btn" data-page="${currentPage - 1}">Previous</button>`;
        }
        
        // Page numbers
        for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
            paginationHTML += `<button class="page-btn ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }
        
        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `<button class="page-btn" data-page="${currentPage + 1}">Next</button>`;
        }
        
        container.innerHTML = paginationHTML;
    }

    async handleAddQuestion(form) {
        try {
            const formData = new FormData(form);
            const questionData = {
                category: formData.get('category'),
                question_text: formData.get('question_text'),
                option_a: formData.get('option_a'),
                option_b: formData.get('option_b'),
                option_c: formData.get('option_c'),
                option_d: formData.get('option_d'),
                correct_answer: formData.get('correct_answer'),
                explanation: formData.get('explanation')
            };

            const response = await fetch('/admin/api/questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(questionData)
            });

            if (response.ok) {
                this.showSuccess('Question added successfully!');
                this.closeModal();
                form.reset();
                this.loadDashboardData();
            } else {
                throw new Error('Failed to add question');
            }
        } catch (error) {
            console.error('Error adding question:', error);
            this.showError('Failed to add question');
        }
    }

    async handleAddUser(form) {
        try {
            const formData = new FormData(form);
            const userData = {
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                company: formData.get('company'),
                industry: formData.get('industry')
            };

            const response = await fetch('/admin/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                this.showSuccess('User added successfully!');
                this.closeModal();
                form.reset();
                this.loadDashboardData();
            } else {
                throw new Error('Failed to add user');
            }
        } catch (error) {
            console.error('Error adding user:', error);
            this.showError('Failed to add user');
        }
    }

    async deleteQuestion(id) {
        if (!confirm('Are you sure you want to delete this question?')) {
            return;
        }

        try {
            const response = await fetch(`/admin/api/questions/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccess('Question deleted successfully!');
                this.loadDashboardData();
            } else {
                throw new Error('Failed to delete question');
            }
        } catch (error) {
            console.error('Error deleting question:', error);
            this.showError('Failed to delete question');
        }
    }

    async deleteUser(id) {
        if (!confirm('Are you sure you want to delete this user?')) {
            return;
        }

        try {
            const response = await fetch(`/admin/api/users/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccess('User deleted successfully!');
                this.loadDashboardData();
            } else {
                throw new Error('Failed to delete user');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            this.showError('Failed to delete user');
        }
    }

    async exportUsers() {
        try {
            this.showLoading('Exporting users data...');
            
            const response = await fetch('/admin/export/users');
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'users_export.xlsx');
                this.showSuccess('Users data exported successfully!');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export users data');
        } finally {
            this.hideLoading();
        }
    }

    async exportSessions() {
        try {
            this.showLoading('Exporting sessions data...');
            
            const response = await fetch('/admin/export/sessions');
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'sessions_export.xlsx');
                this.showSuccess('Sessions data exported successfully!');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export sessions data');
        } finally {
            this.hideLoading();
        }
    }

    async exportQuestions() {
        try {
            this.showLoading('Exporting questions data...');
            
            const response = await fetch('/admin/export/questions');
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'questions_export.xlsx');
                this.showSuccess('Questions data exported successfully!');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export questions data');
        } finally {
            this.hideLoading();
        }
    }

    downloadFile(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    handleSearch(query) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.currentPage = 1;
            this.loadDashboardData();
        }, 500);
    }

    changePage(page) {
        this.currentPage = page;
        this.loadDashboardData();
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = 'auto';
    }

    setupAutoRefresh() {
        // Refresh dashboard data every 5 minutes
        setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

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

    showError(message) {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        document.body.appendChild(error);
        
        setTimeout(() => {
            error.remove();
        }, 5000);
    }

    showSuccess(message) {
        const success = document.createElement('div');
        success.className = 'success-message';
        success.textContent = message;
        document.body.appendChild(success);
        
        setTimeout(() => {
            success.remove();
        }, 3000);
    }
}

// Initialize admin manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('admin-page')) {
        window.adminManager = new AdminManager();
    }
});