"""Flask REST API. Run from the project root: python -m backend.app."""
import os
from datetime import date
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
FIELDS = ('title', 'description', 'research_area', 'faculty_name', 'department',
          'required_skills', 'available_positions', 'application_deadline', 'status')
LIMITS = {'title': 200, 'description': 10000, 'research_area': 120,
          'faculty_name': 120, 'department': 120, 'required_skills': 2000}


def connect():
    """Open a new connection per operation; credentials never enter source code."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'), port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'portal_user'), password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'research_portal'), charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor, connect_timeout=5,
        read_timeout=10, write_timeout=10, autocommit=False)


def validate(payload):
    """POST/PUT both expect the complete resource; reject silently ignored fields."""
    if not isinstance(payload, dict):
        return {}, {'body': 'Send a JSON object.'}
    errors, clean = {}, {}
    unknown = set(payload) - set(FIELDS)
    if unknown:
        errors['body'] = 'Unknown fields: ' + ', '.join(sorted(unknown))
    for field, maximum in LIMITS.items():
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = 'This field is required and must be text.'
        elif len(value.strip()) > maximum:
            errors[field] = f'Maximum {maximum} characters.'
        else:
            clean[field] = value.strip()
    positions = payload.get('available_positions')
    if type(positions) is not int or not 1 <= positions <= 2147483647:
        errors['available_positions'] = 'Enter a positive whole number (maximum 2147483647).'
    else:
        clean['available_positions'] = positions
    deadline = payload.get('application_deadline')
    try:
        if not isinstance(deadline, str) or len(deadline) != 10:
            raise ValueError
        parsed = date.fromisoformat(deadline)
        if parsed.isoformat() != deadline:
            raise ValueError
        clean['application_deadline'] = deadline
    except (ValueError, TypeError):
        errors['application_deadline'] = 'Enter a valid date as YYYY-MM-DD.'
    status = payload.get('status')
    if status not in ('Open', 'Closed'):
        errors['status'] = 'Choose Open or Closed.'
    else:
        clean['status'] = status
    return clean, errors


def serialize(row):
    if row is None:
        return None
    result = dict(row)
    value = result['application_deadline']
    result['application_deadline'] = value.isoformat() if isinstance(value, date) else value
    return result


def create_app(connection_factory=None):
    app = Flask(__name__, static_folder=None)
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024
    factory = connection_factory or connect

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        # Non-JSON bodies are a validation error rather than Flask's default 415.
        return jsonify(error=error.description), error.code

    @app.errorhandler(Exception)
    def server_error(error):
        app.logger.exception('Request failed')
        return jsonify(error='Internal server error. Check the database connection and server logs.'), 500

    def fetch(identifier=None):
        with factory() as db:
            with db.cursor() as cursor:
                if identifier is None:
                    cursor.execute('SELECT * FROM opportunities ORDER BY id DESC')
                    return [serialize(row) for row in cursor.fetchall()]
                cursor.execute('SELECT * FROM opportunities WHERE id=%s', (identifier,))
                return serialize(cursor.fetchone())

    def valid_id(identifier):
        return len(identifier) <= 10 and identifier.isascii() and identifier.isdigit() and 1 <= int(identifier) <= 4294967295

    @app.get('/')
    def index():
        return send_from_directory(ROOT / 'frontend', 'index.html')

    @app.get('/assets/<path:filename>')
    def assets(filename):
        return send_from_directory(ROOT / 'frontend', filename)

    @app.get('/api/opportunities')
    def all_opportunities():
        return jsonify(fetch()), 200

    @app.post('/api/opportunities')
    def create():
        payload = request.get_json(silent=True) if request.is_json else None
        clean, errors = validate(payload)
        if errors:
            return jsonify(error='Validation failed.', fields=errors), 400
        with factory() as db:
            with db.cursor() as cursor:
                columns = ', '.join(FIELDS)
                placeholders = ', '.join(['%s'] * len(FIELDS))
                cursor.execute(f'INSERT INTO opportunities ({columns}) VALUES ({placeholders})',
                               tuple(clean[field] for field in FIELDS))
                identifier = cursor.lastrowid
                cursor.execute('SELECT * FROM opportunities WHERE id=%s', (identifier,))
                row = serialize(cursor.fetchone())
            db.commit()
        return jsonify(row), 201, {'Location': f'/api/opportunities/{identifier}'}

    @app.route('/api/opportunities/<identifier>', methods=['GET', 'PUT', 'DELETE'])
    def opportunity(identifier):
        if not valid_id(identifier):
            return jsonify(error='ID must be a positive integer.'), 400
        identifier = int(identifier)
        if request.method == 'GET':
            row = fetch(identifier)
            return (jsonify(row), 200) if row else (jsonify(error='Opportunity not found.'), 404)
        clean = None
        if request.method == 'PUT':
            payload = request.get_json(silent=True) if request.is_json else None
            clean, errors = validate(payload)
            if errors:
                return jsonify(error='Validation failed.', fields=errors), 400
        with factory() as db:
            with db.cursor() as cursor:
                # Lock the row so delete/update cannot race the existence check.
                cursor.execute('SELECT * FROM opportunities WHERE id=%s FOR UPDATE', (identifier,))
                if cursor.fetchone() is None:
                    return jsonify(error='Opportunity not found.'), 404
                if request.method == 'DELETE':
                    cursor.execute('DELETE FROM opportunities WHERE id=%s', (identifier,))
                    response = {'message': 'Opportunity deleted.', 'id': identifier}
                else:
                    assignments = ', '.join(f'{field}=%s' for field in FIELDS)
                    cursor.execute(f'UPDATE opportunities SET {assignments} WHERE id=%s',
                                   tuple(clean[field] for field in FIELDS) + (identifier,))
                    cursor.execute('SELECT * FROM opportunities WHERE id=%s', (identifier,))
                    response = serialize(cursor.fetchone())
            db.commit()
        return jsonify(response), 200

    return app


app = create_app()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', '5000')), debug=False)
