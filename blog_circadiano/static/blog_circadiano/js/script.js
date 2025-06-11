// blog_circadiano/static/blog_circadiano/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Lógica para el manejo de formularios de respuesta de comentarios ---
    document.querySelectorAll('.reply-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            // Ocultar todos los formularios de respuesta excepto el actual
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });

            // Alternar la visibilidad del formulario de respuesta actual
            if (replyForm.style.display === 'none' || replyForm.style.display === '') {
                replyForm.style.display = 'block';
            } else {
                replyForm.style.display = 'none';
            }
        });
    });

    // --- Lógica para el Modo Noche (Dark Mode) ---

    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement; // Usamos el elemento HTML
    const currentTheme = localStorage.getItem('theme'); // Obtiene la preferencia guardada

    // 1. Aplicar el tema guardado al cargar la página (para el texto del botón)
    // La aplicación de la clase ya la hace el script temprano en el <head> de base.html
    if (currentTheme === 'dark-mode') {
        if (themeToggleBtn) { // Asegúrate de que el botón existe antes de cambiar su texto
            themeToggleBtn.textContent = 'Modo Día';
        }
    } else {
        if (themeToggleBtn) {
            themeToggleBtn.textContent = 'Modo Noche';
        }
    }

    // Opcional: Esto ya no es estrictamente necesario aquí si el script en <head> maneja la preferencia del sistema
    // Sin embargo, si decides eliminar el script en <head>, esta parte sería necesaria.
    // if (!currentTheme && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    //     // Esto ya lo maneja el script en el head para evitar el flash
    //     // htmlElement.classList.add('dark-mode'); 
    //     if (themeToggleBtn) {
    //         themeToggleBtn.textContent = 'Modo Día';
    //     }
    //     localStorage.setItem('theme', 'dark-mode');
    // } 

    // 2. Manejar el clic del botón de alternancia
    if (themeToggleBtn) { // Esto es crucial: Solo añade el listener si el botón se encontró
        themeToggleBtn.addEventListener('click', () => {
            if (htmlElement.classList.contains('dark-mode')) {
                htmlElement.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light-mode'); // Guarda la preferencia
                themeToggleBtn.textContent = 'Modo Noche';
            } else {
                htmlElement.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark-mode'); // Guarda la preferencia
                themeToggleBtn.textContent = 'Modo Día';
            }
        });
    }
});