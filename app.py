from flask import Flask, render_template, request, jsonify
from linkedin_post_generator import generate_linkedin_post, generate_hooks, suggest_hashtags, generate_carousel, schedule_post, track_analytics
from templates import get_template
import os
import traceback

app = Flask(__name__)

# Enable CORS for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/')
def home():
    return render_template('index.html')

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

        # Handle keywords if passed as string
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]

        # Convert keywords list to string for the generator
        keywords_str = ', '.join(keywords) if keywords else ''

        if post_type == 'text':
            if not topic:
                return jsonify({'error': 'Topic is required for text posts'}), 400

            post = generate_linkedin_post(topic, audience, goal, tone, length, keywords_str, cta)
            hooks = generate_hooks(topic)
            hashtags = suggest_hashtags(topic)

            return jsonify({
                'post': post,
                'hooks': hooks,
                'hashtags': hashtags,
                'success': True
            })

        elif post_type == 'carousel':
            if not topic:
                return jsonify({'error': 'Topic is required for carousel posts'}), 400

            slides = generate_carousel(topic)
            return jsonify({
                'slides': slides,
                'success': True
            })

        elif post_type == 'template':
            template_name = data.get('template_name', 'personal_story')
            if not template_name:
                return jsonify({'error': 'Template name is required'}), 400

            template = get_template(template_name)
            if template is None:
                return jsonify({'error': f'Template "{template_name}" not found'}), 404

            return jsonify({
                'template': template,
                'success': True
            })
        else:
            return jsonify({'error': 'Invalid post type. Use: text, carousel, or template'}), 400

    except Exception as e:
        print(f"Error in generate endpoint: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/schedule', methods=['POST', 'OPTIONS'])
def schedule():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'})

    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        post = data.get('post', '')
        time_str = data.get('time', '')
        timezone = data.get('timezone', 'UTC')

        if not post or not time_str:
            return jsonify({'error': 'Post content and time are required'}), 400

        result = schedule_post(post, time_str, timezone)
        return jsonify({
            'result': result,
            'success': True
        })
    except Exception as e:
        print(f"Error in schedule endpoint: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
def analytics():
    try:
        filename = request.args.get('filename', '')
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400

        analytics_data = track_analytics(filename)
        return jsonify({
            'data': analytics_data,
            'success': True
        })
    except Exception as e:
        print(f"Error in analytics endpoint: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/templates')
def list_templates():
    """Return list of available templates"""
    from templates import templates
    return jsonify({
        'templates': list(templates.keys()),
        'success': True
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
