from abc import ABC, abstractmethod

class AbstractLanguageModel(ABC):
    """
    모든 언어 모델이 따라야 하는 기본 인터페이스를 정의하는 추상 클래스입니다.
    """
    @abstractmethod
    def call(self, text: str) -> str:
        """주어진 텍스트를 처리하고 결과를 문자열로 반환합니다."""
        pass