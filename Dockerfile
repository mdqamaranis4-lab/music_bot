FROM python:3.9-slim

# FFmpeg install karna music convert karne ke liye
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app
COPY . .

# Sabhi libraries install karna
RUN pip install --no-cache-dir -r requirements.txt

# Bot start karna
CMD ["python", "bot.py"]
