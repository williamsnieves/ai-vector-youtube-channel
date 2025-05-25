from typing import List, Dict
from datetime import datetime
import json
from openai import AsyncOpenAI
from ...domain.interfaces import AIProvider
from ...domain.entities import Channel, AnalysisResult
from config.settings import get_settings

class OpenAIProvider(AIProvider):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def analyze_channel(self, channel: Channel) -> AnalysisResult:
        # Prepare channel data for analysis
        channel_data = f"""
        Channel: {channel.title}
        Description: {channel.description}
        Subscribers: {channel.subscriber_count}
        Total Videos: {channel.video_count}
        
        Recent Videos:
        """
        
        for video in channel.videos[:5]:  # Analyze last 5 videos
            channel_data += f"""
            Title: {video.title}
            Views: {video.view_count}
            Likes: {video.like_count}
            Comments: {video.comment_count}
            Tags: {', '.join(video.tags)}
            """

        # Get analysis from GPT-4
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert YouTube channel analyst. Analyze the provided channel data and provide detailed insights."},
                {"role": "user", "content": f"Please analyze this YouTube channel data and provide:\n1. A summary of the channel's performance\n2. Key metrics and trends\n3. Sentiment analysis of the content\n\nChannel Data:\n{channel_data}"}
            ]
        )

        analysis_text = response.choices[0].message.content

        # Get metrics analysis
        metrics_response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert YouTube analytics specialist. Provide detailed metrics analysis in a well-formatted markdown structure."},
                {"role": "user", "content": f"""Analyze these channel metrics and provide a detailed analysis in markdown format.
                Include sections for:
                - Overall Performance Metrics
                - Engagement Metrics
                - Growth Metrics
                - Content Performance
                
                Use markdown formatting with headers, bullet points, and tables where appropriate.
                Include specific numbers and percentages.
                
                Channel Data:
                {channel_data}"""}
            ]
        )

        # Get sentiment analysis
        sentiment_response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert in content sentiment analysis. Provide detailed sentiment analysis in a well-formatted markdown structure."},
                {"role": "user", "content": f"""Analyze the sentiment of this channel's content and provide a detailed analysis in markdown format.
                Include sections for:
                - Overall Sentiment Score
                - Content Tone Analysis
                - Emotional Impact
                - Audience Response Analysis
                
                Use markdown formatting with headers, bullet points, and tables where appropriate.
                Include specific scores and percentages.
                
                Channel Data:
                {channel_data}"""}
            ]
        )

        # Parse the analysis into structured format
        return AnalysisResult(
            channel_id=channel.channel_id,
            analysis_date=datetime.now(),
            summary=analysis_text,
            recommendations=[],  # Will be populated by generate_recommendations
            metrics=metrics_response.choices[0].message.content,
            sentiment_analysis=sentiment_response.choices[0].message.content
        )

    async def generate_recommendations(self, analysis: AnalysisResult) -> List[str]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert YouTube marketing strategist. Provide actionable recommendations based on the channel analysis."},
                {"role": "user", "content": f"Based on this channel analysis, provide 5 specific, actionable recommendations for improvement:\n\n{analysis.summary}"}
            ]
        )

        recommendations_text = response.choices[0].message.content
        # Split recommendations into a list
        recommendations = [rec.strip() for rec in recommendations_text.split('\n') if rec.strip()]
        
        return recommendations 