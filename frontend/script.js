// Banking System Frontend JavaScript
class BankingSystem {
    constructor() {
        this.API_BASE_URL = 'http://localhost:5000/api';
        this.init();
    }

    async init() {
        // Initialize the system
        this.setupEventListeners();
        await this.checkAPIHealth();
        this.updateDateTime();
        
        // Update time every second
        setInterval(() => this.updateDateTime(), 1000);
        
        // Check API health every 30 seconds
        setInterval(() => this.checkAPIHealth(), 30000);
        
        // Initial welcome message
        setTimeout(() => {
            this.addMessage('Banking System initialized. Ready for operations.', 'info');
        }, 1000);
    }

    // Update current date and time
    updateDateTime() {
        const now = new Date();
        const datetime = now.toLocaleString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        const datetimeElement = document.getElementById('datetime');
        if (datetimeElement) {
            datetimeElement.textContent = datetime;
        }
    }

    // Check API health status
    async checkAPIHealth() {
        const apiStatus = document.getElementById('apiStatus');
        if (!apiStatus) return;

        try {
            const response = await fetch(`${this.API_BASE_URL}/health`);
            if (response.ok) {
                const data = await response.json();
                apiStatus.innerHTML = '<i class="fas fa-circle" style="color: #28a745;"></i><span>API: Connected</span>';
                return true;
            } else {
                apiStatus.innerHTML = '<i class="fas fa-circle" style="color: #dc3545;"></i><span>API: Disconnected</span>';
                return false;
            }
        } catch (error) {
            apiStatus.innerHTML = '<i class="fas fa-circle" style="color: #dc3545;"></i><span>API: Error</span>';
            this.addMessage('API connection failed. Make sure the backend server is running on port 5000.', 'error');
            return false;
        }
    }

    // Setup all event listeners
    setupEventListeners() {
        // Menu navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => this.handleMenuClick(e));
        });

        // Form submissions
        const createAccountForm = document.getElementById('createAccountForm');
        const depositForm = document.getElementById('depositForm');
        const withdrawForm = document.getElementById('withdrawForm');
        const balanceForm = document.getElementById('balanceForm');
        const transactionsForm = document.getElementById('transactionsForm');

        if (createAccountForm) {
            createAccountForm.addEventListener('submit', (e) => this.handleCreateAccount(e));
        }
        if (depositForm) {
            depositForm.addEventListener('submit', (e) => this.handleDeposit(e));
        }
        if (withdrawForm) {
            withdrawForm.addEventListener('submit', (e) => this.handleWithdraw(e));
        }
        if (balanceForm) {
            balanceForm.addEventListener('submit', (e) => this.handleBalanceCheck(e));
        }
        if (transactionsForm) {
            transactionsForm.addEventListener('submit', (e) => this.handleTransactionHistory(e));
        }

        // Clear results button
        const clearResultsBtn = document.getElementById('clearResults');
        if (clearResultsBtn) {
            clearResultsBtn.addEventListener('click', () => this.clearMessages());
        }
    }

    // Handle menu click
    handleMenuClick(event) {
        const menuItem = event.currentTarget;
        
        // Remove active class from all menu items
        document.querySelectorAll('.menu-item').forEach(i => {
            i.classList.remove('active');
        });
        
        // Add active class to clicked item
        menuItem.classList.add('active');
        
        // Hide all form sections
        document.querySelectorAll('.form-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show the selected form section
        const target = menuItem.getAttribute('data-target');
        const targetSection = document.getElementById(target);
        if (targetSection) {
            targetSection.classList.add('active');
        }
    }

    // Handle Create Account form
    async handleCreateAccount(event) {
        event.preventDefault();
        
        const nameInput = document.getElementById('name');
        const balanceInput = document.getElementById('initialBalance');
        
        if (!nameInput || !balanceInput) {
            this.addMessage('Form elements not found.', 'error');
            return;
        }
        
        const name = nameInput.value.trim();
        const balance = parseFloat(balanceInput.value);
        
        if (!name) {
            this.addMessage('Please enter your full name.', 'error');
            return;
        }
        
        if (isNaN(balance) || balance < 10) {
            this.addMessage('Minimum initial deposit is $10.00.', 'error');
            return;
        }
        
        // Show loading
        this.showLoading('createAccountLoading');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/create_account`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    balance: balance
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const accountType = document.getElementById('accountType')?.value || 'savings';
                this.addMessage(`Account created successfully! Account Number: ${result.account_number}, Name: ${result.name}, Initial Balance: $${result.balance.toFixed(2)}, Type: ${accountType}`, 'success');
                
                // Clear form
                event.target.reset();
                if (balanceInput) {
                    balanceInput.value = '10.00';
                }
            } else {
                this.addMessage(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.addMessage('Network error. Please check your connection and try again.', 'error');
        } finally {
            this.hideLoading('createAccountLoading');
        }
    }

    // Handle Deposit form
    async handleDeposit(event) {
        event.preventDefault();
        
        const accNoInput = document.getElementById('depositAccNo');
        const amountInput = document.getElementById('depositAmount');
        
        if (!accNoInput || !amountInput) {
            this.addMessage('Form elements not found.', 'error');
            return;
        }
        
        const accNo = parseInt(accNoInput.value);
        const amount = parseFloat(amountInput.value);
        
        if (!accNo || accNo <= 0) {
            this.addMessage('Please enter a valid account number.', 'error');
            return;
        }
        
        if (!amount || amount <= 0) {
            this.addMessage('Please enter a valid deposit amount.', 'error');
            return;
        }
        
        // Show loading
        this.showLoading('depositLoading');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/deposit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    acc_no: accNo,
                    amount: amount
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addMessage(`Successfully deposited $${amount.toFixed(2)} to account #${accNo}. New balance: $${result.new_balance.toFixed(2)}`, 'success');
                event.target.reset();
            } else {
                this.addMessage(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.addMessage('Network error. Please check your connection and try again.', 'error');
        } finally {
            this.hideLoading('depositLoading');
        }
    }

    // Handle Withdraw form
    async handleWithdraw(event) {
        event.preventDefault();
        
        const accNoInput = document.getElementById('withdrawAccNo');
        const amountInput = document.getElementById('withdrawAmount');
        
        if (!accNoInput || !amountInput) {
            this.addMessage('Form elements not found.', 'error');
            return;
        }
        
        const accNo = parseInt(accNoInput.value);
        const amount = parseFloat(amountInput.value);
        
        if (!accNo || accNo <= 0) {
            this.addMessage('Please enter a valid account number.', 'error');
            return;
        }
        
        if (!amount || amount <= 0) {
            this.addMessage('Please enter a valid withdrawal amount.', 'error');
            return;
        }
        
        // Show loading
        this.showLoading('withdrawLoading');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/withdraw`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    acc_no: accNo,
                    amount: amount
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addMessage(`Successfully withdrew $${amount.toFixed(2)} from account #${accNo}. New balance: $${result.new_balance.toFixed(2)}`, 'warning');
                event.target.reset();
            } else {
                this.addMessage(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.addMessage('Network error. Please check your connection and try again.', 'error');
        } finally {
            this.hideLoading('withdrawLoading');
        }
    }

    // Handle Balance check form
    async handleBalanceCheck(event) {
        event.preventDefault();
        
        const accNoInput = document.getElementById('balanceAccNo');
        
        if (!accNoInput) {
            this.addMessage('Form element not found.', 'error');
            return;
        }
        
        const accNo = parseInt(accNoInput.value);
        
        if (!accNo || accNo <= 0) {
            this.addMessage('Please enter a valid account number.', 'error');
            return;
        }
        
        // Show loading
        this.showLoading('balanceLoading');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/balance/${accNo}`);
            const result = await response.json();
            
            const resultDiv = document.getElementById('balanceResult');
            
            if (result.success) {
                if (resultDiv) {
                    resultDiv.innerHTML = `
                        <div class="balance-display">
                            <div class="balance-header">
                                <i class="fas fa-user-circle"></i>
                                <h4>Account Information</h4>
                            </div>
                            <div class="balance-details">
                                <div class="balance-row">
                                    <span>Account Number:</span>
                                    <strong>${result.account_number}</strong>
                                </div>
                                <div class="balance-row">
                                    <span>Account Holder:</span>
                                    <strong>${result.name}</strong>
                                </div>
                                <div class="balance-row">
                                    <span>Account Created:</span>
                                    <strong>${result.created_at}</strong>
                                </div>
                                <div class="balance-row highlight">
                                    <span>Current Balance:</span>
                                    <strong class="balance-amount">$${result.balance.toFixed(2)}</strong>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                this.addMessage(`Balance checked for account #${accNo}`, 'info');
                event.target.reset();
            } else {
                if (resultDiv) {
                    resultDiv.innerHTML = '';
                }
                this.addMessage(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.addMessage('Network error. Please check your connection and try again.', 'error');
            const resultDiv = document.getElementById('balanceResult');
            if (resultDiv) {
                resultDiv.innerHTML = '';
            }
        } finally {
            this.hideLoading('balanceLoading');
        }
    }

    // Handle Transaction History form
    async handleTransactionHistory(event) {
        event.preventDefault();
        
        const accNoInput = document.getElementById('transAccNo');
        
        if (!accNoInput) {
            this.addMessage('Form element not found.', 'error');
            return;
        }
        
        const accNo = parseInt(accNoInput.value);
        
        if (!accNo || accNo <= 0) {
            this.addMessage('Please enter a valid account number.', 'error');
            return;
        }
        
        // Show loading
        this.showLoading('transactionsLoading');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/transactions/${accNo}`);
            const result = await response.json();
            
            const resultDiv = document.getElementById('transactionsResult');
            
            if (result.success) {
                if (resultDiv) {
                    let transactionsHTML = '<div class="transactions-list">';
                    
                    if (result.transactions && result.transactions.length > 0) {
                        result.transactions.forEach(trans => {
                            const typeClass = trans.type.toLowerCase().includes('deposit') || trans.type.toLowerCase().includes('initial') ? "deposit" : "withdrawal";
                            const icon = typeClass === "deposit" ? 'arrow-down' : 'arrow-up';
                            const formattedDate = new Date(trans.date_time).toLocaleString();
                            
                            transactionsHTML += `
                                <div class="transaction-item ${typeClass}">
                                    <div class="transaction-type">
                                        <i class="fas fa-${icon}"></i>
                                        <span>${trans.type}</span>
                                    </div>
                                    <div class="transaction-amount">$${parseFloat(trans.amount).toFixed(2)}</div>
                                    <div class="transaction-date">${formattedDate}</div>
                                </div>
                            `;
                        });
                    } else {
                        transactionsHTML += `
                            <div class="no-transactions">
                                <i class="fas fa-info-circle"></i>
                                <p>No transactions found for this account.</p>
                            </div>
                        `;
                    }
                    
                    transactionsHTML += '</div>';
                    
                    resultDiv.innerHTML = `
                        <div class="transactions-container">
                            <div class="transactions-header">
                                <i class="fas fa-file-alt"></i>
                                <h4>Transaction History for Account #${accNo} (${result.name})</h4>
                            </div>
                            <div class="transactions-summary">
                                <p>Total Transactions: ${result.count || 0}</p>
                            </div>
                            ${transactionsHTML}
                        </div>
                    `;
                }
                
                this.addMessage(`Transaction history retrieved for account #${accNo}`, 'info');
                event.target.reset();
            } else {
                if (resultDiv) {
                    resultDiv.innerHTML = '';
                }
                this.addMessage(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            this.addMessage('Network error. Please check your connection and try again.', 'error');
            const resultDiv = document.getElementById('transactionsResult');
            if (resultDiv) {
                resultDiv.innerHTML = '';
            }
        } finally {
            this.hideLoading('transactionsLoading');
        }
    }

    // Show loading spinner
    showLoading(elementId) {
        const loadingElement = document.getElementById(elementId);
        if (loadingElement) {
            loadingElement.style.display = 'flex';
        }
    }

    // Hide loading spinner
    hideLoading(elementId) {
        const loadingElement = document.getElementById(elementId);
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    // Add message to message container
    addMessage(text, type = 'info') {
        const messageContainer = document.getElementById('messageContainer');
        if (!messageContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'warning') icon = 'exclamation-triangle';
        if (type === 'error') icon = 'exclamation-circle';
        
        const now = new Date();
        const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <div class="message-content">
                <p>${text}</p>
                <small class="message-time">${time}</small>
            </div>
        `;
        
        // Add to top of container
        messageContainer.insertBefore(messageDiv, messageContainer.firstChild);
        
        // Limit to 5 messages
        if (messageContainer.children.length > 5) {
            messageContainer.removeChild(messageContainer.lastChild);
        }
    }

    // Clear all messages
    clearMessages() {
        const messageContainer = document.getElementById('messageContainer');
        if (messageContainer) {
            messageContainer.innerHTML = '';
            this.addMessage('All messages cleared.', 'info');
        }
    }
}

// Initialize the banking system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.bankingSystem = new BankingSystem();
});