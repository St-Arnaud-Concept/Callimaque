import os
import google.generativeai as genai

class AIManager:
    def __init__(self):
        self.models = {
            "Gemini 1.5 Flash": self._correct_with_gemini,
            "Claude 3.5 Sonnet": self._correct_with_claude,
            "Chat GPT-4o": self._correct_with_gpt,
            "Grok 1.5": self._correct_with_grok
        }
        self.current_model_name = "Gemini 1.5 Flash"
        self.api_keys = {}

    def get_available_models(self):
        return list(self.models.keys())

    def set_model(self, model_name):
        if model_name in self.models:
            self.current_model_name = model_name
        else:
            raise ValueError(f"Model {model_name} not found.")

    def set_api_key(self, model_name, api_key):
        self.api_keys[model_name] = api_key

    def correct_text(self, text):
        if not text:
            return "No text to correct."
            
        correction_function = self.models.get(self.current_model_name)
        if correction_function:
            return correction_function(text)
        else:
            return "Error: Model function not found."

    def _correct_with_gemini(self, text):
        api_key = self.api_keys.get("Gemini 1.5 Flash")
        if not api_key:
            return "Error: API Key for Gemini is missing. Please set it in options."

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Please correct the OCR errors in the following text. 
            Fix spelling mistakes, grammar issues, and broken words resulting from the OCR process.
            Maintain the original formatting (newlines, indentation) as much as possible.
            Do not add any introductory or concluding remarks, just provide the corrected text.
            
            Text to correct:
            {text}
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

    def _correct_with_claude(self, text):
        return "Claude 3.5 Sonnet integration is coming soon. (Fake Infrastructure)"

    def _correct_with_gpt(self, text):
        return "Chat GPT-4o integration is coming soon. (Fake Infrastructure)"

    def _correct_with_grok(self, text):
        return "Grok 1.5 integration is coming soon. (Fake Infrastructure)"
