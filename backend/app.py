from flask import Flask, request, jsonify
from flask_cors import CORS
from faqGenerator import main as faq_generator

app = Flask(__name__)
CORS(app)

@app.route('/generate-faq', methods=['POST'])
def generate_faq_route():
    if request.method == 'POST':
        url = request.json.get('url')
        if url:
            try:
                index = 0
                while True:
                    faq = faq_generator(url)
                    if len(faq) >= 60 or index >= 3:
                        break
                    index += 1
                
                return jsonify({'faq': faq})
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'URL not provided'}), 400
    else:
        return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)
