# Tahap 1: builder (butuh compiler)
FROM python:3.11-alpine as builder

RUN apk add --no-cache build-base libpq

# Set workdir dan salin file requirements
WORKDIR /app
COPY requirements.txt .

# Buat virtualenv untuk isolasi
RUN python -m venv /venv && \
    . /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Tahap 2: production image
FROM python:3.11-alpine

# Install dependensi minimal runtime (tanpa compiler)
RUN apk add --no-cache libpq

# Salin virtualenv dari builder
COPY --from=builder /venv /venv

# Aktifkan virtualenv
ENV PATH="/venv/bin:$PATH"

# Set working dir & salin project
WORKDIR /app
COPY . .

# Port expose
EXPOSE 8010

# Jalankan
CMD ["gunicorn", "gps_collar_project.wsgi:application", "--bind", "0.0.0.0:8010"]
