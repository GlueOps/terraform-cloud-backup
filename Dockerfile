# Use an official Python runtime as the parent image
FROM python:3.11.9-alpine@sha256:e8effbb94ea2e5439c6b69c97c6455ff11fce94b7feaaed84bb0f2300d798cb7

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
