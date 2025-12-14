/**
 * 🐾 Animales Perdidos - JavaScript Principal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar efectos
    initParallax();
    initRipple();
    initScrollReveal();
    initCounters();
    initDragDrop();
    initTheme();
    initFloatingPaws();
});

/**
 * Efecto parallax en header
 */
function initParallax() {
    const parallaxLayers = document.querySelectorAll('.parallax-layer');
    
    if (parallaxLayers.length === 0) return;
    
    document.addEventListener('mousemove', (e) => {
        const x = (e.clientX - window.innerWidth / 2) / 50;
        const y = (e.clientY - window.innerHeight / 2) / 50;
        
        parallaxLayers.forEach((layer, index) => {
            const depth = (index + 1) * 0.5;
            layer.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
        });
    });
}

/**
 * Efecto ripple en botones
 */
function initRipple() {
    document.querySelectorAll('.btn-huella, .btn-huella-outline, button').forEach(button => {
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = e.clientX - rect.left - size / 2 + 'px';
            ripple.style.top = e.clientY - rect.top - size / 2 + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

/**
 * Animación al hacer scroll
 */
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));
}

/**
 * Contadores animados
 */
function initCounters() {
    const counters = document.querySelectorAll('[data-count]');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-count'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                counter.textContent = target;
                clearInterval(timer);
            } else {
                counter.textContent = Math.floor(current);
            }
        }, 16);
    });
}

/**
 * Drag and drop para fotos
 */
function initDragDrop() {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            const input = zone.querySelector('input[type="file"]');
            
            if (input && files.length > 0) {
                input.files = files;
                previewPhoto(files[0], zone);
            }
        });
    });
}

/**
 * Preview de foto
 */
function previewPhoto(file, container) {
    if (!file.type.startsWith('image/')) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        let preview = container.querySelector('.photo-preview');
        if (!preview) {
            preview = document.createElement('img');
            preview.className = 'photo-preview w-32 h-32 object-cover rounded-xl mx-auto mt-3';
            container.appendChild(preview);
        }
        preview.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

/**
 * Toggle tema oscuro
 */
function initTheme() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
        document.documentElement.classList.add('dark');
    }
}

function toggleTheme() {
    const html = document.documentElement;
    html.classList.toggle('dark');
    localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
}

/**
 * Huellas flotantes decorativas
 */
function initFloatingPaws() {
    const paws = ['🐾', '🐕', '🐈', '🐦', '🐰'];
    
    for (let i = 0; i < 5; i++) {
        const paw = document.createElement('div');
        paw.className = 'floating-paw';
        paw.textContent = paws[Math.floor(Math.random() * paws.length)];
        paw.style.left = Math.random() * 100 + 'vw';
        paw.style.top = Math.random() * 100 + 'vh';
        paw.style.animationDelay = Math.random() * 5 + 's';
        document.body.appendChild(paw);
    }
}

/**
 * Mostrar confetti al encontrar mascota
 */
function celebrar() {
    const colors = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff'];
    
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 0.5 + 's';
        document.body.appendChild(confetti);
        
        setTimeout(() => confetti.remove(), 3000);
    }
}

/**
 * Seleccionar categoría
 */
function seleccionarCategoria(cat) {
    document.querySelectorAll('.categoria-btn').forEach(btn => {
        btn.classList.remove('ring-2', 'ring-amber-500', 'bg-amber-100');
    });
    
    const selected = document.querySelector(`[data-cat="${cat}"]`);
    if (selected) {
        selected.classList.add('ring-2', 'ring-amber-500', 'bg-amber-100');
    }
    
    const input = document.getElementById('categoria');
    if (input) input.value = cat;
}

/**
 * Mostrar alertas
 */
function mostrarAlerta(mensaje, tipo = 'success') {
    const container = document.getElementById('alertas');
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo}`;
    alert.innerHTML = `
        <span>${mensaje}</span>
        <button onclick="this.parentElement.remove()" class="ml-4 font-bold">&times;</button>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
}

/**
 * Compartir reporte
 */
async function compartir(nombre, ubicacion, contacto) {
    const texto = `🐾 ${nombre}\n📍 Ubicación: ${ubicacion}\n📞 Contacto: ${contacto}`;
    
    if (navigator.share) {
        try {
            await navigator.share({
                title: 'Reporte de Animal Perdido',
                text: texto
            });
        } catch (err) {
            console.log('Compartir cancelado');
        }
    } else {
        await navigator.clipboard.writeText(texto);
        mostrarAlerta('Información copiada al portapapeles 📋');
    }
}
