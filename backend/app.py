from flask import Flask, request, jsonify
from flask_cors import CORS
from faqGenerator import main as faq_generator

app = Flask(__name__)
CORS(app)

@app.route('/generate-faq', methods=['POST'])
def generate_faq_route():
    if request.method == 'POST':
        url = request.json.get('urls')
        if url:
            try:
                # faq = faq_generator(url)
                faq = faq_generator(url)
                if faq == -1:
                    return jsonify({'error': 'There is not any markdown file found in this repository. Please check the URL.'})
                
                return jsonify({'faq': faq})
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'URL not provided'}), 400
    else:
        return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)
