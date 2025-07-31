// جافا سكريبت للثيمات والتحكم في المظهر

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || 'light';
        this.applyTheme(this.currentTheme);
        this.setupThemeToggle();
        this.setupColorCustomization();
        this.setupAnimations();
    }

    // استرجاع الثيم المحفوظ
    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    // حفظ الثيم
    saveTheme(theme) {
        localStorage.setItem('theme', theme);
    }

    // تطبيق الثيم
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.saveTheme(theme);
        this.updateThemeButton();
    }

    // تغيير الثيم
    toggleTheme() {
        const themes = ['light', 'dark', 'royal', 'nature'];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        this.applyTheme(themes[nextIndex]);
    }

    // إعداد زر تغيير الثيم
    setupThemeToggle() {
        // إنشاء زر الثيم إذا لم يكن موجوداً
        if (!document.getElementById('theme-toggle')) {
            this.createThemeToggle();
        }

        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    // إنشاء زر تغيير الثيم
    createThemeToggle() {
        const themeToggle = document.createElement('button');
        themeToggle.id = 'theme-toggle';
        themeToggle.className = 'fixed top-4 left-4 z-50 p-3 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-600';
        themeToggle.innerHTML = this.getThemeIcon();
        
        document.body.appendChild(themeToggle);
    }

    // أيقونة الثيم
    getThemeIcon() {
        const icons = {
            light: '☀️',
            dark: '🌙',
            royal: '👑',
            nature: '🌿'
        };
        return icons[this.currentTheme] || '🎨';
    }

    // تحديث زر الثيم
    updateThemeButton() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = this.getThemeIcon();
            themeToggle.title = `الثيم الحالي: ${this.getThemeName()}`;
        }
    }

    // اسم الثيم بالعربية
    getThemeName() {
        const names = {
            light: 'فاتح',
            dark: 'داكن',
            royal: 'ملكي',
            nature: 'طبيعي'
        };
        return names[this.currentTheme] || 'مخصص';
    }

    // إعداد تخصيص الألوان
    setupColorCustomization() {
        // إنشاء لوحة تخصيص الألوان
        this.createColorPanel();
    }

    // إنشاء لوحة تخصيص الألوان
    createColorPanel() {
        const panel = document.createElement('div');
        panel.id = 'color-panel';
        panel.className = 'fixed top-20 left-4 z-40 bg-white dark:bg-gray-800 rounded-xl shadow-xl p-4 hidden';
        panel.innerHTML = `
            <h3 class="text-lg font-bold mb-4 text-gray-800 dark:text-white">🎨 تخصيص الألوان</h3>
            <div class="space-y-3">
                <div>
                    <label class="block text-sm font-medium mb-1">اللون الأساسي:</label>
                    <input type="color" id="primary-color" class="w-full h-8 rounded">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">اللون الثانوي:</label>
                    <input type="color" id="secondary-color" class="w-full h-8 rounded">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">لون الخلفية:</label>
                    <input type="color" id="background-color" class="w-full h-8 rounded">
                </div>
                <button id="apply-colors" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition">
                    تطبيق الألوان
                </button>
                <button id="reset-colors" class="w-full bg-gray-600 text-white py-2 rounded hover:bg-gray-700 transition">
                    إعادة تعيين
                </button>
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // زر فتح لوحة الألوان
        const colorButton = document.createElement('button');
        colorButton.id = 'color-toggle';
        colorButton.className = 'fixed top-16 left-4 z-50 p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-600 text-sm';
        colorButton.innerHTML = '🎨';
        colorButton.title = 'تخصيص الألوان';
        
        document.body.appendChild(colorButton);
        
        // أحداث لوحة الألوان
        this.setupColorEvents();
    }

    // إعداد أحداث لوحة الألوان
    setupColorEvents() {
        document.getElementById('color-toggle')?.addEventListener('click', () => {
            const panel = document.getElementById('color-panel');
            panel.classList.toggle('hidden');
        });

        document.getElementById('apply-colors')?.addEventListener('click', () => {
            this.applyCustomColors();
        });

        document.getElementById('reset-colors')?.addEventListener('click', () => {
            this.resetColors();
        });
    }

    // تطبيق الألوان المخصصة
    applyCustomColors() {
        const primaryColor = document.getElementById('primary-color')?.value;
        const secondaryColor = document.getElementById('secondary-color')?.value;
        const backgroundColor = document.getElementById('background-color')?.value;

        if (primaryColor) {
            document.documentElement.style.setProperty('--primary-color', primaryColor);
        }
        if (secondaryColor) {
            document.documentElement.style.setProperty('--secondary-color', secondaryColor);
        }
        if (backgroundColor) {
            document.documentElement.style.setProperty('--background-color', backgroundColor);
        }

        // حفظ الألوان المخصصة
        localStorage.setItem('custom-colors', JSON.stringify({
            primary: primaryColor,
            secondary: secondaryColor,
            background: backgroundColor
        }));

        this.showNotification('تم تطبيق الألوان المخصصة!', 'success');
    }

    // إعادة تعيين الألوان
    resetColors() {
        localStorage.removeItem('custom-colors');
        this.applyTheme(this.currentTheme);
        this.showNotification('تم إعادة تعيين الألوان!', 'info');
    }

    // تحميل الألوان المخصصة
    loadCustomColors() {
        const customColors = localStorage.getItem('custom-colors');
        if (customColors) {
            const colors = JSON.parse(customColors);
            if (colors.primary) {
                document.documentElement.style.setProperty('--primary-color', colors.primary);
            }
            if (colors.secondary) {
                document.documentElement.style.setProperty('--secondary-color', colors.secondary);
            }
            if (colors.background) {
                document.documentElement.style.setProperty('--background-color', colors.background);
            }
        }
    }

    // إعداد الرسوم المتحركة
    setupAnimations() {
        // رسوم متحركة للعناصر عند الظهور
        this.observeElements();
        
        // رسوم متحركة للنقر
        this.setupClickAnimations();
    }

    // مراقبة العناصر للرسوم المتحركة
    observeElements() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fadeIn');
                }
            });
        }, { threshold: 0.1 });

        // مراقبة البطاقات والعناصر
        document.querySelectorAll('.card-modern, .btn-modern, .table-modern').forEach(el => {
            observer.observe(el);
        });
    }

    // رسوم متحركة للنقر
    setupClickAnimations() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn-modern, .theme-button')) {
                e.target.classList.add('animate-pulse');
                setTimeout(() => {
                    e.target.classList.remove('animate-pulse');
                }, 600);
            }
        });
    }

    // عرض الإشعارات
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// إدارة الخطوط
class FontManager {
    constructor() {
        this.fonts = [
            { name: 'Cairo', label: 'القاهرة' },
            { name: 'Amiri', label: 'أميري' },
            { name: 'Noto Sans Arabic', label: 'نوتو سانس' }
        ];
        this.currentFont = localStorage.getItem('selected-font') || 'Cairo';
        this.applyFont();
        this.createFontSelector();
    }

    applyFont() {
        document.documentElement.style.setProperty('--font-primary', `'${this.currentFont}', sans-serif`);
        localStorage.setItem('selected-font', this.currentFont);
    }

    createFontSelector() {
        const selector = document.createElement('select');
        selector.id = 'font-selector';
        selector.className = 'fixed bottom-4 left-4 z-50 p-2 rounded bg-white dark:bg-gray-800 shadow-lg border';
        
        this.fonts.forEach(font => {
            const option = document.createElement('option');
            option.value = font.name;
            option.textContent = font.label;
            option.selected = font.name === this.currentFont;
            selector.appendChild(option);
        });

        selector.addEventListener('change', (e) => {
            this.currentFont = e.target.value;
            this.applyFont();
        });

        document.body.appendChild(selector);
    }
}

// تحسينات الأداء
class PerformanceOptimizer {
    constructor() {
        this.setupLazyLoading();
        this.setupImageOptimization();
    }

    // تحميل الصور الكسول
    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // تحسين الصور
    setupImageOptimization() {
        document.querySelectorAll('img').forEach(img => {
            img.addEventListener('load', () => {
                img.classList.add('animate-fadeIn');
            });
        });
    }
}

// تهيئة كل شيء عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
    window.fontManager = new FontManager();
    window.performanceOptimizer = new PerformanceOptimizer();
    
    // تحميل الألوان المخصصة
    window.themeManager.loadCustomColors();
});

// دعم PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
