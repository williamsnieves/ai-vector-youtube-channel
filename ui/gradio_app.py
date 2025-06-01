import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gradio as gr
import asyncio
from typing import List, Dict
from src.core.infrastructure.repositories.youtube_repository import YouTubeRepositoryImpl
from src.core.infrastructure.repositories.vector_store_repository import VectorStoreRepositoryImpl
from src.core.infrastructure.repositories.social_media_repositories import InstagramRepositoryImpl, TwitterRepositoryImpl
from src.core.infrastructure.ai_providers.openai_provider import OpenAIProvider
from src.core.infrastructure.ai_providers.anthropic_provider import AnthropicProvider
from src.core.application.services.youtube_service import YouTubeAnalysisService

# Initialize services
youtube_repo = YouTubeRepositoryImpl()
vector_store_repo = VectorStoreRepositoryImpl()
instagram_repo = InstagramRepositoryImpl()
twitter_repo = TwitterRepositoryImpl()
openai_provider = OpenAIProvider()
anthropic_provider = AnthropicProvider()

# Create service instances for both AI providers
openai_service = YouTubeAnalysisService(
    youtube_repo,
    vector_store_repo,
    openai_provider,
    instagram_repo,
    twitter_repo
)
anthropic_service = YouTubeAnalysisService(
    youtube_repo,
    vector_store_repo,
    anthropic_provider,
    instagram_repo,
    twitter_repo
)

async def analyze_channel(channel_id: str, ai_provider: str) -> tuple[str, str, str, str]:
    service = openai_service if ai_provider == "GPT-4" else anthropic_service
    analysis = await service.analyze_channel(channel_id)
    
    return (
        analysis.summary,
        "\n".join(analysis.recommendations),
        str(analysis.metrics),
        str(analysis.sentiment_analysis)
    )

async def search_content(query: str) -> tuple[str, str, str]:
    results = await openai_service.search_similar_content(query)
    if not results:
        return (
            "No results found",
            "No Instagram post generated",
            "No Twitter post generated"
        )
    
    # Get the first result's posts
    first_result = results[0]
    return (
        first_result["text"],
        first_result.get("instagram_post", "No Instagram post generated"),
        first_result.get("twitter_post", "No Twitter post generated")
    )

async def publish_to_instagram(post: str, account: str) -> str:
    result = await openai_service.publish_to_instagram(post, account)
    return f"Status: {result['message']}"

async def publish_to_twitter(post: str, account: str) -> str:
    result = await openai_service.publish_to_twitter(post, account)
    return f"Status: {result['message']}"

# Create Gradio interface
with gr.Blocks(title="YouTube Channel Analyzer") as demo:
    gr.Markdown("# YouTube Channel Analyzer")
    gr.Markdown("Analyze your YouTube channel and get AI-powered insights and recommendations.")
    
    with gr.Row():
        with gr.Column():
            channel_id = gr.Textbox(
                label="YouTube Channel ID",
                placeholder="Enter YouTube Channel ID"
            )
            ai_provider = gr.Radio(
                choices=["GPT-4", "Claude"],
                label="AI Provider",
                value="GPT-4"
            )
            analyze_btn = gr.Button("Analyze Channel")
        
        with gr.Column():
            summary = gr.Textbox(label="Analysis Summary", lines=10)
            recommendations = gr.Textbox(label="Recommendations", lines=5)
            metrics = gr.Markdown(label="Metrics")
            sentiment = gr.Markdown(label="Sentiment Analysis")
    
    with gr.Row():
        with gr.Column():
            search_query = gr.Textbox(
                label="Search Similar Content",
                placeholder="Enter your search query"
            )
            search_btn = gr.Button("Search")
        
        with gr.Column():
            search_results = gr.Markdown(label="Search Results")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Instagram Configuration")
            instagram_account = gr.Textbox(
                label="Instagram Account",
                placeholder="Enter Instagram account username (e.g., @your_account)"
            )
            instagram_auth_btn = gr.Button("🔐 Connect Instagram Account")
            instagram_auth_status = gr.Textbox(
                label="Instagram Connection Status",
                value="Not connected",
                interactive=False
            )
            instagram_post = gr.Textbox(
                label="Instagram Post",
                lines=5,
                placeholder="Generated Instagram post will appear here..."
            )
            instagram_publish_btn = gr.Button("📸 Publish to Instagram", interactive=False)
            instagram_status = gr.Textbox(label="Instagram Status", interactive=False)
        
        with gr.Column():
            gr.Markdown("### Twitter (X) Configuration")
            twitter_account = gr.Textbox(
                label="Twitter Account",
                placeholder="Enter Twitter account username (e.g., @your_account)"
            )
            twitter_auth_btn = gr.Button("🔐 Connect Twitter Account")
            twitter_auth_status = gr.Textbox(
                label="Twitter Connection Status",
                value="Not connected",
                interactive=False
            )
            twitter_post = gr.Textbox(
                label="Twitter (X) Post",
                lines=3,
                placeholder="Generated Twitter post will appear here..."
            )
            twitter_publish_btn = gr.Button("🐦 Publish to Twitter", interactive=False)
            twitter_status = gr.Textbox(label="Twitter Status", interactive=False)
    
    # Set up event handlers
    analyze_btn.click(
        fn=analyze_channel,
        inputs=[channel_id, ai_provider],
        outputs=[summary, recommendations, metrics, sentiment]
    )
    
    search_btn.click(
        fn=search_content,
        inputs=[search_query],
        outputs=[search_results, instagram_post, twitter_post]
    )
    
    async def connect_instagram(account: str) -> tuple[str, bool]:
        try:
            # TODO: Implement actual Instagram OAuth flow
            # For now, just return a mock response
            return f"Connected to {account}", True
        except Exception as e:
            return f"Error connecting to Instagram: {str(e)}", False
    
    async def connect_twitter(account: str) -> tuple[str, bool]:
        try:
            # TODO: Implement actual Twitter OAuth flow
            # For now, just return a mock response
            return f"Connected to {account}", True
        except Exception as e:
            return f"Error connecting to Twitter: {str(e)}", False
    
    instagram_auth_btn.click(
        fn=connect_instagram,
        inputs=[instagram_account],
        outputs=[instagram_auth_status, instagram_publish_btn]
    )
    
    twitter_auth_btn.click(
        fn=connect_twitter,
        inputs=[twitter_account],
        outputs=[twitter_auth_status, twitter_publish_btn]
    )
    
    instagram_publish_btn.click(
        fn=publish_to_instagram,
        inputs=[instagram_post, instagram_account],
        outputs=[instagram_status]
    )
    
    twitter_publish_btn.click(
        fn=publish_to_twitter,
        inputs=[twitter_post, twitter_account],
        outputs=[twitter_status]
    )

if __name__ == "__main__":
    demo.launch() 