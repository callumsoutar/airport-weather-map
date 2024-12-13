from flask import Flask, jsonify
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

URL = 'https://www.ifis.airways.co.nz/script/briefing/met_briefing_proc.asp'
LOGIN_URL = 'https://www.ifis.airways.co.nz/secure/script/user_reg/login_proc.asp'

@app.route('/taf/<airport_code>')
def get_taf(airport_code):
    try:
        # Login credentials
        login_payload = {
            'UserName': 'Callum',
            'Password': '21Everest'
        }
        
        # Create a session
        with requests.Session() as session:
            # Login
            session.post(LOGIN_URL, data=login_payload)
            
            # Request TAF data
            data_payload = {
                'TAF': 1,
                'MetLocations': airport_code
            }
            
            response = session.post(URL, data=data_payload)
            
            # Extract TAF using regex
            matches = re.search(r'<span class="metText">(.*?)</span>', response.text, re.DOTALL)
            
            if matches:
                taf_raw = matches.group(1)
                taf_cleaned = re.sub(r'\s+', ' ', taf_raw).strip()
                return jsonify({
                    'success': True,
                    'taf': {
                        airport_code: {
                            'raw_text': taf_cleaned
                        }
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No TAF data found'
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)