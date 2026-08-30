FROM python:3.12-slim

WORKDIR /service
COPY produtos.json catalog_service.py ./
EXPOSE 8080
CMD ["python", "catalog_service.py"]
