# LinkedIn Post Generator

An AI-powered web application that generates professional, engaging LinkedIn content. Create text posts, carousels, and use pre-built templates to streamline your content creation workflow.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black.svg)
![Multi-Provider](https://img.shields.io/badge/AI-Multi--Provider-green.svg)

## Live Demo

[View Live App](https://linkedin-post-generator.vercel.app) *(Update with your Vercel URL)*

## Features

- **Text Post Generation** - Create LinkedIn-ready posts with customizable tone, audience, and goals
- **Hook Generator** - Get 5 attention-grabbing opening lines optimized for LinkedIn's "See more" cutoff
- **Hashtag Suggestions** - AI-generated relevant hashtags (mix of broad and niche)
- **Carousel Creator** - Generate multi-slide content for LinkedIn carousels
- **Post Templates** - Pre-built frameworks for personal stories, lists, results breakdowns, and hot takes
- **Copy-to-Clipboard** - One-click copying for seamless posting to LinkedIn
- **Responsive UI** - Modern dark-themed interface that works on desktop and mobile
- **Multi-Provider Support** - Works with OpenRouter, Google Gemini, and other OpenAI-compatible APIs

## Screenshots

<p align="center">
  <img src="docs/Laptop_1.png" alt="Desktop View - Input Form" width="45%">
  <img src="docs/Laptop_2.png" alt="Desktop View - Generated Content" width="45%">
</p>

<p align="center">
  <img src="docs/Mobile_1.png" alt="Mobile View 1" width="30%">
  <img src="docs/Mobile_2.png" alt="Mobile View 2" width="30%">
  <img src="docs/Mobile_3.png" alt="Mobile View 3" width="30%">
</p>

## Deploy Your Own

### Deploy to Vercel

1. Fork this repository
2. Import to [Vercel](https://vercel.com/new)
3. Add environment variables (see [Environment Variables](#environment-variables) section)
4. Deploy!

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/LEKKALAGANESH/LinkedIn_Post_Generator)

### Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/LEKKALAGANESH/LinkedIn_Post_Generator.git
   cd LinkedIn_Post_Generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   # API Key for your chosen provider
   OPENROUTER_API_KEY=your_api_key_here

   # API Base URL (see Provider Configuration below)
   API_BASE_URL=https://openrouter.ai/api/v1/chat/completions

   # Models to use (comma-separated)
   API_MODELS=anthropic/claude-sonnet-4,google/gemini-2.0-flash-exp:free
   ```

4. **Run the app**
   ```bash
   cd api && python index.py
   ```

5. Open `http://localhost:5000`

## Provider Configuration

This app supports multiple AI providers. Configure your `.env` file based on your provider:

### OpenRouter (Recommended)

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
API_BASE_URL=https://openrouter.ai/api/v1/chat/completions
API_MODELS=anthropic/claude-sonnet-4,google/gemini-2.0-flash-exp:free,meta-llama/llama-3.2-3b-instruct:free
```

Get your API key: [openrouter.ai](https://openrouter.ai/)

### Google Gemini

```env
OPENROUTER_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
API_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
API_MODELS=gemini-2.0-flash,gemini-1.5-flash
```

Get your API key: [Google AI Studio](https://aistudio.google.com/apikey)

### Other OpenAI-Compatible APIs

Any OpenAI-compatible API can be used. Just set:
- `OPENROUTER_API_KEY` - Your API key
- `API_BASE_URL` - The chat completions endpoint
- `API_MODELS` - Comma-separated list of model names

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENROUTER_API_KEY` | Your API key for the chosen provider | Yes | - |
| `API_BASE_URL` | The API endpoint URL | No | `https://openrouter.ai/api/v1/chat/completions` |
| `API_MODELS` | Comma-separated list of models to try (in order) | No | OpenRouter defaults |

### Model Fallback System

The app tries models in order. If one fails (rate limit, credits exhausted), it automatically tries the next. This ensures high availability.

Example with fallbacks:
```env
API_MODELS=anthropic/claude-sonnet-4,google/gemini-2.0-flash-exp:free,meta-llama/llama-3.2-3b-instruct:free
```

## Usage

1. Select your post type: **Text Post**, **Carousel**, or **Template**
2. Enter your topic and customize options (audience, tone, goal, etc.)
3. Click **Generate Post**
4. Copy the generated content directly to LinkedIn

## Project Structure

```
linkedin-post-generator/
├── api/
│   └── index.py          # Flask app with AI integration
├── templates/
│   └── index.html        # UI template (used locally)
├── docs/                  # Screenshots
├── .env                   # Environment configuration (create this)
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── README.md
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| Topic | Main subject of the post | Required |
| Audience | Target readers (e.g., "startup founders") | professionals |
| Goal | Content objective: educate, engage, inspire, convert | educate |
| Tone | Writing style: professional, casual, inspirational, conversational, authoritative | professional |
| Length | Approximate word count (50-500) | 150 |
| Keywords | Comma-separated terms to include | - |
| CTA | Call-to-action prompt | - |

## Available Templates

| Template | Description |
|----------|-------------|
| Personal Story | Share a failure that became a lesson |
| Mini List | 5 quick tips with actionable takeaways |
| Results Breakdown | Share metrics and data-driven insights |
| Hot Take | Controversial opinion with reasoning |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/generate` | POST | Generate content |
| `/templates` | GET | List available templates |

## Tech Stack

- **Runtime**: Python 3.10+ on Vercel Serverless
- **Framework**: Flask
- **AI Providers**: OpenRouter, Google Gemini, or any OpenAI-compatible API
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Vercel

## Dependencies

```
flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
```

## Troubleshooting

### "OPENROUTER_API_KEY environment variable not set"
- Make sure your `.env` file exists in the project root
- Verify the API key is correct and not expired

### "All models failed" error
- Check your API key has credits/quota remaining
- Verify the `API_BASE_URL` is correct for your provider
- Check the `API_MODELS` match your provider's model names
- Look at console logs for `[API ERROR]` messages with details

### Rate limiting errors
- The app has built-in retry logic with exponential backoff
- If persistent, add more fallback models to `API_MODELS`

## Changelog

### v2.0.0 - Multi-Provider Support
- Added support for multiple AI providers (OpenRouter, Gemini, etc.)
- New environment variables: `API_BASE_URL`, `API_MODELS`
- Fixed `.env` file loading (added `python-dotenv` integration)
- Conditional headers (OpenRouter-specific headers only sent to OpenRouter)
- Improved error logging with detailed API error messages
- Model fallback system with exponential backoff retry logic

### v1.x - Initial Release
- Text post generation
- Hook generator
- Hashtag suggestions
- Carousel creator
- Post templates
- Responsive dark-themed UI

## License

This project is for personal and educational use.

## Author

**Ganesh Lekkala** - [GitHub](https://github.com/LEKKALAGANESH)
