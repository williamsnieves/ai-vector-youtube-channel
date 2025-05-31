import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gradio as gr
import asyncio
from typing import List, Dict
from src.core.infrastructure.repositories.youtube_repository import YouTubeRepositoryImpl
from src.core.infrastructure.repositories.vector_store_repository import VectorStoreRepositoryImpl
from src.core.infrastructure.ai_providers.openai_provider import OpenAIProvider
from src.core.infrastructure.ai_providers.anthropic_provider import AnthropicProvider
from src.core.application.services.youtube_service import YouTubeAnalysisService

# Initialize services
youtube_repo = YouTubeRepositoryImpl()
vector_store_repo = VectorStoreRepositoryImpl()
openai_provider = OpenAIProvider()
anthropic_provider = AnthropicProvider()

# Create service instances for both AI providers
openai_service = YouTubeAnalysisService(youtube_repo, vector_store_repo, openai_provider)
anthropic_service = YouTubeAnalysisService(youtube_repo, vector_store_repo, anthropic_provider)

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
    
    # Extract the actual content, removing any markdown headers
    instagram_post = first_result.get("instagram_post", "")
    if instagram_post.startswith("###"):
        instagram_post = instagram_post.replace("### Instagram Post:", "").strip()
    
    twitter_post = first_result.get("twitter_post", "")
    if twitter_post.startswith("###"):
        twitter_post = twitter_post.replace("### Twitter (X) Post:", "").strip()
    
    return (
        first_result["text"],
        instagram_post if instagram_post else "No Instagram post generated",
        twitter_post if twitter_post else "No Twitter post generated"
    )

def publish_to_instagram(post: str) -> str:
    # TODO: Implement Instagram publishing logic
    return f"Post published to Instagram:\n{post}"

def publish_to_twitter(post: str) -> str:
    # TODO: Implement Twitter publishing logic
    return f"Post published to Twitter:\n{post}"

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
            instagram_post = gr.Textbox(
                label="Instagram Post",
                lines=5,
                placeholder="Generated Instagram post will appear here..."
            )
            instagram_publish_btn = gr.Button("📸 Publish to Instagram")
            instagram_status = gr.Textbox(label="Instagram Status", interactive=False)
        
        with gr.Column():
            twitter_post = gr.Textbox(
                label="Twitter (X) Post",
                lines=3,
                placeholder="Generated Twitter post will appear here..."
            )
            twitter_publish_btn = gr.Button("🐦 Publish to Twitter")
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
    
    instagram_publish_btn.click(
        fn=publish_to_instagram,
        inputs=[instagram_post],
        outputs=[instagram_status]
    )
    
    twitter_publish_btn.click(
        fn=publish_to_twitter,
        inputs=[twitter_post],
        outputs=[twitter_status]
    )

if __name__ == "__main__":
    demo.launch() 