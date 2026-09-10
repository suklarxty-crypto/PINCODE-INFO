# app.py - Pincode Info API (FULLY FIXED - FLAT)
from flask import Flask, request, jsonify
import requests
import json
import time
from functools import wraps
import re
import os

app = Flask(__name__)

# ==============================================
# 📮 PINCODE INFO API
# Made by @KINGFFAIAK47x · ANSH AFT
# ==============================================

# ONLY 2 KEYS
VALID_KEYS = {
    "AFT": "full_access",
}

# ==============================================
# AUTHENTICATION
# ==============================================

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key', '').strip()
        
        if not api_key:
            return jsonify({
                "status": "error",
                "message": "API key required",
                "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
            }), 401
        
        if api_key not in VALID_KEYS:
            return jsonify({
                "status": "error",
                "message": "Invalid API key",
                "credit": {"username": "@KINGFFAIAK47x", "made_by": "ANSH AFT"}
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ==============================================
# PINCODE FUNCTIONS
# ==============================================

def validate_pincode(pincode):
    """Validate pincode"""
    if not pincode:
        return False, "Pincode required"
    
    pincode = pincode.strip()
    
    if not re.match(r'^[0-9]{6}$', pincode):
        return False, "Invalid pincode. Must be 6 digits"
    
    return True, pincode


def get_pincode_info(pincode):
    """
    Get pincode information
    FIXED: Uses HTTP (api.postalpincode.in has SSL issues with HTTPS)
    """
    is_valid, result = validate_pincode(pincode)
    
    if not is_valid:
        return {
            "status": "error",
            "message": result,
            "pincode": pincode
        }
    
    pincode_clean = result
    
    # Try multiple URLs (HTTP first since HTTPS has SSL issues)
    urls = [
        f"http://api.postalpincode.in/pincode/{pincode_clean}",
        f"https://api.postalpincode.in/pincode/{pincode_clean}",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    last_error = None
    
    for url in urls:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=False  # Ignore SSL issues
            )
            response.raise_for_status()
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                if data[0].get('Status') == 'Success':
                    return {
                        "status": "success",
                        "data": data[0],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                else:
                    return {
                        "status": "error",
                        "message": data[0].get('Message', 'No data found'),
                        "pincode": pincode_clean
                    }
        except requests.exceptions.Timeout:
            last_error = "Request timeout"
            continue
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)}"
            continue
        except requests.exceptions.SSLError as e:
            last_error = f"SSL error: {str(e)}"
            continue
        except requests.exceptions.RequestException as e:
            last_error = f"Network error: {str(e)}"
            continue
        except json.JSONDecodeError:
            last_error = "Invalid response format"
            continue
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            continue
    
    return {
        "status": "error",
        "message": last_error or "Failed to fetch pincode data",
        "pincode": pincode_clean
    }


def build_flat_response(result, pincode):
    """
    Build FULLY FLAT response - all top-level fields, no nesting
    Post offices as compact list
    """
    d = result.get('data', {})
    post_offices = d.get('PostOffice', [])
    
    # Aggregate data from all post offices
    districts = set()
    states = set()
    circles = set()
    divisions = set()
    regions = set()
    blocks = set()
    countries = set()
    
    for po in post_offices:
        if po.get('District'): districts.add(po.get('District'))
        if po.get('State'): states.add(po.get('State'))
        if po.get('Circle'): circles.add(po.get('Circle'))
        if po.get('Division'): divisions.add(po.get('Division'))
        if po.get('Region'): regions.add(po.get('Region'))
        if po.get('Block'): blocks.add(po.get('Block'))
        if po.get('Country'): countries.add(po.get('Country'))
    
    # Build office list (compact, one-line per office)
    offices_compact = []
    for po in post_offices:
        offices_compact.append({
            "name": po.get('Name', 'N/A'),
            "branch_type": po.get('BranchType', 'N/A'),
            "delivery_status": po.get('DeliveryStatus', 'N/A'),
            "district": po.get('District', 'N/A'),
            "division": po.get('Division', 'N/A'),
            "region": po.get('Region', 'N/A'),
            "block": po.get('Block', 'N/A'),
            "state": po.get('State', 'N/A')
        })
    
    response = {
        "status": "success",
        "pincode": pincode,
        "api_status": d.get('Status', 'N/A'),
        "api_message": d.get('Message', 'N/A'),
        "total_offices": len(post_offices),
        "districts": list(districts),
        "states": list(states),
        "circles": list(circles),
        "divisions": list(divisions),
        "regions": list(regions),
        "blocks": list(blocks),
        "countries": list(countries),
        "post_offices": offices_compact,
        "timestamp": result.get('timestamp', 'N/A'),
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    }
    
    return response


# ==============================================
# ONLY 1 ENDPOINT
# ==============================================

@app.route('/', methods=['GET'])
def home():
    """API Info"""
    return jsonify({
        "service": "📮 Pincode Info API",
        "version": "2.0.0",
        "description": "Get detailed pincode information",
        "endpoint": {
            "/pincode": {
                "method": "GET",
                "description": "Get pincode information",
                "example": "/pincode?code=110001&key=your_api_key"
            }
        },
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    })


@app.route('/pincode', methods=['GET'])
@require_api_key
def get_pincode():
    """
    Get pincode information - FLAT RESPONSE
    Example: /pincode?code=110001&key=AFT
    """
    pincode = request.args.get('code', '').strip()
    
    if not pincode:
        return jsonify({
            "status": "error",
            "message": "Pincode required",
            "usage": "/pincode?code=110001&key=your_api_key",
            "credit": {
                "username": "@KINGFFAIAK47x",
                "made_by": "ANSH AFT"
            }
        }), 400
    
    result = get_pincode_info(pincode)
    
    if result['status'] == 'success':
        flat = build_flat_response(result, pincode)
        return jsonify(flat)
    else:
        return jsonify({
            "status": "error",
            "message": result.get('message', 'Unknown error'),
            "pincode": result.get('pincode', 'N/A'),
            "credit": {
                "username": "@KINGFFAIAK47x",
                "made_by": "ANSH AFT"
            }
        }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Use /pincode endpoint",
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "credit": {
            "username": "@KINGFFAIAK47x",
            "made_by": "ANSH AFT"
        }
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print("=" * 50)
    print("📮 PINCODE INFO API (FLAT)")
    print("=" * 50)
    print(f"🚀 Running on: http://localhost:{port}")
    print("\n🔑 Key: AFT")
    print("\n📌 ENDPOINT:")
    print("  GET /pincode?code=110001&key=AFT")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=True)
