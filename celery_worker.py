from api.core.celery import celery_app
from agents.crew import travel_crew

@celery_app.task
def run_crew_task(user_query: str):
    """CrewAI 작업을 비동기적으로 실행하는 Celery 태스크"""
    result = travel_crew.kickoff(inputs={'query': user_query})
    return result.raw