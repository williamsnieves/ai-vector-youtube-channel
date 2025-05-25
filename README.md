# YouTube Channel Analyzer

An AI-powered tool for analyzing YouTube channels and providing marketing insights using GPT-4 and Claude AI models.

## Features

- YouTube channel analysis using the YouTube Data API
- AI-powered insights and recommendations using GPT-4 and Claude
- Vector database storage using Chroma for semantic search
- Modern web interface built with Gradio
- Clean architecture following SOLID principles

## Prerequisites

- Python 3.8+
- YouTube Data API key
- OpenAI API key
- Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-channel-analyzer.git
cd youtube-channel-analyzer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Usage

1. Start the application:
```bash
python ui/gradio_app.py
```

2. Open your web browser and navigate to `http://localhost:7860`

3. Enter a YouTube channel ID and select your preferred AI provider (GPT-4 or Claude)

4. Click "Analyze Channel" to get insights and recommendations

5. Use the search feature to find similar content in the vector database

## Project Structure

```
ai-vector-youtube-channel/
├── src/
│   ├── core/
│   │   ├── domain/
│   │   │   ├── entities.py
│   │   │   └── interfaces.py
│   │   ├── application/
│   │   │   └── services/
│   │   │       └── youtube_service.py
│   │   └── infrastructure/
│   │       ├── repositories/
│   │       │   ├── youtube_repository.py
│   │       │   └── vector_store_repository.py
│   │       └── ai_providers/
│   │           ├── openai_provider.py
│   │           └── anthropic_provider.py
├── ui/
│   └── gradio_app.py
├── config/
│   └── settings.py
├── requirements.txt
└── README.md
```

## Architecture

The project follows a clean architecture approach with the following layers:

1. **Domain Layer**: Contains business entities and interfaces
2. **Application Layer**: Contains business logic and use cases
3. **Infrastructure Layer**: Contains implementations of repositories and external services
4. **UI Layer**: Contains the Gradio web interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 