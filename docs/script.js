// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 70; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile navigation toggle
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a link
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });

    // Navbar background on scroll
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .step, .doc-card, .contact-item');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Typing animation for hero title
    const heroTitle = document.querySelector('.hero-content h1');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        // Start typing animation after a short delay
        setTimeout(typeWriter, 500);
    }

    // Chat bubble animation
    const chatBubbles = document.querySelectorAll('.chat-bubble');
    chatBubbles.forEach((bubble, index) => {
        bubble.style.opacity = '0';
        bubble.style.transform = 'translateX(-20px)';
        bubble.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            bubble.style.opacity = '1';
            bubble.style.transform = 'translateX(0)';
        }, 1000 + (index * 500));
    });

    // Price ticker simulation
    const priceElement = document.createElement('div');
    priceElement.className = 'price-ticker';
    priceElement.innerHTML = `
        <i class="fab fa-bitcoin"></i>
        <span class="price">$43,250.00</span>
        <span class="change positive">+2.45%</span>
    `;
    priceElement.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: linear-gradient(135deg, #f7931a, #ff9500);
        color: white;
        padding: 10px 15px;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(247, 147, 26, 0.3);
        z-index: 999;
        display: flex;
        align-items: center;
        gap: 8px;
        opacity: 0;
        transform: translateX(100px);
        transition: all 0.5s ease;
    `;
    
    document.body.appendChild(priceElement);
    
    // Show price ticker after hero section
    setTimeout(() => {
        priceElement.style.opacity = '1';
        priceElement.style.transform = 'translateX(0)';
    }, 2000);

    // Simulate price updates
    setInterval(() => {
        const priceSpan = priceElement.querySelector('.price');
        const changeSpan = priceElement.querySelector('.change');
        
        const currentPrice = parseFloat(priceSpan.textContent.replace('$', '').replace(',', ''));
        const change = (Math.random() - 0.5) * 1000;
        const newPrice = currentPrice + change;
        const changePercent = (change / currentPrice * 100).toFixed(2);
        
        priceSpan.textContent = `$${newPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        changeSpan.textContent = `${changePercent > 0 ? '+' : ''}${changePercent}%`;
        changeSpan.className = `change ${changePercent > 0 ? 'positive' : 'negative'}`;
    }, 5000);

    // Add CSS for price ticker
    const style = document.createElement('style');
    style.textContent = `
        .price-ticker .change.positive {
            color: #10b981;
        }
        .price-ticker .change.negative {
            color: #ef4444;
        }
        @media (max-width: 768px) {
            .price-ticker {
                display: none !important;
            }
        }
    `;
    document.head.appendChild(style);

    // Form validation for contact form (if exists)
    const contactForm = document.querySelector('form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const email = this.querySelector('input[type="email"]');
            const message = this.querySelector('textarea');
            
            if (email && !email.value.includes('@')) {
                alert('Please enter a valid email address');
                return;
            }
            
            if (message && message.value.length < 10) {
                alert('Please enter a message with at least 10 characters');
                return;
            }
            
            // Simulate form submission
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                alert('Thank you for your message! We\'ll get back to you soon.');
                this.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }

    // Add loading animation
    window.addEventListener('load', function() {
        const loader = document.querySelector('.loader');
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }
    });

    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero');
        if (hero) {
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        }
    });

    // Add hover effects for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add click-to-copy functionality for code blocks
    const codeBlocks = document.querySelectorAll('code');
    codeBlocks.forEach(code => {
        code.style.cursor = 'pointer';
        code.title = 'Click to copy';
        
        code.addEventListener('click', function() {
            const text = this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                // Show feedback
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                this.style.background = '#10b981';
                this.style.color = 'white';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '#f3f4f6';
                    this.style.color = '#f7931a';
                }, 1000);
            });
        });
    });
});

// Add CSS for mobile navigation
const mobileNavStyles = `
    @media (max-width: 768px) {
        .nav-menu {
            position: fixed;
            left: -100%;
            top: 70px;
            flex-direction: column;
            background-color: white;
            width: 100%;
            text-align: center;
            transition: 0.3s;
            box-shadow: 0 10px 27px rgba(0, 0, 0, 0.05);
            padding: 2rem 0;
        }
        
        .nav-menu.active {
            left: 0;
        }
        
        .nav-menu li {
            margin: 1rem 0;
        }
        
        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: translateY(8px) rotate(45deg);
        }
        
        .hamburger.active span:nth-child(3) {
            transform: translateY(-8px) rotate(-45deg);
        }
    }
`;

// Inject mobile navigation styles
const styleSheet = document.createElement('style');
styleSheet.textContent = mobileNavStyles;
document.head.appendChild(styleSheet);
