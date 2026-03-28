FROM python:3.9-slim

# FFmpeg install karna music conversion ke liye
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app
COPY . .

# Libraries install karna
RUN pip install --no-cache-dir -r requirements.txt

# Bot chalana
CMD ["python", "bot.py"]
