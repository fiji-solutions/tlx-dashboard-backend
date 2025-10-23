import base64

import jwt
import requests
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from coingecko_sol_all import get_coingecko_sol_all, get_coingecko_sol_all_memes, get_coingecko_all_memes
from coingecko_sol import get_market_cap_sums_and_participation
from liquidity import calculate_correlations
from rsps import get_rsps
from prices import get_price_chart
import json
from database import get_db_connection, get_db_cursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from jupiter import get_jupiter_all, get_jupiter
import cryptography.hazmat.primitives.serialization as serialization
from trading_view_experiments import fetch_records_from_experiments, add_record_to_experiments, delete_record_from_experiments

from trw_guy_new_entry import add_data, get_data, delete_data_by_date
from trw_guy import trw_guy_def

app = Flask(__name__)

# Configure CORS to allow all origins
CORS(app, 
     origins="*",
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
)

# Cognito specific configurations from environment variables
COGNITO_REGION = os.getenv('COGNITO_REGION', 'us-east-1')
COGNITO_USERPOOL_ID = os.getenv('COGNITO_USERPOOL_ID', 'your_user_pool_id')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_APP_CLIENT_ID', 'your_client_id')
COGNITO_ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}"

# Helper function to convert JWK to PEM format
def convert_jwk_to_pem(jwk):
    n = base64.urlsafe_b64decode(jwk['n'] + '==')
    e = base64.urlsafe_b64decode(jwk['e'] + '==')

    public_key = rsa.RSAPublicNumbers(
        int.from_bytes(e, byteorder='big'),
        int.from_bytes(n, byteorder='big')
    ).public_key(default_backend())

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

# Caching the public keys
def get_cognito_public_keys():
    response = requests.get(f'{COGNITO_ISSUER}/.well-known/jwks.json')
    keys = response.json()['keys']
    return {key['kid']: key for key in keys}

# Middleware to check token
def token_required(f):
    def wrapper(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            public_keys = get_cognito_public_keys()
            unverified_header = jwt.get_unverified_header(token)
            jwk = public_keys[unverified_header['kid']]

            # Convert JWK to PEM
            rsa_public_key = convert_jwk_to_pem(jwk)

            # Verify the token
            payload = jwt.decode(
                token,
                key=rsa_public_key,
                algorithms=['RS256'],
                audience=COGNITO_APP_CLIENT_ID,
                issuer=COGNITO_ISSUER
            )

            # If valid, continue
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper

# Database connection function is now imported from database.py

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/coin/<coin>', methods=['GET'])
def coin_price(coin):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    response = get_price_chart(start_date, end_date, coin)
    return response

@app.route('/coingecko-sol-all', methods=['GET'])
def coingecko_sol_api():
    response = get_coingecko_sol_all()
    return jsonify(json.loads(response['body']))

@app.route('/coingecko-sol-memes-all', methods=['GET'])
def coingecko_sol_memes_api():
    response = get_coingecko_sol_all_memes()
    return jsonify(json.loads(response['body']))

@app.route('/coingecko-memes-all', methods=['GET'])
def coingecko_memes_api():
    response = get_coingecko_all_memes()
    return jsonify(json.loads(response['body']))

@app.route('/coingecko-sol', methods=['GET'])
def coingecko_sol_range():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        index_start = int(request.args.get('index_start', 0))
        index_end = int(request.args.get('index_end', 9))
        exclude_ids = request.args.get('exclude_ids', '').split(',')

        if not start_date or not end_date:
            return "start_date and end_date are required parameters.", 400

        market_cap_sums, whatever, participation, correlation_data = get_market_cap_sums_and_participation(start_date, end_date, index_start, index_end, exclude_ids, "coingecko")
        response = {
            'market_cap_sums': market_cap_sums,
            'participation': participation,
            'correlation_data': correlation_data
        }
        return jsonify(response)
    except Exception as e:
        print(e)
        return str(e), 500

@app.route('/coingecko-sol-memes', methods=['GET'])
def coingecko_sol_memes_range():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        index_start = int(request.args.get('index_start', 0))
        index_end = int(request.args.get('index_end', 9))
        exclude_ids = request.args.get('exclude_ids', '').split(',')
        correlation_coin_ids = request.args.get('correlation_coin_ids', '').split(',')

        if not start_date or not end_date:
            return "start_date and end_date are required parameters.", 400

        market_cap_sums, market_cap_sums_base_indexed, participation, correlation_data = get_market_cap_sums_and_participation(start_date, end_date, index_start, index_end, exclude_ids, "coingecko-sol-memes", correlation_coin_ids)
        response = {
            'market_cap_sums': market_cap_sums,
            'market_cap_sums_base_indexed': market_cap_sums_base_indexed,
            'participation': participation,
            'correlation_data': correlation_data
        }
        return jsonify(response)
    except Exception as e:
        return str(e), 500

@app.route('/coingecko-memes', methods=['GET'])
def coingecko_memes_range():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        index_start = int(request.args.get('index_start', 0))
        index_end = int(request.args.get('index_end', 9))
        exclude_ids = request.args.get('exclude_ids', '').split(',')
        correlation_coin_ids = request.args.get('correlation_coin_ids', '').split(',')

        if not start_date or not end_date:
            return "start_date and end_date are required parameters.", 400

        market_cap_sums, market_cap_sums_base_indexed, participation, correlation_data = get_market_cap_sums_and_participation(start_date, end_date, index_start, index_end, exclude_ids, "coingecko-memes", correlation_coin_ids)
        response = {
            'market_cap_sums': market_cap_sums,
            'market_cap_sums_base_indexed': market_cap_sums_base_indexed,
            'participation': participation,
            'correlation_data': correlation_data
        }
        return jsonify(response)
    except Exception as e:
        return str(e), 500


@app.route('/rsps', methods=['GET'])
def get_rsps_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_market_cap = request.args.get('min_market_cap')
    max_market_cap = request.args.get('max_market_cap')
    results = int(request.args.get('results'))
    excluded = request.args.get('excluded').split(",")
    return get_rsps(start_date, end_date, max_market_cap, min_market_cap, results, excluded)


@app.route('/new-secret-path', methods=['GET'])
@token_required
def get_liquidity():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db_connection()
    cursor = get_db_cursor(conn)

    query = """
        SELECT * FROM liquidity
        WHERE (record_date BETWEEN %s AND %s) AND (record_index = %s)
        ORDER BY record_date ASC
    """
    cursor.execute(query, (start_date, end_date, "TGA1"))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(records)

@app.route('/tga1', methods=['GET'])
def get_liquidity_free():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db_connection()
    cursor = get_db_cursor(conn)

    query = """
        SELECT * FROM liquidity
        WHERE (record_date BETWEEN %s AND %s) AND (record_index = %s)
        ORDER BY record_date ASC
    """
    cursor.execute(query, (start_date, end_date, "TGA1"))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(records)

@app.route('/new-secret-path2', methods=['GET'])
@token_required
def get_liquidity2():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db_connection()
    cursor = get_db_cursor(conn)

    query = """
        SELECT * FROM liquidity
        WHERE (record_date BETWEEN %s AND %s) AND (record_index = %s)
        ORDER BY record_date ASC
    """
    cursor.execute(query, (start_date, end_date, "TGA2"))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(records)

@app.route('/tga2', methods=['GET'])
def get_liquidity_free2():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = get_db_connection()
    cursor = get_db_cursor(conn)

    query = """
        SELECT * FROM liquidity
        WHERE (record_date BETWEEN %s AND %s) AND (record_index = %s)
        ORDER BY record_date ASC
    """
    cursor.execute(query, (start_date, end_date, "TGA2"))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(records)


@app.route('/liquidity/correlation', methods=['POST'])
def get_liquidity_correlation():
    data = request.get_json()
    return jsonify(calculate_correlations(data.get("liquidity"), data.get("lag"), data.get("ma_length")))


@app.route('/jupiter-all', methods=['GET'])
def jupiter_all():
    response = get_jupiter_all()
    return jsonify(json.loads(response['body']))

@app.route('/jupiter', methods=['GET'])
def jupiter():
    ids = request.args.get('ids', '').split(',')

    response = get_jupiter(ids)
    return jsonify(json.loads(response['body']))

@app.route('/trw-guy-generate', methods=['GET'])
def trw_guy_generate():
    trw_guy_def()
    return jsonify({})

@app.route('/add-data', methods=['POST'])
def trw_guy_add_data():
    data = request.json
    response = add_data(data)
    trw_guy_def()
    return response

@app.route('/delete-data', methods=['DELETE'])
def trw_guy_delete_data():
    data = request.json
    date_value = data.get("date")
    password = data.get("password")

    if not date_value:
        return jsonify({"error": "Date is required"}), 400

    return delete_data_by_date(date_value, password)

@app.route('/get-data', methods=['GET'])
def trw_guy_get_data():
    password = request.args.get('password')
    response = get_data(password)
    return response

@app.route('/trading-view-experiments', methods=['GET'])
def trading_view_experiments():
    indicator = request.args.get('indicator')
    experiment = request.args.get('experiment')
    password = request.args.get('password')
    response = fetch_records_from_experiments(indicator, experiment, password)
    return response

@app.route('/trading-view-experiments-add', methods=['GET'])
def trading_view_experiments_add():
    indicator = request.args.get('indicator')
    experiment = request.args.get('experiment')
    dd = request.args.get('dd')
    intra_dd = request.args.get('intra_dd')
    sortino = request.args.get('sortino')
    sharpe = request.args.get('sharpe')
    profit_factor = request.args.get('profit_factor')
    profitable = request.args.get('profitable')
    trades = request.args.get('trades')
    omega = request.args.get('omega')
    net_profit = request.args.get('net_profit')
    net_profit_ratio = request.args.get('net_profit_ratio')
    parameters = request.args.get('parameters')
    password = request.args.get('password')
    add_record_to_experiments(indicator, experiment, dd, intra_dd, sortino, sharpe, profit_factor, profitable, trades, omega, net_profit, net_profit_ratio, parameters, password)
    return jsonify({})

@app.route('/trading-view-experiments-delete', methods=['GET'])
def trading_view_experiments_delete():
    id = request.args.get('id')
    password = request.args.get('password')
    delete_record_from_experiments(id, password)
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
