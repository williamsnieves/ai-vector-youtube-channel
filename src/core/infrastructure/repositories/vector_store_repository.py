from typing import List, Dict
import json
from datetime import datetime
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from ...domain.interfaces import VectorStoreRepository
from ...domain.entities import Channel, AnalysisResult
from config.settings import get_settings

class VectorStoreRepositoryImpl(VectorStoreRepository):
    def __init__(self):
        settings = get_settings()
        self.embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        self.chroma_client = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            embedding_function=self.embeddings
        )
        self.text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def _prepare_channel_text(self, channel: Channel) -> str:
        channel_text = f"""
        Channel Title: {channel.title}
        Description: {channel.description}
        Subscribers: {channel.subscriber_count}
        Total Videos: {channel.video_count}
        
        Videos:
        """
        
        for video in channel.videos:
            channel_text += f"""
            Video: {video.title}
            Description: {video.description}
            Views: {video.view_count}
            Likes: {video.like_count}
            Comments: {video.comment_count}
            Tags: {', '.join(video.tags)}
            Published: {video.published_at}
            """
            
            if video.transcript:
                channel_text += f"Transcript: {video.transcript}\n"
        
        return channel_text

    async def store_channel_data(self, channel: Channel) -> None:
        channel_text = self._prepare_channel_text(channel)
        texts = self.text_splitter.split_text(channel_text)
        
        metadata = {
            "channel_id": channel.channel_id,
            "type": "channel_data",
            "timestamp": datetime.now().isoformat()
        }
        
        metadatas = [metadata] * len(texts)
        
        self.chroma_client.add_texts(
            texts=texts,
            metadatas=metadatas
        )

    async def store_analysis_result(self, result: AnalysisResult) -> None:
        analysis_text = f"""
        Channel Analysis for {result.channel_id}
        Date: {result.analysis_date}
        
        Summary:
        {result.summary}
        
        Recommendations:
        {chr(10).join(result.recommendations)}
        
        Metrics:
        {json.dumps(result.metrics, indent=2)}
        
        Sentiment Analysis:
        {json.dumps(result.sentiment_analysis, indent=2)}
        """
        
        texts = self.text_splitter.split_text(analysis_text)
        
        metadata = {
            "channel_id": result.channel_id,
            "type": "analysis_result",
            "timestamp": result.analysis_date.isoformat()
        }
        
        metadatas = [metadata] * len(texts)
        
        self.chroma_client.add_texts(
            texts=texts,
            metadatas=metadatas
        )

    async def search_similar_content(self, query: str, limit: int = 5) -> List[Dict]:
        results = self.chroma_client.similarity_search_with_score(
            query=query,
            k=limit
        )
        
        return [
            {
                "text": doc.page_content,
                "metadata": doc.metadata
            }
            for doc, _ in results
        ] 