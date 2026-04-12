from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very scret key'  

# Data storage path
DATA_DIR = 'data'
SCRIPTS_FILE = os.path.join(DATA_DIR, 'scripts.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_scripts():
    """Load all scripts from JSON file"""
    if os.path.exists(SCRIPTS_FILE):
        with open(SCRIPTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scripts(scripts):
    """Save scripts to JSON file"""
    with open(SCRIPTS_FILE, 'w') as f:
        json.dump(scripts, f, indent=2)

@app.route('/')
def index():
    """Redirect to browse page"""
    return redirect(url_for('browse'))

@app.route('/browse')
def browse():
    """Browse all scripts"""
    scripts = load_scripts()
    return render_template('browse.html', scripts=scripts)

@app.route('/new')
def new_script():
    """Create a new script"""
    return render_template('editor.html', script_id=None)

@app.route('/edit/<script_id>')
def edit_script(script_id):
    """Edit an existing script"""
    scripts = load_scripts()
    if script_id not in scripts:
        return redirect(url_for('browse'))
    return render_template('editor.html', script_id=script_id, script=scripts[script_id])

@app.route('/api/scripts', methods=['GET'])
def get_scripts():
    """API endpoint to get all scripts"""
    scripts = load_scripts()
    return jsonify(scripts)

@app.route('/api/scripts/<script_id>', methods=['GET'])
def get_script(script_id):
    """API endpoint to get a specific script"""
    scripts = load_scripts()
    if script_id in scripts:
        return jsonify(scripts[script_id])
    return jsonify({'error': 'Script not found'}), 404

@app.route('/api/scripts', methods=['POST'])
def create_script():
    """API endpoint to create a new script"""
    data = request.json
    scripts = load_scripts()
    
    # Generate new script ID
    script_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
    
    scripts[script_id] = {
        'id': script_id,
        'title': data.get('title', 'Untitled Script'),
        'scenes': data.get('scenes', []),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    save_scripts(scripts)
    return jsonify({'id': script_id, 'script': scripts[script_id]})

@app.route('/api/scripts/<script_id>', methods=['PUT'])
def update_script(script_id):
    """API endpoint to update a script"""
    data = request.json
    scripts = load_scripts()
    
    if script_id not in scripts:
        return jsonify({'error': 'Script not found'}), 404
    
    scripts[script_id]['title'] = data.get('title', scripts[script_id]['title'])
    scripts[script_id]['scenes'] = data.get('scenes', scripts[script_id]['scenes'])
    scripts[script_id]['updated_at'] = datetime.now().isoformat()
    
    save_scripts(scripts)
    return jsonify(scripts[script_id])

@app.route('/api/scripts/<script_id>', methods=['DELETE'])
def delete_script(script_id):
    """API endpoint to delete a script"""
    scripts = load_scripts()
    
    if script_id not in scripts:
        return jsonify({'error': 'Script not found'}), 404
    
    del scripts[script_id]
    save_scripts(scripts)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)