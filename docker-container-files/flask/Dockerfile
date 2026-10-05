# Flask task-manager application image.
#
# Base: python:3.14-slim — the slim variant excludes toolchain and doc
# layers, keeping the image small and the attack surface minimal.
FROM python:3.14-slim

WORKDIR /app

# Dependency layer first: requirements.txt changes rarely, so pip install
# stays cached across code edits. Copying app source before this line
# would invalidate the cache on every app.py change and reinstall deps.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code changes often — keep it in the final layers.
COPY app.py .
COPY templates ./templates/

# Documentation for humans and orchestration tooling: the app listens on
# 5000 inside the container. EXPOSE publishes nothing by itself —
# docker-compose.yml controls which host interfaces get bindings.
EXPOSE 5000

# Flask's built-in development server. Fine for a portfolio/demo; a
# production deployment would run gunicorn behind the nginx proxy.
CMD ["python3", "app.py"]
