from backend.config import settings  # ✅ importa settings que ya tiene la API key
import httpx
from typing import Dict, Optional


class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        if not self.api_key:
            raise ValueError("⚠️ Falta configurar OPENWEATHER_API_KEY en tu .env")
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_weather(self, city: str = "San Jose") -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": city,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "es",
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            return {
                "ciudad": data["name"],
                "temperatura": data["main"]["temp"],
                "sensacion_termica": data["main"]["feels_like"],
                "humedad": data["main"]["humidity"],
                "descripcion": data["weather"][0]["description"],
                "viento": data["wind"]["speed"],
            }
        except Exception as e:
            return {"error": f"Error obteniendo clima: {str(e)}"}


class NutritionService:
    """Servicio para obtener información nutricional y recetas saludables"""

    def __init__(self):
        # API gratuita que no requiere key para recetas básicas
        self.base_url = "https://www.themealdb.com/api/json/v1/1"

    async def get_healthy_meals(self, categoria: str = "Chicken") -> Dict:
        """Obtiene recetas saludables por categoría"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Buscar recetas por ingrediente principal
                resp = await client.get(
                    f"{self.base_url}/filter.php",
                    params={"i": categoria}
                )
                resp.raise_for_status()
                data = resp.json()

            if not data.get("meals"):
                return {
                    "categoria": categoria,
                    "total_recetas": 0,
                    "recetas": [],
                    "mensaje": f"No se encontraron recetas para {categoria}"
                }

            # Formatear solo las primeras 5 recetas
            recetas_formateadas = []
            for meal in data["meals"][:5]:
                recetas_formateadas.append({
                    "nombre": meal["strMeal"],
                    "imagen": meal["strMealThumb"],
                    "id": meal["idMeal"],
                    "categoria": meal.get("strCategory", "General")
                })

            return {
                "categoria": categoria,
                "total_recetas": len(recetas_formateadas),
                "recetas": recetas_formateadas,
                "mensaje": f"Recetas saludables encontradas para {categoria}"
            }

        except Exception as e:
            return {
                "error": f"Error obteniendo recetas: {str(e)}",
                "categoria": categoria,
                "total_recetas": 0,
                "recetas": []
            }


# ✅ Crear instancias globales de los servicios
weather_service = WeatherService()
nutrition_service = NutritionService()