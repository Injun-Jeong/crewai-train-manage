import os
import time
import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Type
from datetime import date

load_dotenv()

TRAIN_API_BASE_URL = os.getenv("TRAIN_API_BASE_URL")

# --- 도구 입력 스키마 정의  ---
class CurrentDateTool(BaseTool):
    name: str = "Current Date Finder"
    description: str = "오늘의 현재 날짜를 'YYYY-MM-DD' 형식으로 확인하기 위해 사용합니다."
    cache: bool = False

    def _run(self) -> str:
        return date.today().strftime("%Y-%m-%d")

class RequestSearchInput(BaseModel):
    dep_station: str = Field(..., description="출발역 이름 (예: '수서')")
    arr_station: str = Field(..., description="도착역 이름 (예: '부산')")
    dep_date: str = Field(..., description="출발 날짜 (YYYY-MM-DD 형식)")

class GetResultsInput(BaseModel):
    job_id: str = Field(..., description="검색 요청 후 받은 작업 ID")


# --- 도구 1: 열차 검색 크롤링 요청 도구(비동기) ---
class RequestTrainSearchTool(BaseTool):
    name: str = "Request Train Search"
    description: str = "열차 좌석 조회를 '시작'하고 '작업 ID'를 받기 위해 사용합니다. 출발역, 도착역, 날짜를 반드시 입력해야 합니다."
    args_schema: Type[BaseModel] = RequestSearchInput
    cache: bool = False

    def _run(self, **kwargs) -> str:
        try:
            response = requests.post(
                f"{TRAIN_API_BASE_URL}/api/v1/search/check-seat-availability",
                json=kwargs
            )
            response.raise_for_status()
            result = response.json()
            return f"Search requested successfully. Your job ID is: {result['result_id']}"
        except Exception as e:
            return f"Error requesting train search: {e}"


# --- 도구 2: 크롤링 결과 조회 도구 ---
class GetTrainSearchResultsTool(BaseTool):
    name: str = "Get Train Search Results"
    description: str = "이전에 요청한 열차 조회의 '결과'를 '작업 ID'를 사용해 가져옵니다."
    args_schema: Type[BaseModel] = GetResultsInput
    cache: bool = False

    def _run(self, **kwargs) -> str:
        job_id = kwargs.get('job_id')
        if not job_id:
            return "Error: job_id is required."
            
        for _ in range(8):
            try:
                response = requests.get(f"{TRAIN_API_BASE_URL}/api/v1/search/results/{job_id}")
                response.raise_for_status()
                result = response.json()

                if result['status'] == 'COMPLETED':
                    return f"Search completed. Train information: {result['data']}"
                elif result['status'] == 'ERROR':
                    return f"Search failed. Error: {result['data']}"
                
                time.sleep(5)
            except Exception as e:
                return f"Error getting search results: {e}"
        return "Search timed out. The result is still pending after 40 seconds."