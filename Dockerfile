FROM python:3.7
COPY . algomosaic/
ENV PYTHONPATH "${PYTHONPATH}:/algomosaic"
RUN python3 -m pip install -r algomosaic/requirements.txt
