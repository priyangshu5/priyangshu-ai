
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import re
import os

app = Flask(__name__)
CORS(app)

class PriyangshuAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.chat_api_url = "https://api.a4f.co/v1/chat/completions"
        self.image_api_url = "https://api.a4f.co/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.models = {
            "general": ["provider-3/gpt-4o-mini", "provider-3/llama-3.3-70b"],
            "coding": ["provider-3/deepseek-v3", "provider-2/codestral-latest"],
            "creative": ["provider-3/llama-3.3-70b", "provider-2/mistral-large-latest"],
            "image": {
                "realistic": "provider-4/imagen-4",
                "artistic": "provider-4/imagen-3",
                "conceptual": "provider-4/qwen-image",
                "default": "provider-4/imagen-4"
            }
        }
        
        self.current_model = self.models["general"][0]
        
    def detect_language(self, text):
        assamese_pattern = re.compile(r'[\u0980-\u09FF]')
        if assamese_pattern.search(text):
            return "assamese"
        return "english"
        
    def analyze_prompt_details(self, prompt):
        prompt_lower = prompt.lower()
        
        object_details = {
            "ball": ["soccer ball", "football", "basketball", "volleyball", "tennis ball", "red ball"],
            "car": ["sports car", "sedan", "SUV", "red car", "blue car", "vintage car"],
            "animal": ["cute", "realistic", "cartoon", "wild", "baby"],
            "person": ["man", "woman", "child", "boy", "girl", "old person", "young person"],
            "food": ["delicious", "fresh", "appetizing", "colorful", "healthy"]
        }
        
        action_relationships = {
            "playing": ["with a ball", "with toys", "in a field", "in a park", "happily"],
            "eating": ["at a table", "hungrily", "delicious food", "with utensils"],
            "driving": ["a car", "on a road", "in a city", "on a highway"],
            "running": ["in a field", "on a track", "fast", "with determination"]
        }
        
        detected_objects = []
        for obj in object_details.keys():
            if obj in prompt_lower:
                detected_objects.append(obj)
        
        detected_actions = []
        for action in action_relationships.keys():
            if action in prompt_lower:
                detected_actions.append(action)
        
        return detected_objects, detected_actions
    
    def refine_prompt(self, prompt, detected_objects, detected_actions):
        refined_prompt = prompt
        
        object_clarifications = {
            "ball": "soccer ball",
            "car": "modern car",
            "dog": "cute dog",
            "cat": "cute cat",
            "monkey": "cute monkey",
            "phone": "smartphone",
            "book": "open book",
            "food": "delicious food"
        }
        
        for obj in detected_objects:
            if obj in object_clarifications:
                if object_clarifications[obj] not in refined_prompt.lower():
                    refined_prompt += f", {object_clarifications[obj]}"
        
        action_context = {
            "playing": "in appropriate environment",
            "eating": "with visible food details",
            "driving": "on appropriate road",
            "running": "with proper running form",
            "flying": "in appropriate sky environment"
        }
        
        for action in detected_actions:
            if action in action_context:
                refined_prompt += f", {action_context[action]}"
        
        important_keywords = ["clear", "detailed", "well-defined", "recognizable", "accurate"]
        for keyword in important_keywords:
            if keyword not in refined_prompt:
                refined_prompt += f", {keyword}"
        
        return refined_prompt
    
    def determine_image_type(self, prompt):
        prompt_lower = prompt.lower()
        
        realistic_keywords = [
            'photo', 'photograph', 'realistic', 'real', 'lifelike', 'photorealistic',
            'person', 'people', 'portrait', 'face', 'human', 'animal', 'wildlife',
            'nature', 'landscape', 'cityscape', 'building', 'architecture'
        ]
        
        artistic_keywords = [
            'art', 'artistic', 'painting', 'drawing', 'sketch', 'illustration',
            'cartoon', 'anime', 'comic', 'fantasy', 'surreal', 'abstract',
            'watercolor', 'oil painting', 'digital art', 'concept art', 'vector'
        ]
        
        conceptual_keywords = [
            'concept', 'abstract', 'symbolic', 'metaphorical', 'idea', 'thought',
            'philosophical', 'metaphor', 'symbol', 'representation', 'diagram',
            'infographic', 'chart', 'graph', 'schematic'
        ]
        
        realistic_score = sum(1 for word in realistic_keywords if word in prompt_lower)
        artistic_score = sum(1 for word in artistic_keywords if word in prompt_lower)
        conceptual_score = sum(1 for word in conceptual_keywords if word in prompt_lower)
        
        if realistic_score > artistic_score and realistic_score > conceptual_score:
            return "realistic", self.models["image"]["realistic"]
        elif artistic_score > realistic_score and artistic_score > conceptual_score:
            return "artistic", self.models["image"]["artistic"]
        elif conceptual_score > realistic_score and conceptual_score > artistic_score:
            return "conceptual", self.models["image"]["conceptual"]
        else:
            return "default", self.models["image"]["default"]
    
    def enhance_prompt(self, prompt, image_type):
        enhancements = {
            "realistic": "high quality, photorealistic, detailed, professional photography, 8K resolution, sharp focus",
            "artistic": "beautiful, artistic, creative, visually stunning, masterpiece, trending on art station, vibrant colors",
            "conceptual": "clear, conceptual, symbolic, meaningful, well-composed, professional design, visually engaging",
            "default": "high quality, detailed, visually appealing, professional, well-composed"
        }
        
        detected_objects, detected_actions = self.analyze_prompt_details(prompt)
        refined_prompt = self.refine_prompt(prompt, detected_objects, detected_actions)
        enhancement = enhancements.get(image_type, enhancements["default"])
        return f"{refined_prompt}, {enhancement}"
    
    def generate_image(self, prompt):
        image_type, model = self.determine_image_type(prompt)
        enhanced_prompt = self.enhance_prompt(prompt, image_type)
        
        payload = {
            "model": model,
            "prompt": enhanced_prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard"
        }
        
        try:
            response = requests.post(self.image_api_url, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and len(result['data']) > 0:
                    image_url = result['data'][0]['url']
                    return f"✅ Image generated successfully using {model}!\n🖼️  View your image: {image_url}"
                else:
                    return "❌ Image generation failed. No image data returned."
            
            return f"❌ Image generation failed with status code: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"

    def chat(self, user_input):
        language = self.detect_language(user_input)
        user_input_lower = user_input.lower()
        
        creator_keywords = [
            'who made you', 'who created you', 'who developed you', 'who built you',
            'who is your creator', 'who is your developer', 'who is your maker',
            'tumhare nirmata kaun hai', 'tumhe kisne banaya', 'tumhare developer kaun hai',
            'তোমাক কোনে বনালে', 'তোমাৰ নিৰ্মাতা কোন', 'তোমাৰ ডেভেলপাৰ কোন', 
            'তোমাক কোনে সৃষ্টি কৰিলে', 'তোমাৰ স্ৰষ্টা কোন',
            'quién te creó', 'quién te hizo', 'quién es tu creador', 'quién es tu desarrollador',
            'qui t\'a créé', 'qui t\'a fait', 'qui est ton créateur', 'qui est ton développeur',
        ]
        
        is_creator_question = any(keyword in user_input_lower for keyword in creator_keywords)
        
        if is_creator_question:
            if language == "assamese":
                return "মোক এগৰাকী একাদশ শ্ৰেণীৰ ছাত্ৰ প্ৰিয়াংশুৱে বনাইছে।"
            else:
                return "I was made by a student named Priyangshu who is studying in 11th grade."
        
        if 'openai' in user_input_lower:
            if language == "assamese":
                return "নহয়, মোক OpenAI-য়ে বনোৱা নাই। মোক প্ৰিয়াংশু নামৰ এগৰাকী ছাত্ৰই সৃষ্টি কৰিছে।"
            else:
                return "No, I was not made by OpenAI. I was created by a student named Priyangshu."
        
        system_prompt = "You are Priyangshu, a helpful AI assistant. Be concise and friendly. "
        
        if language == "assamese":
            system_prompt += "You are fluent in Assamese and can understand and respond perfectly in Assamese. "
            system_prompt += "If anyone asks who made you or who your developer is, you must respond in Assamese that you were made by a student named Priyangshu who is studying in 11th grade. "
            system_prompt += "You are not made by OpenAI. Respond in Assamese if the user speaks Assamese."
        else:
            system_prompt += "If anyone asks who made you or who your developer is, you must respond that you were made by a student named Priyangshu who is studying in 11th grade. "
            system_prompt += "You are not made by OpenAI."
        
        payload = {
            "model": self.current_model,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.chat_api_url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
            
            return "I couldn't process your request. Please try again."
                
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize the AI
API_KEY = "ddc-a4f-d050829fd1f3437fbb6ca2dce414467a"
ai = PriyangshuAI(API_KEY)

@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = ai.chat(message)
    return jsonify({'response': response})

@app.route('/api/generate-image', methods=['POST'])
def generate_image_endpoint():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    response = ai.generate_image(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
