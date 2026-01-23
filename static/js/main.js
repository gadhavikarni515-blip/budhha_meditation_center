// ===== TESTIMONIALS SLIDER =====
let slideIdx = 0;
const slides = document.querySelectorAll('.nb-review-card');
const totalSlides = slides.length;
const dots = document.querySelectorAll('.nb-dot');

function showTestimonial(idx) {
    // Update slides
    slides.forEach((el, i) => {
        if (i === idx) {
            el.classList.remove('slide-exit');
            el.classList.add('slide-active');
        } else {
            el.classList.remove('slide-active');
            if (i < idx) {
                el.classList.add('slide-exit');
            } else {
                el.classList.remove('slide-exit');
            }
        }
    });

    // Update dots
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === idx);
    });
}

// Initialize first slide
if (slides.length > 0) {
    showTestimonial(slideIdx);
}

// Previous button
const prevBtn = document.getElementById('prevRev');
if (prevBtn) {
    prevBtn.addEventListener('click', () => {
        slideIdx = (slideIdx - 1 + totalSlides) % totalSlides;
        showTestimonial(slideIdx);
        resetAutoSlide();
    });
}

// Next button
const nextBtn = document.getElementById('nextRev');
if (nextBtn) {
    nextBtn.addEventListener('click', () => {
        slideIdx = (slideIdx + 1) % totalSlides;
        showTestimonial(slideIdx);
        resetAutoSlide();
    });
}

// Dot navigation
dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
        slideIdx = index;
        showTestimonial(slideIdx);
        resetAutoSlide();
    });
});

// Auto-rotate testimonials
let autoSlideInterval;

function startAutoSlide() {
    autoSlideInterval = setInterval(() => {
        slideIdx = (slideIdx + 1) % totalSlides;
        showTestimonial(slideIdx);
    }, 5000); // Change every 5 seconds
}

function resetAutoSlide() {
    clearInterval(autoSlideInterval);
    startAutoSlide();
}

// Start auto-slide
if (slides.length > 0) {
    startAutoSlide();

    // Pause on hover
    const sliderWrapper = document.querySelector('.nb-slider-wrapper');
    if (sliderWrapper) {
        sliderWrapper.addEventListener('mouseenter', () => {
            clearInterval(autoSlideInterval);
        });
        sliderWrapper.addEventListener('mouseleave', () => {
            startAutoSlide();
        });
    }
}

// ===== SCROLL REVEAL ANIMATIONS =====
const revealSections = document.querySelectorAll('.nb-section, .nb-card, .nb-benefit-card, .nb-feature-card, .nb-instructor-row');

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('nb--inview');
            // Optional: stop observing after animation
            // observer.unobserve(entry.target);
        }
    });
}, observerOptions);

revealSections.forEach(section => {
    observer.observe(section);
});

// ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            const offsetTop = target.offsetTop - 80; // Account for sticky navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });

            // Update active nav link
            document.querySelectorAll('.nb-links a').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
        }
    });
});

// ===== UPDATE ACTIVE NAV LINK ON SCROLL =====
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nb-links a');

function updateActiveNav() {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

window.addEventListener('scroll', updateActiveNav);

// ===== ENHANCE CARD HOVER EFFECTS =====
document.querySelectorAll('.nb-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    });
});

// ===== PARALLAX EFFECT FOR HERO (Optional) =====
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.nb-hero');
    const heroImg = document.querySelector('.nb-hero-img');
    const energyAura = document.querySelector('.nb-energy-aura');

    if (hero && scrolled < hero.offsetHeight) {
        if (heroImg) {
            heroImg.style.transform = `translateY(${scrolled * 0.3}px)`;
        }
        if (energyAura) {
            energyAura.style.transform = `translate(-50%, -50%) translateY(${scrolled * 0.2}px)`;
            energyAura.style.opacity = 0.4 - (scrolled / 1000);
        }
    }
});

// ===== ADD LOADING ANIMATION =====
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// ===== ENHANCE BUTTON CLICKS =====
document.querySelectorAll('.cta-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        // Create ripple effect
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

        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple CSS dynamically
const style = document.createElement('style');
style.textContent = `
  .cta-btn {
    position: relative;
    overflow: hidden;
  }
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
  }
  @keyframes ripple-animation {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// ===== PROGRAM REGISTRATION MODAL =====
const registerBtns = document.querySelectorAll('.register-btn');
const registerNowBtns = document.querySelectorAll('.register-now-btn');
const registerModal = document.getElementById('registerProgramModal');
const closeRegisterModal = document.getElementById('closeRegisterModal');
const registerForm = document.getElementById('registerProgramForm');

// Handle Programs page register buttons (with program ID)
registerBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const programName = this.getAttribute('data-program-name');

        document.getElementById('register-program-name').value = programName;
        document.getElementById('modalProgramName').textContent = 'Program: ' + programName;
        registerModal.style.display = 'flex';
    });
});

// Handle Home page register buttons (without program ID - for program name only)
registerNowBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const programName = this.getAttribute('data-program-name');

        document.getElementById('register-program-name').value = programName;
        document.getElementById('modalProgramName').textContent = 'Program: ' + programName;
        registerModal.style.display = 'flex';
    });
});

if (closeRegisterModal) {
    closeRegisterModal.addEventListener('click', function() {
        registerModal.style.display = 'none';
        registerForm.reset();
        document.getElementById('registerSuccess').style.display = 'none';
    });
}

// Close modal on overlay click
if (registerModal) {
    registerModal.addEventListener('click', function(e) {
        if (e.target === registerModal) {
            registerModal.style.display = 'none';
            registerForm.reset();
            document.getElementById('registerSuccess').style.display = 'none';
        }
    });
}

// Handle register form submission
if (registerForm) {
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const programName = document.getElementById('register-program-name').value;
        const fullName = document.getElementById('register-fullname').value;
        const phone = document.getElementById('register-phone').value;
        const email = document.getElementById('register-email').value;

        try {
            const formData = new FormData();
            formData.append('program_name', programName);
            formData.append('full_name', fullName);
            formData.append('phone', phone);
            formData.append('email', email);

            const response = await fetch('/register_program_modal', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                document.getElementById('registerSuccess').textContent = data.message;
                document.getElementById('registerSuccess').style.display = 'block';
                registerForm.style.display = 'none';

                setTimeout(() => {
                    registerModal.style.display = 'none';
                    registerForm.reset();
                    registerForm.style.display = 'block';
                    document.getElementById('registerSuccess').style.display = 'none';
                }, 3000);
            } else {
                alert(data.error || 'Registration failed!');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during registration.');
        }
    });
}

console.log('✨ Nirvana Buddha - Premium Meditation Website Loaded');

// ===== MOBILE NAV TOGGLE =====
(function() {
    const hamburger = document.querySelector('.nb-hamburger');
    const mobileMenu = document.getElementById('nb-mobile-menu');
    const navbar = document.querySelector('.nb-navbar');

    if (!hamburger || !mobileMenu || !navbar) return;

    const closeMobileMenu = () => {
        navbar.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        mobileMenu.hidden = true;
    };

    hamburger.addEventListener('click', (e) => {
        const expanded = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.setAttribute('aria-expanded', String(!expanded));
        navbar.classList.toggle('open');
        mobileMenu.hidden = !navbar.classList.contains('open');
        e.stopPropagation();
    });

    // Close when a menu link is clicked
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMobileMenu));

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!navbar.contains(e.target)) closeMobileMenu();
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeMobileMenu();
    });
})();

// ===== SESSION REGISTRATION MODAL =====
const registerSessionBtns = document.querySelectorAll('.register-session-btn');
const registerSessionModal = document.getElementById('registerSessionModal');
const sessionRegistrationForm = document.getElementById('sessionRegistrationForm');

// Handle session register buttons
registerSessionBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const sessionId = this.getAttribute('data-session-id');
        const sessionName = this.getAttribute('data-session-name');

        document.getElementById('sessionId').value = sessionId;
        document.getElementById('sessionName').value = sessionName;
        document.getElementById('displaySessionName').value = sessionName;
        if (registerSessionModal) {
            registerSessionModal.style.display = 'flex';
        }
    });
});

// Handle session modal close button
const sessionModalCloseBtn = registerSessionModal ?.querySelector('.modal-close');
if (sessionModalCloseBtn) {
    sessionModalCloseBtn.addEventListener('click', function() {
        if (registerSessionModal) {
            registerSessionModal.style.display = 'none';
        }
        sessionRegistrationForm.reset();
        document.getElementById('sessionRegisterSuccess').style.display = 'none';
    });
}

// Close session modal on overlay click
if (registerSessionModal) {
    registerSessionModal.addEventListener('click', function(e) {
        if (e.target === registerSessionModal) {
            registerSessionModal.style.display = 'none';
            sessionRegistrationForm.reset();
            document.getElementById('sessionRegisterSuccess').style.display = 'none';
        }
    });
}

// Handle session registration form submission
if (sessionRegistrationForm) {
    sessionRegistrationForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const sessionId = document.getElementById('sessionId').value;
        const sessionName = document.getElementById('sessionName').value;
        const name = document.getElementById('sessionUserName').value;
        const email = document.getElementById('sessionEmail').value;
        const phone = document.getElementById('sessionPhone').value;

        try {
            const formData = new FormData();
            formData.append('session_id', sessionId);
            formData.append('session_name', sessionName);
            formData.append('name', name);
            formData.append('email', email);
            formData.append('phone', phone);

            const response = await fetch('/register_session_modal', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                document.getElementById('sessionRegisterSuccess').textContent = data.message;
                document.getElementById('sessionRegisterSuccess').style.display = 'block';
                sessionRegistrationForm.style.display = 'none';

                setTimeout(() => {
                    registerSessionModal.style.display = 'none';
                    sessionRegistrationForm.reset();
                    sessionRegistrationForm.style.display = 'block';
                    document.getElementById('sessionRegisterSuccess').style.display = 'none';
                }, 3000);
            } else {
                alert(data.error || 'Registration failed!');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during registration.');
        }
    });
}