# CSV-Parser
docker build -t csv-parser-image . 
docker run -p 5000:5000 csv-parser-image



docker tag firstimage YOUR_DOCKERHUB_NAME/firstimage
docker push YOUR_DOCKERHUB_NAME/firstimage

docker pull bionamicxu/csv-parser:latest