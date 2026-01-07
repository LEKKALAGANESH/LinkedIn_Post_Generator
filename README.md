# LinkedIn Post Generator

An AI-powered web application that generates professional, engaging LinkedIn content. Create text posts, carousels, and use pre-built templates to streamline your content creation workflow.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web_App-green.svg)
![Claude AI](https://img.shields.io/badge/AI-Claude_Sonnet-purple.svg)

## Features

- **Text Post Generation** - Create LinkedIn-ready posts with customizable tone, audience, and goals
- **Hook Generator** - Get 5 attention-grabbing opening lines optimized for LinkedIn's "See more" cutoff
- **Hashtag Suggestions** - AI-generated relevant hashtags (mix of broad and niche)
- **Carousel Creator** - Generate multi-slide content for LinkedIn carousels
- **Post Templates** - Pre-built frameworks for personal stories, lists, results breakdowns, and hot takes
- **Copy-to-Clipboard** - One-click copying for seamless posting to LinkedIn
- **Responsive UI** - Modern dark-themed interface that works on desktop and mobile

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

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Installation

1. **Clone or download the repository**

2. **Install dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

3. **Configure your API key**

   Create a `.env` file in the project root:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**

   Navigate to `http://localhost:5000`

## Usage

### Web Interface

1. Select your post type: **Text Post**, **Carousel**, or **Template**
2. Enter your topic and customize options (audience, tone, goal, etc.)
3. Click **Generate Post**
4. Copy the generated content directly to LinkedIn

### Command Line

Run the generator directly from terminal for quick posts:

```bash
python linkedin_post_generator.py
```

Follow the prompts to:
- Choose post type (text, carousel, template)
- Enter your topic
- Customize audience, tone, and other options
- Generated posts are saved to the `outputs/` folder

## Project Structure

```
linkedin-post-generator/
├── app.py                    # Flask web server
├── linkedin_post_generator.py # Core generation logic
├── templates.py              # Post template definitions
├── agentic_workflow.py       # Advanced multi-agent workflow (experimental)
├── templates/
│   └── index.html            # Web UI
├── docs/                     # Screenshots
├── outputs/                  # Generated posts (CLI mode)
├── Requirements.txt          # Python dependencies
└── .env                      # API key configuration
```

## Configuration Options

### Post Customization

| Option | Description | Default |
|--------|-------------|---------|
| Topic | Main subject of the post | Required |
| Audience | Target readers (e.g., "startup founders") | professionals |
| Goal | Content objective: educate, engage, inspire, convert | educate |
| Tone | Writing style: professional, casual, inspirational, conversational, authoritative | professional |
| Length | Approximate word count (50-500) | 150 |
| Keywords | Comma-separated terms to include | - |
| CTA | Call-to-action prompt | - |

### Available Templates

- **Personal Story** - Share a failure that became a lesson
- **Mini List** - 5 quick tips with actionable takeaways
- **Results Breakdown** - Share metrics and data-driven insights
- **Hot Take** - Controversial opinion with reasoning

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/generate` | POST | Generate content |
| `/templates` | GET | List available templates |
| `/schedule` | POST | Schedule a post (experimental) |
| `/analytics` | GET | View post analytics (mock data) |

## Tech Stack

- **Backend**: Python, Flask
- **AI Model**: Claude Sonnet 4.5 (via OpenRouter)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Additional Libraries**: python-dotenv, pytz, schedule

## Advanced: Agentic Workflow

The `agentic_workflow.py` module provides an experimental multi-agent system using:

- **LangGraph** - Stateful workflow orchestration
- **CrewAI** - Multi-agent collaboration (Researcher, Writer, Analyst)
- **PydanticAI** - Type-safe validation
- **AutoGen** - Agent debate and consensus

This is designed for more complex content generation pipelines with human-in-the-loop approval.

## License

This project is for personal and educational use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
