"""
Reddit Response Generator - Agent Alpha
Generates value-first responses for Reddit opportunities
"""
from modules.writer_agent import WriterAgent

def generate_reddit_responses():
    writer = WriterAgent()

    opportunities = [
        {
            'title': 'Idea check: Tool to reverse-engineer competitor video ads',
            'pain': 'UGC creators expensive ($200-500/video), AI tools require prompt engineering skills',
        },
        {
            'title': 'Reddit Ads for Real Estate Tech: Your honest take on ROI',
            'pain': 'Struggling to determine ROI of Reddit ads vs Meta/Google',
        },
        {
            'title': 'How much work do you have to do as a turn-key business owner?',
            'pain': 'Even with team, working 40+ hours, wants passive management',
        }
    ]

    print('='*60)
    print('AGENT ALPHA: Generating Value-First Responses')
    print('='*60)

    responses = []
    for i, opp in enumerate(opportunities, 1):
        prompt = f"""User is asking about: {opp['title']}
Their pain point: {opp['pain']}

Write a helpful Reddit comment that:
1. Shows genuine understanding of their problem
2. Provides actionable advice (2-3 bullet points)
3. Does NOT sound like an ad
4. Subtly mentions that you use AI-powered business reports to automate similar tasks
5. Keep it under 150 words
6. End with a question to encourage dialogue

DO NOT include any links or direct promotions."""

        title_short = opp['title'][:40]
        print(f"\n--- Opportunity {i}: {title_short}... ---")
        
        response = writer.generate_reply(prompt, platform='reddit')
        if isinstance(response, dict):
            text = response.get('reply_content', str(response))
        else:
            text = str(response)
        
        print(text)
        responses.append({'title': opp['title'], 'response': text})
        print()
    
    return responses

if __name__ == "__main__":
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    generate_reddit_responses()
