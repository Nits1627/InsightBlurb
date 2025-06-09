from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from services.data_collector import DataCollector
from services.ai_analyzer import AIAnalyzer
from services.cache_manager import CacheManager
from config import Config

# Initialize app
app = Flask(__name__)
CORS(app)

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core components
data_collector = DataCollector()
ai_analyzer = AIAnalyzer()
cache_manager = CacheManager()

@app.route('/api/analyze-ads', methods=['POST'])
async def analyze_ads():
    try:
        data = request.json
        cache_key = cache_manager.get_cache_key('ads', data)
        cached = cache_manager.get_cached_data(cache_key)
        if cached:
            return jsonify(cached)

        channel_input = data.get('channel_input')
        youtube_data = await data_collector.get_youtube_channel_data(channel_input)

        ads_analysis = {
            'channel_info': youtube_data,
            'total_videos': len(youtube_data.get('videos', [])),
            'total_views': sum(int(v.get('view_count', 0)) for v in youtube_data.get('videos', [])),
        }

        cache_manager.cache_data(cache_key, 'ads', ads_analysis, ttl_hours=6)
        return jsonify(ads_analysis)
    except Exception as e:
        logger.error(f\"Error in analyze_ads: {e}\")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-company', methods=['POST'])
async def analyze_company():
    try:
        data = request.json
        cache_key = cache_manager.get_cache_key('company', data)
        cached = cache_manager.get_cached_data(cache_key)
        if cached:
            return jsonify(cached)

        name = data.get('company_name')
        website = data.get('website')
        tasks = [data_collector.get_company_financial_data(name)]
        if website:
            tasks.append(data_collector.scrape_company_website(website))
        results = await asyncio.gather(*tasks)
        financial_data, website_data = results[0], results[1] if len(results) > 1 else {}

        ai_insights = await ai_analyzer.analyze_company_data({
            'name': name, 'website': website,
            'description': website_data.get('description', ''),
            'industry': financial_data.get('industry', '')
        })

        final_result = {
            'profile': financial_data,
            'web_data': website_data,
            'ai_insights': ai_insights
        }

        cache_manager.cache_data(cache_key, 'company', final_result)
        return jsonify(final_result)
    except Exception as e:
        logger.error(f\"Error in analyze_company: {e}\")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-competitors', methods=['POST'])
async def analyze_competitors():
    try:
        data = request.json
        cache_key = cache_manager.get_cache_key('competitors', data)
        cached = cache_manager.get_cached_data(cache_key)
        if cached:
            return jsonify(cached)

        competitors = await data_collector.search_competitors(data['target_company'], data['industry'])
        recommendations = await ai_analyzer.generate_recommendations({'competitors': competitors})

        result = {
            'competitors': competitors,
            'recommendations': recommendations
        }

        cache_manager.cache_data(cache_key, 'competitors', result, ttl_hours=12)
        return jsonify(result)
    except Exception as e:
        logger.error(f\"Error in analyze_competitors: {e}\")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-market', methods=['POST'])
async def analyze_market():
    try:
        data = request.json
        cache_key = cache_manager.get_cache_key('market', data)
        cached = cache_manager.get_cached_data(cache_key)
        if cached:
            return jsonify(cached)

        result = {
            'industry': data['industry'],
            'region': data['region'],
            'trends': [
                'AI adoption',
                'Subscription economy',
                'Data privacy focus'
            ],
            'forecast': {
                'growth': '12.4% CAGR',
                'opportunities': ['IoT', 'Edge computing', 'Green tech']
            }
        }

        cache_manager.cache_data(cache_key, 'market', result, ttl_hours=48)
        return jsonify(result)
    except Exception as e:
        logger.error(f\"Error in analyze_market: {e}\")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Deep Research API running'})

if __name__ == '__main__':
    app.run(debug=True)