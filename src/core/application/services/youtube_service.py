from typing import List, Optional, Dict
from ...domain.interfaces import YouTubeRepository, VectorStoreRepository, AIProvider
from ...domain.entities import Channel, AnalysisResult

class YouTubeAnalysisService:
    def __init__(
        self,
        youtube_repository: YouTubeRepository,
        vector_store_repository: VectorStoreRepository,
        ai_provider: AIProvider
    ):
        self.youtube_repository = youtube_repository
        self.vector_store_repository = vector_store_repository
        self.ai_provider = ai_provider

    async def analyze_channel(self, channel_id: str) -> AnalysisResult:
        # 1. Get channel data from YouTube
        channel = await self.youtube_repository.get_channel_info(channel_id)
        
        # 2. Store channel data in vector store
        await self.vector_store_repository.store_channel_data(channel)
        
        # 3. Analyze channel using AI
        analysis = await self.ai_provider.analyze_channel(channel)
        
        # 4. Generate recommendations
        recommendations = await self.ai_provider.generate_recommendations(analysis)
        analysis.recommendations = recommendations
        
        # 5. Store analysis results
        await self.vector_store_repository.store_analysis_result(analysis)
        
        return analysis

    async def search_similar_content(self, query: str) -> List[Dict]:
        """
        Search for similar content in the vector store
        """
        return await self.vector_store_repository.search_similar_content(query)

    async def get_channel_info(self, channel_id: str) -> Channel:
        return await self.youtube_repository.get_channel_info(channel_id) 