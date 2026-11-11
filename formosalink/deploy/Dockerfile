FROM python:3.12-slim
WORKDIR /app
COPY formosalink/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home formosa
COPY formosalink /app/formosalink
COPY openpilot/sunnypilot/formosalink /app/openpilot/sunnypilot/formosalink
RUN mkdir /state && chown formosa:formosa /state
USER formosa
ENV FORMOSALINK_DATA_DIR=/state
EXPOSE 8765
CMD ["python", "-m", "formosalink.server", "--port", "8765"]
