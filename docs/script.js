// script.js

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // --- Lightbox Logic ---
    const galleryImages = document.querySelectorAll('.screenshot-gallery img, .editor-image img');
    const lightboxOverlay = document.getElementById('lightbox-overlay');
    const lightboxImage = document.getElementById('lightbox-image');
    const lightboxClose = document.getElementById('lightbox-close');

    if (galleryImages.length && lightboxOverlay) {
        galleryImages.forEach(image => {
            image.addEventListener('click', () => {
                lightboxOverlay.style.display = 'flex';
                lightboxImage.src = image.src;
            });
        });

        const closeLightbox = () => {
            lightboxOverlay.style.display = 'none';
        };

        lightboxClose.addEventListener('click', closeLightbox);
        lightboxOverlay.addEventListener('click', (e) => {
            // Close only if the overlay itself is clicked, not the image
            if (e.target === lightboxOverlay) closeLightbox();
        });
    }
});