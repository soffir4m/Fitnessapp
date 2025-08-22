// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Función para manejar el formulario de contacto
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.querySelector('#contact form');

    if (contactForm) {
        contactForm.addEventListener('submit', handleContactSubmit);
    }

    // Cargar programas dinámicamente
    loadPrograms();
    
    // Cargar dashboard fitness inicialmente
    loadFitnessDashboard();
    
    // Configurar evento del botón actualizar dashboard
    const dashboardBtn = document.getElementById('load-dashboard-btn');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', loadFitnessDashboard);
    }
});

async function handleContactSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const contactData = {
        nombre: formData.get('nombre') || e.target.querySelector('input[type="text"]').value,
        correo: formData.get('correo') || e.target.querySelector('input[type="email"]').value,
        mensaje: formData.get('mensaje') || e.target.querySelector('textarea').value
    };

    // Validaciones básicas del frontend
    if (!contactData.nombre || contactData.nombre.length < 2) {
        showAlert('El nombre debe tener al menos 2 caracteres', 'error');
        return;
    }

    if (!contactData.correo || !isValidEmail(contactData.correo)) {
        showAlert('Por favor ingresa un correo electrónico válido', 'error');
        return;
    }

    if (!contactData.mensaje || contactData.mensaje.length < 10) {
        showAlert('El mensaje debe tener al menos 10 caracteres', 'error');
        return;
    }

    const submitButton = e.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;

    try {
        // Deshabilitar botón y mostrar loading
        submitButton.disabled = true;
        submitButton.textContent = 'Enviando...';

        console.log('Enviando datos:', contactData);

        const response = await fetch(`${API_BASE_URL}/contactos/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(contactData)
        });

        console.log('Respuesta status:', response.status);
        const responseData = await response.json();
        console.log('Respuesta data:', responseData);

        if (response.ok) {
            showAlert('¡Mensaje enviado exitosamente! Te contactaremos pronto.', 'success');
            e.target.reset();
        } else {
            const errorMessage = responseData.detail || 'Error al enviar el mensaje';
            showAlert(errorMessage, 'error');
        }

    } catch (error) {
        console.error('Error enviando contacto:', error);
        showAlert('Error de conexión. Por favor intenta nuevamente.', 'error');
    } finally {
        // Restaurar botón
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    }
}

async function loadPrograms() {
    try {
        const response = await fetch(`${API_BASE_URL}/programas/`);

        if (response.ok) {
            const programs = await response.json();
            displayPrograms(programs);
        } else {
            console.error('Error cargando programas:', response.status);
        }
    } catch (error) {
        console.error('Error conectando con la API:', error);
    }
}

function displayPrograms(programs) {
    const programsSection = document.querySelector('#programs .grid');

    if (programsSection && programs.length > 0) {
        programsSection.innerHTML = programs.map(program => `
            <div class="bg-white/80 backdrop-blur-lg p-6 rounded-2xl shadow-lg hover:scale-105 transition">
                <h4 class="text-xl font-semibold mb-3">${program.nombre}</h4>
                <p class="text-gray-600">${program.descripcion}</p>
            </div>
        `).join('');
    }
}

function showAlert(message, type = 'info') {
    // Remover alertas existentes
    const existingAlerts = document.querySelectorAll('.custom-alert');
    existingAlerts.forEach(alert => alert.remove());

    const alert = document.createElement('div');
    alert.className = `custom-alert fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;

    const bgColor = type === 'success' ? 'bg-green-500' :
                   type === 'error' ? 'bg-red-500' : 'bg-blue-500';

    alert.className += ` ${bgColor} text-white`;
    alert.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                ✕
            </button>
        </div>
    `;

    document.body.appendChild(alert);

    // Animar entrada
    setTimeout(() => {
        alert.classList.remove('translate-x-full');
    }, 100);

    // Auto remover después de 5 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.add('translate-x-full');
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// === FITNESS DASHBOARD FUNCTIONS ===

// Función principal para cargar el dashboard fitness
async function loadFitnessDashboard() {
    const cityInput = document.getElementById('city-input');
    const categoryInput = document.getElementById('category-input');
    const loadButton = document.getElementById('load-dashboard-btn');
    
    if (!cityInput || !categoryInput) return;
    
    const city = cityInput.value.trim() || 'San Jose';
    const category = categoryInput.value || 'Chicken';
    
    // Mostrar loading
    if (loadButton) {
        loadButton.disabled = true;
        loadButton.innerHTML = '🔄 Cargando...';
    }
    
    try {
        // Cargar datos del dashboard (clima y recetas) de forma concurrente
        const [weatherData, nutritionData] = await Promise.all([
            loadWeatherData(city),
            loadNutritionData(category)
        ]);
        
        // Mostrar los datos en el dashboard
        displayWeatherInfo(weatherData);
        displayNutritionInfo(nutritionData);
        displayRecipesGrid(nutritionData?.recetas || []);
        
        showAlert(`🎆 Dashboard actualizado para ${city} con recetas de ${category}!`, 'success');
        
    } catch (error) {
        console.error('Error cargando dashboard:', error);
        showAlert('Error cargando el dashboard. Intenta nuevamente.', 'error');
        displayErrorStates();
    } finally {
        // Restaurar botón
        if (loadButton) {
            loadButton.disabled = false;
            loadButton.innerHTML = '🔄 Actualizar';
        }
    }
}

// Cargar datos del clima
async function loadWeatherData(city) {
    const response = await fetch(`${API_BASE_URL}/weather/?ciudad=${encodeURIComponent(city)}`);
    if (!response.ok) {
        throw new Error(`Error cargando clima: ${response.status}`);
    }
    return await response.json();
}

// Cargar datos de nutrición
async function loadNutritionData(category) {
    const response = await fetch(`${API_BASE_URL}/nutrition/?categoria=${encodeURIComponent(category)}`);
    if (!response.ok) {
        throw new Error(`Error cargando recetas: ${response.status}`);
    }
    return await response.json();
}

// Mostrar información del clima
function displayWeatherInfo(weatherData) {
    const weatherContent = document.getElementById('weather-content');
    if (!weatherContent) return;
    
    if (weatherData.error) {
        weatherContent.innerHTML = `
            <div class="text-red-600 p-4 bg-red-50 rounded-lg">
                <p class="font-medium">⚠️ Error del clima</p>
                <p class="text-sm">${weatherData.error}</p>
            </div>
        `;
        return;
    }
    
    const tempColor = weatherData.temperatura > 25 ? 'text-red-600' : 
                     weatherData.temperatura > 15 ? 'text-yellow-600' : 'text-blue-600';
    
    weatherContent.innerHTML = `
        <div class="space-y-3">
            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700">🏡 Ciudad:</span>
                <span class="text-green-600 font-semibold">${weatherData.ciudad}</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700">🌡️ Temperatura:</span>
                <span class="${tempColor} font-bold text-lg">${weatherData.temperatura}°C</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700">💧 Humedad:</span>
                <span class="text-blue-600">${weatherData.humedad}%</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700">🌬️ Viento:</span>
                <span class="text-gray-600">${weatherData.viento} m/s</span>
            </div>
            <div class="pt-3 border-t border-gray-200">
                <p class="text-sm text-gray-600 mb-2">🌤️ ${weatherData.descripcion}</p>
                <div class="bg-green-50 p-3 rounded-lg">
                    <p class="text-sm font-medium text-green-800">🏋️ Recomendación:</p>
                    <p class="text-sm text-green-700">${weatherData.recomendacion_ejercicio}</p>
                </div>
            </div>
        </div>
    `;
}

// Mostrar información de nutrición
function displayNutritionInfo(nutritionData) {
    const nutritionContent = document.getElementById('nutrition-content');
    if (!nutritionContent) return;
    
    if (nutritionData.error) {
        nutritionContent.innerHTML = `
            <div class="text-red-600 p-4 bg-red-50 rounded-lg">
                <p class="font-medium">⚠️ Error de recetas</p>
                <p class="text-sm">${nutritionData.error}</p>
            </div>
        `;
        return;
    }
    
    const categoryEmojis = {
        'Chicken': '🐔',
        'Beef': '🥩',
        'Seafood': '🦐',
        'Vegetarian': '🥬',
        'Dessert': '🍓'
    };
    
    const emoji = categoryEmojis[nutritionData.categoria] || '🍽️';
    
    nutritionContent.innerHTML = `
        <div class="space-y-3">
            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700">🍽️ Categoría:</span>
                <span class="text-green-600 font-semibold">${emoji} ${nutritionData.categoria}</span>
            </div>
            <div class="flex justify-between items-center">
                <span class="font-medium text-gray-700">📊 Total encontradas:</span>
                <span class="text-blue-600 font-bold">${nutritionData.total_recetas} recetas</span>
            </div>
            <div class="pt-3 border-t border-gray-200">
                <div class="bg-blue-50 p-3 rounded-lg">
                    <p class="text-sm font-medium text-blue-800">💪 Beneficios Fitness:</p>
                    <p class="text-sm text-blue-700">Alto en proteína, Bajo en carbohidratos</p>
                    <p class="text-xs text-blue-600 mt-1">Ideal para complementar tu rutina de entrenamiento</p>
                </div>
            </div>
        </div>
    `;
}

// Mostrar grid de recetas
function displayRecipesGrid(recipes) {
    const recipesContainer = document.getElementById('recipes-container');
    if (!recipesContainer || !recipes.length) {
        if (recipesContainer) {
            recipesContainer.innerHTML = `
                <div class="col-span-full text-center p-8 text-gray-500">
                    <p>🍴 No hay recetas disponibles</p>
                </div>
            `;
        }
        return;
    }
    
    recipesContainer.innerHTML = recipes.map(recipe => `
        <div class="bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden hover:scale-105">
            <div class="aspect-square relative overflow-hidden">
                <img 
                    src="${recipe.imagen}" 
                    alt="${recipe.nombre}"
                    class="w-full h-full object-cover"
                    loading="lazy"
                    onerror="this.src='https://via.placeholder.com/200x200?text=🍽️'"
                >
                <div class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                    💪
                </div>
            </div>
            <div class="p-3">
                <h6 class="font-medium text-sm text-gray-800 mb-1 line-clamp-2" title="${recipe.nombre}">
                    ${recipe.nombre}
                </h6>
                <p class="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full inline-block">
                    ${recipe.tags_fitness}
                </p>
            </div>
        </div>
    `).join('');
}

// Mostrar estados de error
function displayErrorStates() {
    const weatherContent = document.getElementById('weather-content');
    const nutritionContent = document.getElementById('nutrition-content');
    const recipesContainer = document.getElementById('recipes-container');
    
    const errorHtml = `
        <div class="text-red-600 p-4 bg-red-50 rounded-lg text-center">
            <p class="font-medium">⚠️ Error de conexión</p>
            <p class="text-sm">No se pudieron cargar los datos</p>
        </div>
    `;
    
    if (weatherContent) weatherContent.innerHTML = errorHtml;
    if (nutritionContent) nutritionContent.innerHTML = errorHtml;
    if (recipesContainer) {
        recipesContainer.innerHTML = `
            <div class="col-span-full text-center p-8 text-red-500">
                <p>😔 Error cargando recetas</p>
            </div>
        `;
    }
}

// === END FITNESS DASHBOARD FUNCTIONS ===

// Smooth scroll para navegación
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
