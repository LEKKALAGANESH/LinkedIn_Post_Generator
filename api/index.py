from flask import Flask, request, jsonify, Response
from openai import OpenAI
import os
import re

app = Flask(__name__)

# Templates
templates = {
    "personal_story": {
        "hook": "I failed at X — and it turned out to be the best thing that happened to my career.",
        "body": "Context: [Describe the situation]\nMistake: [What went wrong]\nLesson: [What I learned]\nTakeaway: [Actionable advice]",
        "cta": "What's one mistake you learned from? I'll read and reply."
    },
    "mini_list": {
        "hook": "5 quick things that improved our onboarding conversion by 30%.",
        "body": "- Tip 1\n- Tip 2\n- Tip 3\n- Tip 4\n- Tip 5",
        "cta": "Want the template? DM me."
    },
    "results_breakdown": {
        "hook": "How we cut support tickets by 42% in 6 weeks.",
        "body": "Problem: [Describe issue]\nApproach: [What we did]\nMetrics: [Results]\nChart: [Suggestion for image]",
        "cta": "If you want the playbook, comment 'playbook'."
    },
    "opinion": {
        "hook": "Opinion: [Controversial statement].",
        "body": "Reason 1: [Explanation]\nReason 2: [Explanation]\nCounterpoint: [Address objection]",
        "cta": "Agree or disagree — what would you do differently?"
    }
}

def get_template(name):
    return templates.get(name, None)

def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def generate_linkedin_post(topic, audience="professionals", goal="educate", tone="professional", length="150-200", keywords="", cta=""):
    system_prompt = """You are an expert LinkedIn content creator. Generate posts that are IMMEDIATELY COPY-PASTE READY for LinkedIn.

CRITICAL FORMATTING RULES:
1. NO markdown formatting (no **, no #, no ---, no headers)
2. NO labels like "LinkedIn Post:" or "Post Draft:"
3. NO word counts or metadata
4. NO "Here's your post:" introductions

LINKEDIN-NATIVE FORMATTING:
- Use short paragraphs (1-2 lines max)
- Add blank lines between paragraphs for readability
- Use simple emojis sparingly (1-3 total, not every line)
- Use → or • or ✓ for bullet points (not markdown dashes)
- Keep the hook in first 140 characters (before "See more" cutoff)
- Place 3-5 hashtags at the very end, separated by spaces

STRUCTURE:
1. Hook (attention-grabbing first line)
2. Body (value, story, or insights with line breaks)
3. Call-to-action (engagement question or prompt)
4. Hashtags (3-5 relevant ones)

Output ONLY the post content. Nothing else."""

    user_prompt = f"""Write a LinkedIn post about: {topic}

Target audience: {audience}
Goal: {goal}
Tone: {tone}
Approximate length: {length} words
Keywords to include: {keywords}
Call-to-action: {cta}

Remember: Output ONLY the ready-to-paste post content."""

    try:
        client = get_client()
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://linkedin-post-generator.app",
                "X-Title": "LinkedIn Post Generator",
            },
            model="anthropic/claude-sonnet-4.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600,
            temperature=0.7,
        )
        post = completion.choices[0].message.content
        if post:
            post = post.strip()
            unwanted_prefixes = ["Here's", "Here is", "LinkedIn Post:", "Post:", "Draft:"]
            for prefix in unwanted_prefixes:
                if post.lower().startswith(prefix.lower()):
                    post = post[len(prefix):].strip()
                    if post.startswith(":"):
                        post = post[1:].strip()
        return post if post else "Error: No content generated."
    except Exception as e:
        return f"Error generating post: {str(e)}"

def generate_hooks(topic, num=5):
    system_prompt = """You are a LinkedIn hook specialist. Generate attention-grabbing opening lines.

RULES:
- Each hook must be under 140 characters (LinkedIn "See more" cutoff)
- NO numbering (no "1.", "2.", etc.)
- NO markdown formatting
- NO quotation marks around hooks
- One hook per line
- Make them punchy, curiosity-inducing, or contrarian
- Mix styles: questions, bold statements, statistics, stories

Output ONLY the hooks, one per line. Nothing else."""

    user_prompt = f"Generate {num} scroll-stopping hooks for a LinkedIn post about: {topic}"

    try:
        client = get_client()
        completion = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.8,
        )
        content = completion.choices[0].message.content
        if content:
            hooks = content.strip().split('\n')
            cleaned_hooks = []
            for h in hooks:
                h = h.strip()
                if h and len(h) > 2:
                    if h[0].isdigit() and h[1] in '.):':
                        h = h[2:].strip()
                    elif h[0].isdigit() and h[1].isdigit() and h[2] in '.):':
                        h = h[3:].strip()
                if h.startswith('-') or h.startswith('•'):
                    h = h[1:].strip()
                if h.startswith('"') and h.endswith('"'):
                    h = h[1:-1]
                if h:
                    cleaned_hooks.append(h)
            return cleaned_hooks[:num] if cleaned_hooks else ["Hook generation failed."]
        return ["Hook generation failed."]
    except Exception as e:
        return [f"Error generating hooks: {str(e)}"]

def suggest_hashtags(topic):
    system_prompt = """You are a LinkedIn hashtag strategist. Generate relevant, high-engagement hashtags.

RULES:
- Return ONLY hashtags, nothing else
- Each hashtag starts with #
- No explanations or descriptions
- Mix: 2-3 broad/popular + 2-3 niche/specific
- All lowercase or CamelCase (e.g., #LinkedInTips or #linkedintips)
- No spaces within hashtags
- 5-7 hashtags total, space-separated on one line

Output format: #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5"""

    user_prompt = f"Generate 5-7 LinkedIn hashtags for a post about: {topic}"

    try:
        client = get_client()
        completion = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=100,
            temperature=0.5,
        )
        content = completion.choices[0].message.content
        if content:
            hashtags = re.findall(r'#\w+', content)
            cleaned = [h for h in hashtags if len(h) > 1][:7]
            return cleaned if cleaned else ["#LinkedIn", "#Networking", "#CareerGrowth"]
        return ["#LinkedIn", "#Networking", "#CareerGrowth"]
    except Exception as e:
        return ["#LinkedIn", "#Networking", "#CareerGrowth"]

def generate_carousel(topic, slides=5):
    system_prompt = """You are a LinkedIn carousel content creator. Generate slide content that's ready to copy into Canva or any design tool.

FORMAT FOR EACH SLIDE:
SLIDE 1: [Title]
• Point 1
• Point 2
• Point 3

RULES:
- Use "SLIDE X:" format for each slide
- First slide = Hook/Title slide (attention-grabbing headline only)
- Last slide = CTA slide (follow prompt + key takeaway)
- Middle slides = Value content (headline + 2-3 bullet points)
- Keep headlines under 10 words
- Keep bullet points under 15 words each
- NO markdown formatting (no **, no #)
- Use • for bullet points
- Add blank line between slides

Output ONLY the slide content. No introductions or explanations."""

    user_prompt = f"Create a {slides}-slide LinkedIn carousel about: {topic}"

    try:
        client = get_client()
        completion = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        content = completion.choices[0].message.content
        return content.strip() if content else "Error generating carousel content."
    except Exception as e:
        return f"Error generating carousel: {str(e)}"

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# HTML template embedded
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Post Generator</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: rgba(26, 26, 36, 0.8);
            --bg-glass: rgba(255, 255, 255, 0.03);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-focus: rgba(99, 102, 241, 0.5);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-primary: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            --success: #10b981;
            --error: #ef4444;
            --radius-md: 12px;
            --radius-xl: 24px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }
        .bg-gradient {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 102, 241, 0.15), transparent);
            pointer-events: none;
        }
        .container { position: relative; max-width: 1400px; margin: 0 auto; padding: 24px; }
        header { text-align: center; padding: 48px 0 40px; }
        h1 {
            font-size: 2.5rem;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { color: var(--text-secondary); margin-top: 8px; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
        @media (max-width: 1024px) { .main-grid { grid-template-columns: 1fr; } }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-xl);
            padding: 32px;
        }
        .card-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 8px; }
        input, select, textarea {
            width: 100%;
            padding: 14px 16px;
            background: var(--bg-glass);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            font-family: inherit;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--border-focus);
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .submit-btn {
            width: 100%;
            padding: 16px;
            background: var(--accent-gradient);
            border: none;
            border-radius: var(--radius-md);
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        .submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }
        .output-section { margin-bottom: 24px; }
        .output-label { font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px; }
        .output-content {
            background: var(--bg-glass);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 20px;
            white-space: pre-wrap;
        }
        .copy-btn {
            background: var(--bg-glass);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px 16px;
            color: var(--text-secondary);
            cursor: pointer;
            margin-top: 12px;
        }
        .copy-btn:hover { border-color: var(--accent-primary); color: var(--accent-primary); }
        .hashtag {
            display: inline-block;
            background: rgba(0, 119, 181, 0.15);
            color: #0077b5;
            padding: 6px 12px;
            border-radius: 20px;
            margin: 4px;
            font-size: 0.85rem;
        }
        .hook-item {
            background: rgba(99, 102, 241, 0.05);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
        }
        .hook-item:hover { background: rgba(99, 102, 241, 0.1); }
        .error { color: var(--error); }
        .spinner {
            width: 20px; height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: inline-block;
            margin-right: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    <div class="container">
        <header>
            <h1>LinkedIn Post Generator</h1>
            <p class="subtitle">Create engaging LinkedIn content with AI</p>
        </header>
        <main class="main-grid">
            <section class="card">
                <h2 class="card-title">Create Your Post</h2>
                <form id="postForm">
                    <div class="form-group">
                        <label>Topic *</label>
                        <input type="text" id="topic" placeholder="e.g., AI product management" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Target Audience</label>
                            <input type="text" id="audience" placeholder="e.g., startup founders" value="professionals">
                        </div>
                        <div class="form-group">
                            <label>Goal</label>
                            <select id="goal">
                                <option value="educate">Educate</option>
                                <option value="engage">Engage</option>
                                <option value="inspire">Inspire</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Tone</label>
                            <select id="tone">
                                <option value="professional">Professional</option>
                                <option value="casual">Casual</option>
                                <option value="inspirational">Inspirational</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Word Count</label>
                            <input type="number" id="length" value="150" min="50" max="500">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Keywords (comma-separated)</label>
                        <input type="text" id="keywords" placeholder="e.g., AI, productivity">
                    </div>
                    <div class="form-group">
                        <label>Call to Action</label>
                        <input type="text" id="cta" placeholder="e.g., Share your thoughts!">
                    </div>
                    <button type="submit" class="submit-btn" id="submitBtn">Generate Post</button>
                </form>
            </section>
            <section class="card">
                <h2 class="card-title">Generated Content</h2>
                <div id="output">
                    <p style="color: var(--text-muted); text-align: center; padding: 40px;">
                        Fill in the form and click Generate to create your post
                    </p>
                </div>
            </section>
        </main>
    </div>
    <script>
        document.getElementById('postForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const output = document.getElementById('output');

            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Generating...';
            output.innerHTML = '<p style="text-align:center;color:var(--text-muted)">Generating your post...</p>';

            const data = {
                post_type: 'text',
                topic: document.getElementById('topic').value,
                audience: document.getElementById('audience').value,
                goal: document.getElementById('goal').value,
                tone: document.getElementById('tone').value,
                length: parseInt(document.getElementById('length').value),
                keywords: document.getElementById('keywords').value,
                cta: document.getElementById('cta').value
            };

            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await res.json();

                if (result.error) {
                    output.innerHTML = `<p class="error">${result.error}</p>`;
                } else {
                    let html = '';
                    if (result.post) {
                        html += `
                            <div class="output-section">
                                <div class="output-label">YOUR POST</div>
                                <div class="output-content" id="postContent">${result.post}</div>
                                <button class="copy-btn" onclick="copyText('postContent')">Copy Post</button>
                            </div>`;
                    }
                    if (result.hooks && result.hooks.length) {
                        html += `<div class="output-section"><div class="output-label">ALTERNATIVE HOOKS</div>`;
                        result.hooks.forEach(h => {
                            html += `<div class="hook-item" onclick="navigator.clipboard.writeText(this.innerText)">${h}</div>`;
                        });
                        html += '</div>';
                    }
                    if (result.hashtags && result.hashtags.length) {
                        html += `<div class="output-section"><div class="output-label">HASHTAGS</div><div>`;
                        result.hashtags.forEach(t => {
                            html += `<span class="hashtag">${t}</span>`;
                        });
                        html += '</div></div>';
                    }
                    output.innerHTML = html;
                }
            } catch (err) {
                output.innerHTML = `<p class="error">Error: ${err.message}</p>`;
            }

            btn.disabled = false;
            btn.textContent = 'Generate Post';
        });

        function copyText(id) {
            const text = document.getElementById(id).innerText;
            navigator.clipboard.writeText(text);
            alert('Copied to clipboard!');
        }
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return Response(HTML_TEMPLATE, mimetype='text/html')

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        post_type = data.get('post_type', 'text')
        topic = data.get('topic', '').strip()
        audience = data.get('audience', 'professionals').strip() or 'professionals'
        goal = data.get('goal', 'educate').strip() or 'educate'
        tone = data.get('tone', 'professional')
        length = data.get('length', 150)
        keywords = data.get('keywords', [])
        cta = data.get('cta', '').strip()

        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        keywords_str = ', '.join(keywords) if keywords else ''

        if post_type == 'text':
            if not topic:
                return jsonify({'error': 'Topic is required'}), 400
            post = generate_linkedin_post(topic, audience, goal, tone, length, keywords_str, cta)
            hooks = generate_hooks(topic)
            hashtags = suggest_hashtags(topic)
            return jsonify({'post': post, 'hooks': hooks, 'hashtags': hashtags, 'success': True})

        elif post_type == 'carousel':
            if not topic:
                return jsonify({'error': 'Topic is required'}), 400
            slides = generate_carousel(topic)
            return jsonify({'slides': slides, 'success': True})

        elif post_type == 'template':
            template_name = data.get('template_name', 'personal_story')
            template = get_template(template_name)
            if template is None:
                return jsonify({'error': f'Template "{template_name}" not found'}), 404
            return jsonify({'template': template, 'success': True})

        return jsonify({'error': 'Invalid post type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/templates')
def list_templates():
    return jsonify({'templates': list(templates.keys()), 'success': True})
