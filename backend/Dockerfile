# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port on which your app will run (usually 5000 for Flask)
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Command to run the Gunicorn server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]