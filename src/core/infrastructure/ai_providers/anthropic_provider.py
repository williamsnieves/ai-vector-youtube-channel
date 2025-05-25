from typing import List, Dict
from datetime import datetime
import json
import anthropic
from ...domain.interfaces import AIProvider
from ...domain.entities import Channel, AnalysisResult
from config.settings import get_settings

class AnthropicProvider(AIProvider):
    def __init__(self):
        settings = get_settings()
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

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

        # Get analysis from Claude
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an expert YouTube channel analyst. Please analyze this YouTube channel data and provide:
                    1. A detailed summary of the channel's performance
                    2. Key metrics and trends
                    3. Sentiment analysis of the content
                    
                    Channel Data:
                    {channel_data}"""
                }
            ]
        )

        analysis_text = response.content[0].text

        # Get metrics analysis
        metrics_response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an expert YouTube analytics specialist. Provide detailed metrics analysis in a well-formatted markdown structure.
                    Include sections for:
                    - Overall Performance Metrics
                    - Engagement Metrics
                    - Growth Metrics
                    - Content Performance
                    
                    Use markdown formatting with headers, bullet points, and tables where appropriate.
                    Include specific numbers and percentages.
                    
                    Channel Data:
                    {channel_data}"""
                }
            ]
        )

        # Get sentiment analysis
        sentiment_response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an expert in content sentiment analysis. Provide detailed sentiment analysis in a well-formatted markdown structure.
                    Include sections for:
                    - Overall Sentiment Score
                    - Content Tone Analysis
                    - Emotional Impact
                    - Audience Response Analysis
                    
                    Use markdown formatting with headers, bullet points, and tables where appropriate.
                    Include specific scores and percentages.
                    
                    Channel Data:
                    {channel_data}"""
                }
            ]
        )

        # Parse the analysis into structured format
        return AnalysisResult(
            channel_id=channel.channel_id,
            analysis_date=datetime.now(),
            summary=analysis_text,
            recommendations=[],  # Will be populated by generate_recommendations
            metrics=metrics_response.content[0].text,
            sentiment_analysis=sentiment_response.content[0].text
        )

    async def generate_recommendations(self, analysis: AnalysisResult) -> List[str]:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are an expert YouTube marketing strategist. Based on this channel analysis, provide 5 specific, actionable recommendations for improvement:

                    {analysis.summary}

                    Please format each recommendation as a separate line starting with a number."""
                }
            ]
        )

        recommendations_text = response.content[0].text
        # Split recommendations into a list
        recommendations = [rec.strip() for rec in recommendations_text.split('\n') if rec.strip()]
        
        return recommendations 