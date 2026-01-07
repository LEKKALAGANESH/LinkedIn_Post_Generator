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

# Try to load external template file, fall back to embedded
HTML_TEMPLATE = ''
try:
    import os
    # Try multiple paths for different environments
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'index.html'),
        os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html'),
        'templates/index.html',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                HTML_TEMPLATE = f.read()
            break
except:
    pass

# Fallback: embedded template for serverless environments
if not HTML_TEMPLATE:
    HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Post Generator | AI-Powered Content Creation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root{--bg-primary:#0a0a0f;--bg-secondary:#12121a;--bg-tertiary:#1a1a24;--bg-card:rgba(26,26,36,0.8);--bg-glass:rgba(255,255,255,0.03);--border-color:rgba(255,255,255,0.08);--border-focus:rgba(99,102,241,0.5);--text-primary:#f8fafc;--text-secondary:#94a3b8;--text-muted:#64748b;--accent-primary:#6366f1;--accent-secondary:#8b5cf6;--accent-gradient:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#a855f7 100%);--success:#10b981;--error:#ef4444;--linkedin-blue:#0077b5;--radius-sm:8px;--radius-md:12px;--radius-xl:24px;--shadow-glow:0 0 40px rgba(99,102,241,0.15);--transition-fast:150ms ease;--transition-normal:250ms ease}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg-primary);color:var(--text-primary);line-height:1.6;min-height:100vh;overflow-x:hidden}
        .bg-gradient{position:fixed;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse 80% 50% at 50% -20%,rgba(99,102,241,0.15),transparent),radial-gradient(ellipse 60% 40% at 100% 50%,rgba(139,92,246,0.1),transparent),radial-gradient(ellipse 60% 40% at 0% 80%,rgba(168,85,247,0.08),transparent);pointer-events:none;z-index:0}
        .container{position:relative;z-index:1;max-width:1400px;margin:0 auto;padding:24px}
        header{text-align:center;padding:48px 0 40px}
        .logo{display:inline-flex;align-items:center;gap:12px;margin-bottom:16px}
        .logo-icon{width:48px;height:48px;background:var(--accent-gradient);border-radius:var(--radius-md);display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow-glow)}
        .logo-icon svg{width:28px;height:28px;color:white}
        h1{font-size:clamp(1.75rem,4vw,2.5rem);font-weight:700;background:var(--accent-gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.02em}
        .subtitle{color:var(--text-secondary);font-size:1.1rem;margin-top:8px;max-width:500px;margin-left:auto;margin-right:auto}
        .main-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start}
        @media(max-width:1024px){.main-grid{grid-template-columns:1fr}}
        .card{background:var(--bg-card);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--border-color);border-radius:var(--radius-xl);padding:32px;box-shadow:0 4px 16px rgba(0,0,0,0.4)}
        .card-header{display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid var(--border-color)}
        .card-icon{width:40px;height:40px;background:var(--bg-glass);border:1px solid var(--border-color);border-radius:var(--radius-md);display:flex;align-items:center;justify-content:center;color:var(--accent-primary)}
        .card-title{font-size:1.25rem;font-weight:600}
        .post-type-selector{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px}
        .post-type-btn{background:var(--bg-glass);border:1px solid var(--border-color);border-radius:var(--radius-md);padding:16px 12px;cursor:pointer;transition:all var(--transition-normal);text-align:center}
        .post-type-btn:hover{background:rgba(99,102,241,0.1);border-color:rgba(99,102,241,0.3)}
        .post-type-btn.active{background:rgba(99,102,241,0.15);border-color:var(--accent-primary);box-shadow:0 0 20px rgba(99,102,241,0.2)}
        .post-type-btn .icon{width:32px;height:32px;margin:0 auto 8px;color:var(--text-secondary);transition:color var(--transition-fast)}
        .post-type-btn.active .icon,.post-type-btn:hover .icon{color:var(--accent-primary)}
        .post-type-btn .label{font-size:0.875rem;font-weight:500;color:var(--text-secondary);transition:color var(--transition-fast)}
        .post-type-btn.active .label,.post-type-btn:hover .label{color:var(--text-primary)}
        .form-group{margin-bottom:20px}
        .form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
        @media(max-width:640px){.form-row{grid-template-columns:1fr}}
        label{display:block;font-size:0.875rem;font-weight:500;color:var(--text-secondary);margin-bottom:8px}
        input[type="text"],input[type="number"],select,textarea{width:100%;padding:14px 16px;background:var(--bg-glass);border:1px solid var(--border-color);border-radius:var(--radius-md);color:var(--text-primary);font-family:inherit;font-size:0.95rem;transition:all var(--transition-fast)}
        input::placeholder,textarea::placeholder{color:var(--text-muted)}
        input:focus,select:focus,textarea:focus{outline:none;border-color:var(--border-focus);background:rgba(99,102,241,0.05);box-shadow:0 0 0 3px rgba(99,102,241,0.1)}
        select{cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;padding-right:40px}
        select option{background:var(--bg-secondary);color:var(--text-primary)}
        .template-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:8px}
        @media(max-width:640px){.template-grid{grid-template-columns:1fr}}
        .template-card{background:var(--bg-glass);border:1px solid var(--border-color);border-radius:var(--radius-md);padding:16px;cursor:pointer;transition:all var(--transition-normal)}
        .template-card:hover{background:rgba(99,102,241,0.08);border-color:rgba(99,102,241,0.3);transform:translateY(-2px)}
        .template-card.selected{background:rgba(99,102,241,0.12);border-color:var(--accent-primary)}
        .template-card h4{font-size:0.9rem;font-weight:600;margin-bottom:6px;display:flex;align-items:center;gap:8px}
        .template-card p{font-size:0.8rem;color:var(--text-muted);line-height:1.4}
        .submit-btn{width:100%;padding:16px 24px;background:var(--accent-gradient);border:none;border-radius:var(--radius-md);color:white;font-family:inherit;font-size:1rem;font-weight:600;cursor:pointer;transition:all var(--transition-normal);display:flex;align-items:center;justify-content:center;gap:10px;margin-top:28px;box-shadow:0 4px 20px rgba(99,102,241,0.3)}
        .submit-btn:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 6px 30px rgba(99,102,241,0.4)}
        .submit-btn:disabled{opacity:0.7;cursor:not-allowed}
        .submit-btn svg{width:20px;height:20px}
        .spinner{width:20px;height:20px;border:2px solid rgba(255,255,255,0.3);border-top-color:white;border-radius:50%;animation:spin 0.8s linear infinite}
        @keyframes spin{to{transform:rotate(360deg)}}
        .output-panel{position:sticky;top:24px}
        .output-empty{text-align:center;padding:60px 20px;color:var(--text-muted)}
        .output-empty svg{width:64px;height:64px;margin-bottom:16px;opacity:0.5}
        .output-empty h3{font-size:1.1rem;font-weight:500;margin-bottom:8px;color:var(--text-secondary)}
        .output-section{margin-bottom:24px;animation:fadeIn 0.4s ease}
        @keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
        .output-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
        .output-label{font-size:0.85rem;font-weight:600;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.05em;display:flex;align-items:center;gap:8px}
        .output-label svg{width:16px;height:16px;color:var(--accent-primary)}
        .copy-btn{background:var(--bg-glass);border:1px solid var(--border-color);border-radius:var(--radius-sm);padding:8px 12px;color:var(--text-secondary);font-size:0.8rem;font-weight:500;cursor:pointer;transition:all var(--transition-fast);display:flex;align-items:center;gap:6px}
        .copy-btn:hover{background:rgba(99,102,241,0.1);border-color:var(--accent-primary);color:var(--accent-primary)}
        .copy-btn.copied{background:rgba(16,185,129,0.1);border-color:var(--success);color:var(--success)}
        .copy-btn svg{width:14px;height:14px}
        .copy-all-btn{width:100%;padding:14px 20px;background:var(--accent-gradient);border:none;border-radius:var(--radius-md);color:white;font-family:inherit;font-size:0.95rem;font-weight:600;cursor:pointer;transition:all var(--transition-normal);display:flex;align-items:center;justify-content:center;gap:10px;box-shadow:0 4px 15px rgba(99,102,241,0.25)}
        .copy-all-btn:hover{transform:translateY(-2px);box-shadow:0 6px 25px rgba(99,102,241,0.35)}
        .copy-all-btn svg{width:18px;height:18px}
        .output-hint{font-size:0.75rem;color:var(--text-muted);font-style:italic}
        .output-content{background:var(--bg-glass);border:1px solid var(--border-color);border-radius:var(--radius-md);padding:20px}
        .post-preview{white-space:pre-wrap;line-height:1.7;font-size:0.95rem}
        .hooks-list{display:flex;flex-direction:column;gap:10px}
        .hook-item{background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.2);border-radius:var(--radius-sm);padding:12px 16px;font-size:0.9rem;display:flex;align-items:flex-start;gap:10px;cursor:pointer;transition:all var(--transition-fast)}
        .hook-item:hover{background:rgba(99,102,241,0.1);border-color:var(--accent-primary)}
        .hook-number{background:var(--accent-gradient);color:white;font-size:0.75rem;font-weight:600;padding:2px 8px;border-radius:4px;flex-shrink:0}
        .hashtags-container{display:flex;flex-wrap:wrap;gap:8px}
        .hashtag{background:rgba(0,119,181,0.15);border:1px solid rgba(0,119,181,0.3);color:var(--linkedin-blue);padding:8px 14px;border-radius:20px;font-size:0.85rem;font-weight:500;cursor:pointer;transition:all var(--transition-fast)}
        .hashtag:hover{background:rgba(0,119,181,0.25);transform:scale(1.05)}
        .template-preview{background:var(--bg-tertiary);border-radius:var(--radius-md);overflow:hidden}
        .template-section{padding:16px 20px;border-bottom:1px solid var(--border-color)}
        .template-section:last-child{border-bottom:none}
        .template-section-label{font-size:0.75rem;font-weight:600;color:var(--accent-primary);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px}
        .template-section-content{color:var(--text-secondary);font-size:0.9rem;line-height:1.5}
        .toast{position:fixed;bottom:24px;right:24px;background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:var(--radius-md);padding:16px 20px;display:flex;align-items:center;gap:12px;box-shadow:0 8px 32px rgba(0,0,0,0.5);transform:translateY(100px);opacity:0;transition:all var(--transition-normal);z-index:1000}
        .toast.show{transform:translateY(0);opacity:1}
        .toast.success{border-color:var(--success)}
        .toast.error{border-color:var(--error)}
        .toast-icon{width:24px;height:24px}
        .toast.success .toast-icon{color:var(--success)}
        .toast.error .toast-icon{color:var(--error)}
        .skeleton{background:linear-gradient(90deg,var(--bg-glass) 25%,var(--bg-tertiary) 50%,var(--bg-glass) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:var(--radius-sm)}
        @keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
        .skeleton-text{height:16px;margin-bottom:12px}
        .skeleton-text:last-child{width:60%;margin-bottom:0}
        .skeleton-box{height:120px}
        footer{text-align:center;padding:40px 24px;color:var(--text-muted);font-size:0.875rem}
        footer a{color:var(--accent-primary);text-decoration:none}
        footer a:hover{text-decoration:underline}
        @media(max-width:768px){.container{padding:16px}header{padding:32px 0 28px}.card{padding:24px}.post-type-selector{grid-template-columns:1fr}.post-type-btn{display:flex;align-items:center;gap:12px;text-align:left;padding:14px 16px}.post-type-btn .icon{margin:0}.output-panel{position:static}}
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg></div>
                <h1>LinkedIn Post Generator</h1>
            </div>
            <p class="subtitle">Create engaging, professional LinkedIn content with AI-powered assistance</p>
        </header>
        <main class="main-grid">
            <section class="card">
                <div class="card-header">
                    <div class="card-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></div>
                    <h2 class="card-title">Create Your Post</h2>
                </div>
                <form id="postForm">
                    <div class="form-group">
                        <label>Select Post Type</label>
                        <div class="post-type-selector">
                            <button type="button" class="post-type-btn active" data-type="text"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg><span class="label">Text Post</span></button>
                            <button type="button" class="post-type-btn" data-type="carousel"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg><span class="label">Carousel</span></button>
                            <button type="button" class="post-type-btn" data-type="template"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg><span class="label">Template</span></button>
                        </div>
                        <input type="hidden" id="post_type" name="post_type" value="text">
                    </div>
                    <div class="form-group" id="templateSelector" style="display:none;">
                        <label>Choose a Template</label>
                        <div class="template-grid">
                            <div class="template-card" data-template="personal_story"><h4><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>Personal Story</h4><p>Share a failure that became a success lesson</p></div>
                            <div class="template-card" data-template="mini_list"><h4><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>Mini List</h4><p>5 quick tips with actionable takeaways</p></div>
                            <div class="template-card" data-template="results_breakdown"><h4><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>Results Breakdown</h4><p>Share metrics and data-driven insights</p></div>
                            <div class="template-card" data-template="opinion"><h4><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>Hot Take</h4><p>Share a controversial opinion with reasoning</p></div>
                        </div>
                        <input type="hidden" id="template_name" name="template_name" value="">
                    </div>
                    <div class="form-group" id="topicGroup"><label for="topic">What's your topic? *</label><input type="text" id="topic" name="topic" placeholder="e.g., AI product management, remote work tips, career growth" required></div>
                    <div id="textOptions">
                        <div class="form-row"><div class="form-group"><label for="audience">Target Audience</label><input type="text" id="audience" name="audience" placeholder="e.g., startup founders, developers"></div><div class="form-group"><label for="goal">Content Goal</label><select id="goal" name="goal"><option value="educate">Educate</option><option value="engage">Engage</option><option value="inspire">Inspire</option><option value="convert">Convert</option></select></div></div>
                        <div class="form-row"><div class="form-group"><label for="tone">Writing Tone</label><select id="tone" name="tone"><option value="professional">Professional</option><option value="casual">Casual</option><option value="inspirational">Inspirational</option><option value="conversational">Conversational</option><option value="authoritative">Authoritative</option></select></div><div class="form-group"><label for="length">Word Count</label><input type="number" id="length" name="length" value="150" min="50" max="500"></div></div>
                        <div class="form-group"><label for="keywords">Keywords (comma-separated)</label><input type="text" id="keywords" name="keywords" placeholder="e.g., AI, productivity, leadership"></div>
                        <div class="form-group"><label for="cta">Call to Action</label><input type="text" id="cta" name="cta" placeholder="e.g., Share your thoughts in the comments!"></div>
                    </div>
                    <button type="submit" class="submit-btn" id="submitBtn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg><span>Generate Post</span></button>
                </form>
            </section>
            <section class="card output-panel">
                <div class="card-header"><div class="card-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div><h2 class="card-title">Generated Content</h2></div>
                <div id="outputContainer"><div class="output-empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg><h3>Ready to create</h3><p>Fill in the form and click generate to create your LinkedIn post</p></div></div>
            </section>
        </main>
        <footer><p>Built with AI &bull; Powered by Claude &bull; <a href="https://linkedin.com" target="_blank">Open LinkedIn</a></p></footer>
    </div>
    <div class="toast" id="toast"><svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg><span id="toastMessage">Copied to clipboard!</span></div>
    <script>
        const state={postType:'text',selectedTemplate:'',isLoading:false};
        const postForm=document.getElementById('postForm'),postTypeInput=document.getElementById('post_type'),templateNameInput=document.getElementById('template_name'),templateSelector=document.getElementById('templateSelector'),topicGroup=document.getElementById('topicGroup'),textOptions=document.getElementById('textOptions'),outputContainer=document.getElementById('outputContainer'),submitBtn=document.getElementById('submitBtn'),toast=document.getElementById('toast'),toastMessage=document.getElementById('toastMessage');
        document.querySelectorAll('.post-type-btn').forEach(btn=>{btn.addEventListener('click',()=>{document.querySelectorAll('.post-type-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');state.postType=btn.dataset.type;postTypeInput.value=state.postType;templateSelector.style.display=state.postType==='template'?'block':'none';textOptions.style.display=state.postType==='text'?'block':'none';topicGroup.style.display=state.postType==='template'?'none':'block';const btnText=submitBtn.querySelector('span');if(state.postType==='text')btnText.textContent='Generate Post';else if(state.postType==='carousel')btnText.textContent='Generate Carousel';else btnText.textContent='Get Template';});});
        document.querySelectorAll('.template-card').forEach(card=>{card.addEventListener('click',()=>{document.querySelectorAll('.template-card').forEach(c=>c.classList.remove('selected'));card.classList.add('selected');state.selectedTemplate=card.dataset.template;templateNameInput.value=state.selectedTemplate;});});
        postForm.addEventListener('submit',async(e)=>{e.preventDefault();if(state.isLoading)return;if(state.postType==='template'&&!state.selectedTemplate){showToast('Please select a template','error');return;}if(state.postType!=='template'&&!document.getElementById('topic').value.trim()){showToast('Please enter a topic','error');return;}state.isLoading=true;setLoadingState(true);showSkeleton();const formData=new FormData(postForm);const data=Object.fromEntries(formData);data.keywords=data.keywords?data.keywords.split(',').map(k=>k.trim()):[];data.length=parseInt(data.length)||150;try{const response=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!response.ok)throw new Error('Generation failed');const result=await response.json();if(result.error)throw new Error(result.error);displayResult(result);showToast('Content generated successfully!','success');}catch(error){displayError(error.message);showToast('Failed to generate content','error');}finally{state.isLoading=false;setLoadingState(false);}});
        function setLoadingState(loading){submitBtn.disabled=loading;submitBtn.innerHTML=loading?'<div class="spinner"></div><span>Generating...</span>':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg><span>Generate Post</span>';}
        function showSkeleton(){outputContainer.innerHTML='<div class="output-section"><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-text"></div><div class="skeleton skeleton-box" style="margin-top:16px;"></div></div>';}
        let currentResult=null;
        function displayResult(result){currentResult=result;let html='';if(result.post&&result.hashtags&&result.hashtags.length){html+='<div class="output-section" style="padding-bottom:0;margin-bottom:16px;"><button class="copy-all-btn" onclick="copyPostWithHashtags()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy Complete Post (with hashtags)</button></div>';}if(result.post){html+='<div class="output-section"><div class="output-header"><span class="output-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Your Post</span><button class="copy-btn" onclick="copyToClipboard(this,\\'post\\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button></div><div class="output-content"><div class="post-preview" id="postContent">'+escapeHtml(result.post)+'</div></div></div>';}if(result.hooks&&result.hooks.length){html+='<div class="output-section"><div class="output-header"><span class="output-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>Alternative Hooks</span><span class="output-hint">Click any hook to copy</span></div><div class="output-content"><div class="hooks-list">';result.hooks.forEach((hook,i)=>{html+='<div class="hook-item" onclick="copyText(\\''+escapeHtml(hook).replace(/'/g,"\\\\'")+'\\')""><span class="hook-number">'+(i+1)+'</span><span>'+escapeHtml(hook)+'</span></div>';});html+='</div></div></div>';}if(result.hashtags&&result.hashtags.length){html+='<div class="output-section"><div class="output-header"><span class="output-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>Hashtags</span><button class="copy-btn" onclick="copyHashtags()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button></div><div class="output-content"><div class="hashtags-container" id="hashtagsContainer">';result.hashtags.forEach(tag=>{html+='<span class="hashtag" onclick="copyText(\\''+tag+'\\')">'+escapeHtml(tag)+'</span>';});html+='</div></div></div>';}if(result.slides){html+='<div class="output-section"><div class="output-header"><span class="output-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>Carousel Slides</span><button class="copy-btn" onclick="copyToClipboard(this,\\'slides\\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button></div><div class="output-content"><div class="post-preview" id="slidesContent">'+escapeHtml(result.slides)+'</div></div></div>';}if(result.template){html+='<div class="output-section"><div class="output-header"><span class="output-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>Template Structure</span><button class="copy-btn" onclick="copyTemplate()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy</button></div><div class="output-content"><div class="template-preview" id="templateContent"><div class="template-section"><div class="template-section-label">Hook</div><div class="template-section-content">'+escapeHtml(result.template.hook||'')+'</div></div><div class="template-section"><div class="template-section-label">Body</div><div class="template-section-content">'+escapeHtml(result.template.body||'')+'</div></div><div class="template-section"><div class="template-section-label">Call to Action</div><div class="template-section-content">'+escapeHtml(result.template.cta||'')+'</div></div></div></div></div>';}outputContainer.innerHTML=html||'<div class="output-empty"><h3>No content generated</h3></div>';}
        function displayError(message){outputContainer.innerHTML='<div class="output-empty" style="color:var(--error);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><h3>Generation Failed</h3><p>'+escapeHtml(message)+'</p></div>';}
        async function copyToClipboard(btn,type){let text='';if(type==='post')text=document.getElementById('postContent')?.textContent||'';else if(type==='slides')text=document.getElementById('slidesContent')?.textContent||'';await copyText(text,btn);}
        async function copyHashtags(){const container=document.getElementById('hashtagsContainer');const hashtags=Array.from(container.querySelectorAll('.hashtag')).map(h=>h.textContent).join(' ');await copyText(hashtags);}
        async function copyPostWithHashtags(){if(!currentResult)return;let fullPost=currentResult.post||'';if(currentResult.hashtags&&currentResult.hashtags.length){const hashtags=currentResult.hashtags.join(' ');if(!fullPost.includes('#'))fullPost=fullPost.trim()+'\\n\\n'+hashtags;}await copyText(fullPost);}
        async function copyTemplate(){const template=document.getElementById('templateContent');const sections=template.querySelectorAll('.template-section');let text='';sections.forEach(section=>{text+=section.querySelector('.template-section-content').textContent+'\\n\\n';});await copyText(text.trim());}
        async function copyText(text,btn=null){try{await navigator.clipboard.writeText(text);if(btn){btn.classList.add('copied');btn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>Copied!';setTimeout(()=>{btn.classList.remove('copied');btn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>Copy';},2000);}showToast('Copied to clipboard!','success');}catch(err){showToast('Failed to copy','error');}}
        function showToast(message,type='success'){toastMessage.textContent=message;toast.className='toast '+type;toast.querySelector('.toast-icon').innerHTML=type==='success'?'<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>':'<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>';toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),3000);}
        function escapeHtml(text){if(!text)return'';const div=document.createElement('div');div.textContent=text;return div.innerHTML;}
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
