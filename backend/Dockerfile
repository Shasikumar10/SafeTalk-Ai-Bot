# Use a newer Debian version (Bookworm) to avoid the 404 error
FROM python:3.11-slim-bookworm

# Setup User with UID 1000 (Hugging Face Requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libasound2-dev \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements and install
COPY --chown=user requirements.txt $HOME/app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all application files
COPY --chown=user . $HOME/app

# Expose the default Hugging Face port
EXPOSE 7860

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
