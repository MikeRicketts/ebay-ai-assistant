import torch
import os
from prompt_builder import build_prompt
from output_parser import parse_output


class ModelClient:
    def __init__(self, model_name="meta-llama/Llama-3.1-8B-Instruct"):
        # Set Hugging Face token in environment
        os.environ["HUGGING_FACE_HUB_TOKEN"] = "hf_YourTokenHere"

        # Import here to avoid circular imports
        from transformers import AutoTokenizer, AutoModelForCausalLM

        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("Model loaded successfully")

    def generate_listing(self, details, sold_listings, max_tokens=512, temperature=0.7):
        prompt = build_prompt(details, sold_listings)

        # Llama-3.1 specific chat template
        messages = [
            {
                "role": "system",
                "content": "You are an expert eBay listing agent. Format your response exactly with <START> and <END> tags."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Prepare input for model
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt"
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        # Generate with parameters optimized for structured outputs
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.15,
                eos_token_id=self.tokenizer.eos_token_id
            )

        # Decode and parse output
        output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return parse_output(output_text.strip())