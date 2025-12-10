from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Initialize Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- CONFIGURATION ---
# We are trying the specific version number "-002" 
# because the generic alias gave a 404 error.
CURRENT_MODEL = "gemini-1.5-flash-002"
# ---------------------

@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "system": "Autopilot AI",
        "version": "1.2",
        "model_setting": CURRENT_MODEL
    })

@app.route("/check-models", methods=["GET"])
def check_models():
    """
    DIAGNOSTIC TOOL: 
    Click this to see the EXACT names of models your API key can access.
    """
    try:
        available_models = []
        for m in genai.list_models():
            # We only want models that can generate text (content)
            if 'generateContent' in m.supported_generation_methods:
                # Strip the "models/" prefix for cleaner reading
                name = m.name.replace("models/", "")
                available_models.append(name)
        
        return jsonify({
            "success": True,
            "available_models": available_models
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/autopilot/execute", methods=["POST"])
def execute():
    """Single task execution"""
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
        model = genai.GenerativeModel(CURRENT_MODEL)
        response = model.generate_content(prompt)
        
        return jsonify({
            "success": True,
            "result": response.text
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/autopilot/workflow", methods=["POST"])
def workflow():
    """Multi-step workflow execution"""
    try:
        steps = request.json.get("steps", [])
        if not steps:
            return jsonify({"error": "No steps provided"}), 400
        
        model = genai.GenerativeModel(CURRENT_MODEL)
        results = []
        context = ""
        
        for step in steps:
            prompt = step.get("prompt", "")
            if context:
                prompt = f"Context: {context}\n\nTask: {prompt}"
            
            response = model.generate_content(prompt)
            result = response.text
            results.append(result)
            context = result[:500]
        
        return jsonify({
            "success": True,
            "steps_completed": len(results),
            "results": results
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
