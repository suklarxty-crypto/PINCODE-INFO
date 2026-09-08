# app.py - Pincode Info API
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
    "FF": "full_access"
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
    """Get pincode information"""
    is_valid, result = validate_pincode(pincode)
    
    if not is_valid:
        return {
            "status": "error",
            "message": result,
            "pincode": pincode
        }
    
    pincode_clean = result
    
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode_clean}"
        
        response = requests.get(url, timeout=30)
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
        else:
            return {
                "status": "error",
                "message": "No data found for this pincode",
                "pincode": pincode_clean
            }
            
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timeout",
            "pincode": pincode_clean
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Connection error",
            "pincode": pincode_clean
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Network error: {str(e)}",
            "pincode": pincode_clean
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid response format",
            "pincode": pincode_clean
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "pincode": pincode_clean
        }

def format_pincode_response(data):
    """Format pincode data"""
    if not data:
        return None
    
    pincode_data = data.get('data', {})
    
    # Basic Info
    basic = {}
    basic['status'] = pincode_data.get('Status', 'N/A')
    basic['message'] = pincode_data.get('Message', 'N/A')
    basic['total_offices'] = len(pincode_data.get('PostOffice', []))
    
    # Post Offices
    post_offices = []
    for po in pincode_data.get('PostOffice', []):
        office = {
            'name': po.get('Name', 'N/A'),
            'branch_type': po.get('BranchType', 'N/A'),
            'delivery_status': po.get('DeliveryStatus', 'N/A'),
            'circle': po.get('Circle', 'N/A'),
            'district': po.get('District', 'N/A'),
            'division': po.get('Division', 'N/A'),
            'region': po.get('Region', 'N/A'),
            'block': po.get('Block', 'N/A'),
            'state': po.get('State', 'N/A'),
            'country': po.get('Country', 'N/A'),
            'pincode': po.get('Pincode', 'N/A')
        }
        post_offices.append(office)
    
    # Statistics
    stats = {}
    branch_types = {}
    delivery_status = {}
    districts = {}
    states = {}
    
    for po in pincode_data.get('PostOffice', []):
        branch = po.get('BranchType', 'Unknown')
        branch_types[branch] = branch_types.get(branch, 0) + 1
        
        delivery = po.get('DeliveryStatus', 'Unknown')
        delivery_status[delivery] = delivery_status.get(delivery, 0) + 1
        
        district = po.get('District', 'Unknown')
        districts[district] = districts.get(district, 0) + 1
        
        state = po.get('State', 'Unknown')
        states[state] = states.get(state, 0) + 1
    
    stats['branch_types'] = branch_types
    stats['delivery_status'] = delivery_status
    stats['districts'] = districts
    stats['states'] = states
    
    return {
        "basic": basic,
        "statistics": stats,
        "post_offices": post_offices
    }

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
    Get pincode information
    Example: /pincode?code=110001&key=your_api_key
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
        formatted_data = format_pincode_response(result)
        
        return jsonify({
            "status": "success",
            "pincode": pincode,
            "data": formatted_data,
            "timestamp": result['timestamp'],
            "credit": {
                "username": "@KINGFFAIAK47x",
                "made_by": "ANSH AFT"
            }
        })
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
    print("📮 PINCODE INFO API")
    print("=" * 50)
    print("🚀 Running on: http://localhost:5000")
    print("\n🔑 Keys: AFT, FF")
    print("\n📌 ONLY 1 ENDPOINT:")
    print("  GET /pincode?code=110001&key=your_api_key")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=port, debug=True)
