from flask import Flask, request, jsonify
from flask_cors import CORS
from faqGenerator import main as generate_faq

app = Flask(__name__)
CORS(app)

@app.route('/api/generate-faq', methods=['POST'])
def generate_faq_route():
    if request.method == 'POST':
        url = request.json.get('url')
        if url:
            try:
                faq = generate_faq(url)
                faq_items = faq.split("\n")

                for item in faq_items:
                    if item.startswith('1'):
                        break
                    faq_items.remove(item)
                    
                for item in faq_items:
                    if item == "":
                        faq_items.remove(item)

                return jsonify({'faq': faq_items})
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'URL not provided'}), 400
    else:
        return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)
