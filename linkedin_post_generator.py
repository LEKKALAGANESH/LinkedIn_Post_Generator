
from openai import OpenAI
import os
import datetime
try:
    import schedule
except ImportError:
    schedule = None
import time
import pytz
from templates import get_template
from dotenv import load_dotenv

load_dotenv()

# Check for API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in environment variables")

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

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://linkedin-post-generator.app",
                "X-Title": "LinkedIn Post Generator",
            },
            extra_body={},
            model="anthropic/claude-sonnet-4.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=600,
            temperature=0.7,
        )

        post = completion.choices[0].message.content
        # Clean up any accidental markdown or extra formatting
        if post:
            post = post.strip()
            # Remove common unwanted prefixes
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

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    try:
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
            # Clean each hook
            cleaned_hooks = []
            for h in hooks:
                h = h.strip()
                # Remove numbering like "1.", "1)", "1:"
                if h and len(h) > 2:
                    if h[0].isdigit() and h[1] in '.):':
                        h = h[2:].strip()
                    elif h[0].isdigit() and h[1].isdigit() and h[2] in '.):':
                        h = h[3:].strip()
                # Remove leading dashes or bullets
                if h.startswith('-') or h.startswith('•'):
                    h = h[1:].strip()
                # Remove surrounding quotes
                if h.startswith('"') and h.endswith('"'):
                    h = h[1:-1]
                if h:
                    cleaned_hooks.append(h)
            return cleaned_hooks[:num] if cleaned_hooks else ["Hook generation failed."]
        else:
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

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    try:
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
            # Extract all hashtags from the response
            import re
            hashtags = re.findall(r'#\w+', content)
            # Ensure we have valid hashtags
            cleaned = [h for h in hashtags if len(h) > 1][:7]
            return cleaned if cleaned else ["#LinkedIn", "#Networking", "#CareerGrowth"]
        else:
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

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    try:
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

def schedule_post(post, time_str, timezone="UTC"):
    if schedule is None:
        return "Scheduling feature is not available (schedule library not installed)"

    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)
    post_time = tz.localize(datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M"))
    if post_time > now:
        delay = (post_time - now).total_seconds()
        schedule.every(delay).seconds.do(lambda: print(f"Posting: {post}"))
        return f"Post scheduled for {time_str} in {timezone}."
    else:
        return "Scheduled time is in the past."

def track_analytics(filename):
    # Mock analytics
    import random
    likes = random.randint(10, 100)
    comments = random.randint(5, 50)
    shares = random.randint(1, 20)
    impressions = random.randint(500, 5000)
    engagement_rate = round((likes + comments + shares) / impressions * 100, 2)

    tip = "High engagement! Try similar topics." if likes > 50 else "Consider adding a question or poll next time."

    return {
        'filename': filename,
        'likes': likes,
        'comments': comments,
        'shares': shares,
        'impressions': impressions,
        'engagement_rate': engagement_rate,
        'tip': tip
    }

def main():
    print("LinkedIn Post Generator")
    post_type = input("Choose post type (text, carousel, template): ").lower()
    topic = input("Provide topic: ")
    
    if post_type == "text":
        audience = input("Audience (e.g., professionals): ") or "professionals"
        goal = input("Goal (educate/engage/convert): ") or "educate"
        tone = input("Tone (professional/casual): ") or "professional"
        length = input("Length (150-200): ") or "150-200"
        keywords = input("Keywords: ")
        cta = input("CTA: ")
        post = generate_linkedin_post(topic, audience, goal, tone, length, keywords, cta)
        hooks = generate_hooks(topic)
        hashtags = suggest_hashtags(topic)
        post += "\n\nHooks:\n" + "\n".join(hooks) + "\n\nHashtags: " + " ".join(hashtags)
    elif post_type == "carousel":
        slides = int(input("Number of slides: ") or 5)
        post = generate_carousel(topic, slides)
    elif post_type == "template":
        template_name = input("Template (personal_story, mini_list, results_breakdown, opinion): ")
        template = get_template(template_name)
        if template:
            post = f"{template['hook']}\n\n{template['body']}\n\n{template['cta']}"
        else:
            post = "Template not found."
    else:
        post = "Invalid type."

    # Save to file
    filename = f'outputs/{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
    try:
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(post)
            print(f"Saving post to {filename}...")
    except Exception as e:
        print(f"Error saving: {e}")

    # Scheduler
    schedule_choice = input("Schedule post? (y/n): ").lower()
    if schedule_choice == "y":
        time_str = input("Time (YYYY-MM-DD HH:MM): ")
        timezone = input("Timezone (e.g., UTC): ") or "UTC"
        schedule_post(post, time_str, timezone)
        while True:
            schedule.run_pending()
            time.sleep(1)

    # Analytics
    track_analytics(filename)

if __name__ == "__main__":
    main()
