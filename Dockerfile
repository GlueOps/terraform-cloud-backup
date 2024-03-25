# Use an official Python runtime as the parent image
FROM python:3.11.8-alpine3.19@sha256:455fc75cfc2cae74520425036b62c6181079f7f6cc1dc0083aa5686dca2edb00

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "-u", "main.py"]
