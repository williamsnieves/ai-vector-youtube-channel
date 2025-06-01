from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from .entities import Channel, Video, AnalysisResult

class YouTubeRepository(ABC):
    @abstractmethod
    async def get_channel_info(self, channel_id: str) -> Channel:
        pass
    
    @abstractmethod
    async def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Video]:
        pass
    
    @abstractmethod
    async def get_video_transcript(self, video_id: str) -> Optional[str]:
        pass

class VectorStoreRepository(ABC):
    @abstractmethod
    async def store_channel_data(self, channel: Channel) -> None:
        pass
    
    @abstractmethod
    async def store_analysis_result(self, result: AnalysisResult) -> None:
        pass
    
    @abstractmethod
    async def search_similar_content(self, query: str) -> List[Dict]:
        pass

class AIProvider(ABC):
    @abstractmethod
    async def analyze_channel(self, channel: Channel) -> AnalysisResult:
        pass
    
    @abstractmethod
    async def generate_recommendations(self, analysis: AnalysisResult) -> List[str]:
        pass

class InstagramRepository(ABC):
    @abstractmethod
    async def publish_post(self, content: str, account: str) -> Dict:
        """Publish a post to Instagram
        
        Args:
            content: The content to publish
            account: The Instagram account username to publish to
        """
        pass

class TwitterRepository(ABC):
    @abstractmethod
    async def publish_post(self, content: str, account: str) -> Dict:
        """Publish a post to Twitter (X)
        
        Args:
            content: The content to publish
            account: The Twitter account username to publish to
        """
        pass 