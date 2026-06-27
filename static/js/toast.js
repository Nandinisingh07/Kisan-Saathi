class Toast {
    static init() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        this.container = container;
    }

    static show(hindiText, englishText, type = 'info') {
        if (!this.container) {
            this.init();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-triangle';

        toast.innerHTML = `
            <i class="fas fa-${icon}" style="font-size: 1.25rem;"></i>
            <div class="bilingual-text">
                <span class="hi-text">${hindiText}</span>
                <span class="en-text">${englishText}</span>
            </div>
        `;

        this.container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s reverse forwards';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 4000);
    }

    static success(hi, en) {
        this.show(hi, en, 'success');
    }

    static error(hi, en) {
        this.show(hi, en, 'error');
    }

    static info(hi, en) {
        this.show(hi, en, 'info');
    }
}

document.addEventListener('DOMContentLoaded', () => Toast.init());
