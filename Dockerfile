# Use a slim Python base image for a smaller footprint
FROM python:3.9-slim

# Set up a non-root user for security
RUN useradd -m -u 1000 user
USER user

# Add the user's local bin to the PATH
ENV PATH="/home/user/.local/bin:${PATH}"

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY --chown=user ./requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application files into the working directory
COPY --chown=user . .

# Expose the port that Hugging Face Spaces expects (7860)
EXPOSE 7860

# The command to run the Streamlit application
# --server.port=7860: Sets the port for Hugging Face Spaces
# --server.headless=true: Recommended for running in a container
# --server.address=0.0.0.0: Makes the server accessible externally
CMD ["streamlit", "run", "quiz_generator.py", "--server.port=7860", "--server.headless=true", "--server.address=0.0.0.0"]