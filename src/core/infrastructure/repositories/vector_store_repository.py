from typing import List, Dict
import json
from datetime import datetime
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from ...domain.interfaces import VectorStoreRepository
from ...domain.entities import Channel, AnalysisResult
from config.settings import get_settings
from openai import AsyncOpenAI

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
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

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

    async def search_similar_content(self, query: str) -> List[Dict]:
        try:
            # Search in vector store
            results = self.chroma_client.similarity_search(query, k=1)
            
            if not results:
                return []
            
            # Get the first result
            result = results[0]
            
            # Generate social media posts using GPT-4
            instagram_post = await self._generate_social_media_post(
                result.page_content,
                "instagram",
                "Create an engaging Instagram post to promote this content. Focus on visual appeal and use relevant hashtags. Keep it under 2200 characters."
            )
            
            twitter_post = await self._generate_social_media_post(
                result.page_content,
                "twitter",
                "Create a concise Twitter post to promote this content. Keep it under 280 characters and use relevant hashtags."
            )
            
            return [{
                "text": result.page_content,
                "instagram_post": instagram_post,
                "twitter_post": twitter_post
            }]
            
        except Exception as e:
            logger.error(f"Error searching similar content: {str(e)}")
            return []

    async def _generate_social_media_post(self, content: str, platform: str, prompt: str) -> str:
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert social media marketing strategist for {platform}.
                        Your task is to create engaging content that will drive engagement and followers.
                        Focus on the specific platform's best practices and format.
                        Do not include any headers or labels in your response, just the post content."""
                    },
                    {
                        "role": "user",
                        "content": f"""{prompt}

Content to promote:
{content}"""
                    }
                ]
            )
            
            # Clean up the response
            post = response.choices[0].message.content.strip()
            # Remove any markdown headers or emojis
            post = post.replace("###", "").replace("🟡", "").strip()
            # Remove platform-specific headers
            post = post.replace("Instagram Post:", "").replace("Twitter (X) Post:", "").strip()
            
            return post
            
        except Exception as e:
            logger.error(f"Error generating {platform} post: {str(e)}")
            return f"Error generating {platform} post" 