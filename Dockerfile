FROM python:3-alpine

WORKDIR /usr/src/app

COPY inventory-management/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY inventory-management ./

EXPOSE 5000
CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "5000" ]
