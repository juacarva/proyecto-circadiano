// blog_circadiano/static/blog_circadiano/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Lógica para el manejo de formularios de respuesta de comentarios ---
    document.querySelectorAll('.reply-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            
            document.querySelectorAll('.reply-form').forEach(form => {
                if (form.id !== `reply-form-${commentId}`) {
                    form.style.display = 'none';
                }
            });

            if (replyForm.style.display === 'none' || replyForm.style.display === '') {
                replyForm.style.display = 'block';
                // Opcional: Desplazarse al formulario
                replyForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                replyForm.style.display = 'none';
            }
        });
    });

    // --- Lógica para el Modo Noche (Dark Mode) ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const currentTheme = localStorage.getItem('theme'); 

    // Función para actualizar el ícono del botón
    function updateThemeToggleButtonIcon(isDarkMode) {
        if (themeToggleBtn) { // Asegura que el botón fue encontrado
            const iconElement = themeToggleBtn.querySelector('i'); // Busca la etiqueta <i> dentro del botón
            const textElement = themeToggleBtn.querySelector('.sr-only');

            if (iconElement) { // Asegura que la etiqueta <i> fue encontrada
                if (isDarkMode) {
                    iconElement.classList.remove('fa-moon');
                    iconElement.classList.add('fa-sun');
                } else {
                    iconElement.classList.remove('fa-sun');
                    iconElement.classList.add('fa-moon');
                }
            }
            if (textElement) {
                textElement.textContent = isDarkMode ? 'Modo Día' : 'Modo Noche';
            }
        }
    }

    // Aplicar el tema guardado al cargar la página (y ajustar el icono)
    // La aplicación de la clase HTML.dark-mode ya la hace el script temprano en el <head>
    if (currentTheme === 'dark-mode') {
        updateThemeToggleButtonIcon(true); // Pasar true para modo oscuro
    } else {
        updateThemeToggleButtonIcon(false); // Pasar false para modo claro
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            if (htmlElement.classList.contains('dark-mode')) {
                htmlElement.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light-mode');
                updateThemeToggleButtonIcon(false); // Actualiza ícono a sol
            } else {
                htmlElement.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark-mode');
                updateThemeToggleButtonIcon(true); // Actualiza ícono a luna
            }
        });
    }

    // --- Lógica para el botón "Me gusta" (toggle_like) ---
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemType = this.dataset.itemType; // Esto será 'articulo' o 'comentario'
            const itemId = this.dataset.itemId;
            const url = this.dataset.url;
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; 

            if (!itemType || !itemId) {
                console.error('Tipo o ID de ítem no definido para el like.');
                return;
            }

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken,
                    },
                    body: `item_type=${itemType}&item_id=${itemId}`
                });

                if (!response.ok) {
                    const errorText = await response.text(); 
                    console.error('Error HTTP:', response.status, response.statusText, 'Respuesta:', errorText);
                    alert(`Error al dar Me gusta: ${response.status} ${response.statusText}. Por favor, inténtalo de nuevo.`);
                    return;
                }

                const data = await response.json(); 

                if (data.status === 'success') {
                    // MODIFICACIÓN CRÍTICA AQUÍ: Ajustar el prefijo del ID
                    let idPrefix = '';
                    if (itemType === 'articulo') {
                        idPrefix = 'article';
                    } else if (itemType === 'comentario') {
                        idPrefix = 'comment';
                    }
                    
                    const likesCountSpan = document.getElementById(`${idPrefix}-likes-count-${itemId}`);
                    
                    if (likesCountSpan) { // <--- Añadimos una comprobación por si acaso
                        likesCountSpan.textContent = data.total_likes;
                    } else {
                        console.error(`Elemento con ID ${idPrefix}-likes-count-${itemId} no encontrado.`);
                    }
                    
                    if (data.liked) {
                        this.classList.add('liked');
                        this.innerHTML = '<span class="icon">&#x2764;</span> Ya no me gusta';
                    } else {
                        this.classList.remove('liked');
                        this.innerHTML = '<span class="icon">&#x2764;</span> Me gusta';
                    }
                } else {
                    console.error('Error al procesar like (respuesta del servidor):', data.message);
                    alert('Error al dar Me gusta: ' + data.message);
                }
            } catch (error) {
                console.error('Error de red o parsing JSON:', error);
                alert('Hubo un error de conexión o el servidor envió una respuesta inesperada.');
            }
        });
    });

    // --- Lógica para el botón "Archivar/Desarchivar Conversación" ---
    document.querySelectorAll('.archive-toggle-button').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const convId = this.dataset.convId;
            const isArchivedInitial = this.dataset.isArchived === 'true'; // Convierte el string a booleano
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            if (!convId) {
                console.error('ID de conversación no definido para el archivo.');
                return;
            }

            try {
                const response = await fetch('/messages/toggle_archive/', { // Ajusta la URL si es diferente
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken,
                    },
                    body: `conversation_id=${convId}`
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Error HTTP al archivar/desarchivar:', response.status, response.statusText, 'Respuesta:', errorText);
                    alert(`Error al archivar/desarchivar conversación: ${response.status} ${response.statusText}. Por favor, inténtalo de nuevo.`);
                    return;
                }

                const data = await response.json();

                if (data.status === 'success') {
                    // Actualizar el botón y posiblemente eliminar/mover la conversación de la lista
                    const conversationItem = document.getElementById(`conv-${convId}`);
                    
                    if (data.is_archived) {
                        this.innerHTML = '<i class="fa-solid fa-box-open"></i> Desarchivar';
                        this.dataset.isArchived = 'true';
                        // Opcional: Eliminar el elemento de la lista "Activas" o moverlo
                        // if (conversationItem) { conversationItem.remove(); } // Si quieres que desaparezca inmediatamente
                        // Opcional: Añadir una animación o mensaje de confirmación
                    } else {
                        this.innerHTML = '<i class="fa-solid fa-box-archive"></i> Archivar';
                        this.dataset.isArchived = 'false';
                        // Opcional: Eliminar el elemento de la lista "Archivadas"
                        // if (conversationItem) { conversationItem.remove(); }
                    }
                    alert(data.message); // Muestra el mensaje de éxito del servidor

                    // Para una experiencia de usuario fluida, podrías recargar solo la lista
                    // o redirigir a la URL actual para que se aplique el filtro.
                    // location.reload(); // Recargar la página para aplicar el filtro

                    // Una mejor opción es simplemente recargar la lista de conversaciones
                    // sin una recarga completa de la página, pero eso es más avanzado (AJAX para la lista).
                    // Por ahora, un reload simple es efectivo.
                    window.location.reload(); // Recargar la página para que se actualice el filtro
                } else {
                    console.error('Error al procesar archivo (respuesta del servidor):', data.message);
                    alert('Error al archivar/desarchivar: ' + data.message);
                }
            } catch (error) {
                console.error('Error de red o parsing JSON al archivar:', error);
                alert('Hubo un error de conexión o el servidor envió una respuesta inesperada al archivar/desarchivar.');
            }
        });
    });

    // --- Lógica para mostrar/ocultar comentarios y desplazar ---
    // Asegúrate de que el ID del artículo esté en el h1.articulo-titulo con data-pk
    const articlePkElement = document.querySelector('.articulo-titulo');
    const articlePk = articlePkElement ? articlePkElement.dataset.pk : null;

    const commentsContainer = document.getElementById(`comments-section-${articlePk}`);
    const commentsToggleButton = document.getElementById(`comment-toggle-btn-${articlePk}`);
    const replyToArticleButton = document.getElementById(`reply-to-article-btn-${articlePk}`);
    const articleCommentForm = document.getElementById('article-comment-form');

    if (commentsToggleButton && commentsContainer) {
        commentsToggleButton.addEventListener('click', () => {
            if (commentsContainer.style.display === 'none' || commentsContainer.style.display === '') {
                commentsContainer.style.display = 'block';
                commentsToggleButton.textContent = 'Ocultar comentarios'; // Cambiar texto al mostrar
            } else {
                commentsContainer.style.display = 'none';
                // CAMBIO CLAVE AQUÍ: Restablecer el texto original del botón.
                // Usamos innerHTML para mantener el icono si lo tienes en el HTML original del botón.
                commentsToggleButton.innerHTML = '<span class="icon">&#x1F4AC;</span> Comentarios'; 
                // Si quieres el conteo, necesitarías recuperarlo o guardarlo:
                // commentsToggleButton.innerHTML = `<span class="icon">&#x1F4AC;</span> Comentarios (${document.querySelector('#comments-section-' + articlePk + ' h2').textContent.match(/\((\d+)\)/)[1]})`;
                // Para simplificar, si no quieres re-calcular el conteo dinámicamente:
                // commentsToggleButton.innerHTML = '<span class="icon">&#x1F4AC;</span> Comentarios';
            }
        });
    }

    if (replyToArticleButton && articleCommentForm) {
        replyToArticleButton.addEventListener('click', () => {
            if (commentsContainer) {
                commentsContainer.style.display = 'block';
                // Asegúrate de que el botón de comentarios también refleje que están visibles
                if (commentsToggleButton) {
                     commentsToggleButton.textContent = 'Ocultar comentarios';
                }
            }
            articleCommentForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }
});