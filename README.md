### CHAT MATH

(1) Activate virtual environment
conda activate chat-math

(2) To install dependencies, run the following command:
pip install -r requirements.txt

(3) Pull LLM 
ollama pull qwen2.5

(4) Run Local LLM
ollama serve

(5) Run this code with the command
streamlit run app.py

(6) If needed, export libraries to requirements.txt
pip list --format=freeze > requirements.txt

(7) Access the app at https://localhost
sudo stunnel stunnel.conf
[passphrase: gary]
