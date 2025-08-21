import httpx
import os
from typing import Dict, Optional


class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"

    async def get_weather(self, city: str = "San Jose") -> Optional[Dict]:
        """Obtiene el clima actual para determinar si es buen día para entrenar"""
        if not self.api_key:
            return {"error": "API key not configured"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": city,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "es"
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Procesamos los datos para fitness
                return {
                    "ciudad": data["name"],
                    "temperatura": data["main"]["temp"],
                    "sensacion_termica": data["main"]["feels_like"],
                    "humedad": data["main"]["humidity"],
                    "descripcion": data["weather"][0]["description"],
                    "viento": data["wind"]["speed"],
                    "recomendacion_ejercicio": self._get_exercise_recommendation(
                        data["main"]["temp"],
                        data["main"]["humidity"],
                        data["weather"][0]["main"]
                    )
                }
            except httpx.HTTPError as e:
                return {"error": f"Error fetching weather: {str(e)}"}

    def _get_exercise_recommendation(self, temp: float, humidity: int, condition: str) -> str:
        """Genera recomendación de ejercicio basada en el clima"""
        if temp < 10:
            return "Ideal para ejercicio indoor o cardio intenso"
        elif temp > 30 or humidity > 80:
            return "Recomendado ejercicio ligero, mantente hidratado"
        elif condition in ["Rain", "Thunderstorm"]:
            return "Perfecto para rutina indoor o yoga"
        else:
            return "Excelente día para ejercicio al aire libre"


# Servicio alternativo con TheMealDB para recetas fitness
class NutritionService:
    def __init__(self):
        self.base_url = "https://www.themealdb.com/api/json/v1/1"

    async def get_healthy_meals(self, category: str = "Chicken") -> Optional[Dict]:
        """Obtiene recetas saludables por categoría"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/filter.php",
                    params={"c": category}
                )
                response.raise_for_status()
                data = response.json()

                # Limitamos a 5 recetas y agregamos info fitness
                meals = data.get("meals", [])[:5]
                return {
                    "categoria": category,
                    "total_recetas": len(meals),
                    "recetas": [
                        {
                            "id": meal["idMeal"],
                            "nombre": meal["strMeal"],
                            "imagen": meal["strMealThumb"],
                            "tags_fitness": "Alto en proteína, Bajo en carbohidratos"
                        }
                        for meal in meals
                    ]
                }
            except httpx.HTTPError as e:
                return {"error": f"Error fetching meals: {str(e)}"}


weather_service = WeatherService()
nutrition_service = NutritionService()