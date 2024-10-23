# Use an official Python runtime as the parent image
FROM python:3.12.7-alpine@sha256:38e179a0f0436c97ecc76bcd378d7293ab3ee79e4b8c440fdc7113670cb6e204

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
