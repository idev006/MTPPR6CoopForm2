FROM python:3.12-slim

WORKDIR /app

# ติดตั้ง system deps ที่ pikepdf ต้องการ
RUN apt-get update && apt-get install -y --no-install-recommends \
    libqpdf-dev \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง Python deps ก่อน copy code (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source code
COPY . .

# สร้าง directories ที่ต้องการ
RUN mkdir -p /app/data/pdf_templates /app/data/pdf_generated /app/data/attachments /app/data/logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
