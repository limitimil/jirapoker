cp ../env.sh .
cp ../docker-compose.yml .
docker-compose down
sudo chown -R dockeruser:dockeruser mongodbdata/
docker-compose up -d --build
sleep 5
docker ps
