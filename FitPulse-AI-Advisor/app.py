import os
import gradio as gr
from groq import Groq

# 1. Setup Groq
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)


style = """
.gradio-container { 
    font-family: 'Inter', sans-serif; 
    background-color: #121212; /* رمادي داكن جداً للخلفية */
}

#title-text { 
    text-align: center; 
    color: #ffffff; 
    padding: 20px; 
    font-weight: bold;
}

.message { 
    border-radius: 12px !important; 
    border: 1px solid #333 !important;
}


#chatbot {
    background-color: #1e1e1e !important;
    border-radius: 15px;
}


.subtitle {
    color: #666666;
    text-align: center;
    margin-bottom: 20px;
}

body { 
    background: linear-gradient(135deg, #121212 0%, #2c3e50 100%); 
}
"""

def fitness_chat(message, history):
    # System prompt for professional fitness guidance
    messages = [
        {"role": "system", "content": """You are a professional Fitness & Nutrition Coach AI. Provide:
1. General fitness advice and workout tips
2. Basic nutrition guidance for fitness goals
3. Form and technique recommendations
4. Motivation and accountability strategies

IMPORTANT DISCLAIMERS:
- Always remind users to consult with healthcare professionals before starting new exercise programs
- Specify that you're not a substitute for certified personal trainers or dietitians
- Encourage proper warm-up and cool-down routines
- Emphasize listening to one's body and avoiding overtraining
"""}

    ]
    
    # Filter metadata to prevent the error seen in your previous logs
    for entry in history:
        messages.append({"role": entry["role"], "content": entry["content"]})
    
    messages.append({"role": "user", "content": message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
                yield response
    except Exception as e:
        yield f"AI Service Alert: {str(e)}"

# 2. Modern GUI Layout (Optimized for Gradio 6.0)
with gr.Blocks() as demo:
    gr.Markdown("# 💪 **Fitness AI Coach Pro**", elem_id="title-text")
    gr.Markdown("### Your AI-powered fitness and nutrition assistant")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Fitness Consultation",
                height=500,
                show_label=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask about workouts, nutrition, or fitness goals...",
                    show_label=False,
                    scale=7
                )
                submit = gr.Button("Send", variant="primary", scale=1)

            with gr.Row():
                clear = gr.Button("🔄 Reset Chat", size="sm")
                gr.HTML("<div style='text-align: right; color: #666; font-size: 0.8em; padding: 5px;'>Always consult professionals for personalized advice</div>")

        with gr.Column(scale=1):
            gr.Markdown("### 🏋️‍♂️ Quick Examples")
            gr.Examples(
                examples=[
                    "Beginner full-body workout routine",
                    "How to improve running endurance?",
                    "High-protein meal ideas for muscle building",
                    "Proper squat form tips",
                    "How to stay motivated to exercise?",
                    "Pre and post-workout nutrition"
                ],
                inputs=msg,
                label="Common Questions"
            )
            
            gr.Markdown("### 📊 Quick Tips")
            gr.HTML("""
            <div style='
                background: #1e1e1e; 
                padding: 15px; 
                border-radius: 10px; 
                border-left: 4px solid #e53935; 
                color: #e0e0e0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            '>
                <b style='color: #ffffff; font-size: 1.1em;'>💡 Remember:</b>
                <ul style='margin-top: 10px; line-height: 1.6; color: #b0b0b0;'>
                    <li><span style='color: #e53935;'>•</span> Start slow and progress gradually</li>
                    <li><span style='color: #e53935;'>•</span> Consistency beats intensity</li>
                    <li><span style='color: #e53935;'>•</span> Hydration is key</li>
                    <li><span style='color: #e53935;'>•</span> Rest is part of training</li>
                    <li><span style='color: #e53935;'>•</span> Form over weight</li>
                </ul>
            </div>
            """)

    def respond(message, chat_history):
        # Adding user message
        chat_history.append({"role": "user", "content": message})
        # Placeholder for AI
        chat_history.append({"role": "assistant", "content": ""})
        
        # Stream response
        bot_generator = fitness_chat(message, chat_history[:-2])
        
        for updated_text in bot_generator:
            chat_history[-1]["content"] = updated_text
            yield "", chat_history

    # Event handlers
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    demo.launch(css=style, share=False)