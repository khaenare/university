document.addEventListener('DOMContentLoaded', function() {
    const feedbackLink = document.querySelector('.feedback-link');
    const overlay      = document.querySelector('.modal-overlay');
    const modal        = document.querySelector('.feedback-modal');
    const form         = document.getElementById('feedback-form');

    function openModal() {
        overlay.classList.add('show');
        modal.classList.add('show');
    }
    function closeModal() {
        overlay.classList.remove('show');
        modal.classList.remove('show');
    }

    feedbackLink.addEventListener('click', function(e) {
        e.preventDefault();
        openModal();
    });
    overlay.addEventListener('click', closeModal);
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });
    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) return;
        e.preventDefault();
        alert('Дякуй, ваш відгук надіслано!');
        closeModal();
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.slider'),
        slides = slider.querySelectorAll('.slide'),
        prev = document.createElement('button'),
        next = document.createElement('button');
    let idx = 0, interval;

    prev.className = 'slider-nav prev';
    prev.innerHTML = '&#10094;';
    next.className = 'slider-nav next';
    next.innerHTML = '&#10095;';
    slider.append(prev, next);

    function show(n) {
        slides[idx].classList.remove('active');
        idx = (n + slides.length) % slides.length;
        slides[idx].classList.add('active');
    }
    function reset() {
        clearInterval(interval);
        interval = setInterval(() => show(idx + 1), 4000);
    }

    prev.onclick = () => { show(idx - 1); reset(); };
    next.onclick = () => { show(idx + 1); reset(); };
    reset();
});
