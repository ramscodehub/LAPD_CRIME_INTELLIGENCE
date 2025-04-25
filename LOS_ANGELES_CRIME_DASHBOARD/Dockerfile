# Use official Python image
FROM python:3.10-slim

# Set environment variables to avoid Python buffering issues and enable UTF-8 encoding
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# Set working directory
WORKDIR /app

# Copy all files into container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Download necessary NLTK data
RUN python -m nltk.downloader punkt

# Expose the port that Dash runs on (default: 8050)
EXPOSE 8050

# Command to run the Dash app
CMD ["python3", "crime_dash_board.py"]
