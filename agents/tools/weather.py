# tools/weather_tool.py (새 파일 또는 기존 파일에 추가)
from crewai.tools import BaseTool

class WeatherSearchTool(BaseTool):
    name: str = "Weather Search Tool"
    description: str = "지정된 도시와 날짜의 날씨 정보를 조회합니다. 입력은 '도시,YYYY-MM-DD' 형식이어야 합니다."

    def _run(self, argument: str) -> str:
        city, date = argument.split(',')
        # 이 부분에 실제 날씨 API를 호출하는 코드를 구현합니다.
        # 예시를 위해 더미 데이터를 반환합니다.
        print(f"Buscando clima para {city.strip()} en la fecha {date.strip()}...")
        return f"{date}의 {city} 날씨는 '맑음', 최고 기온 25°C, 최저 기온 15°C 입니다."