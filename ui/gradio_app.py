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

async def search_content(query: str) -> List[Dict]:
    results = await openai_service.search_similar_content(query)
    return results

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
            search_results = gr.JSON(label="Search Results")
    
    # Set up event handlers
    analyze_btn.click(
        fn=analyze_channel,
        inputs=[channel_id, ai_provider],
        outputs=[summary, recommendations, metrics, sentiment]
    )
    
    search_btn.click(
        fn=search_content,
        inputs=[search_query],
        outputs=[search_results]
    )

if __name__ == "__main__":
    demo.launch() 