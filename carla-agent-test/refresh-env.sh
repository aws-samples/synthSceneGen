#docker kill carla-1
cd /home/ubuntu/environment/carla-output/images

sudo rm -R *

cd /home/ubuntu/environment/carla-agent-test

docker container rm carla-1

docker build -t carla-agent-env .

#sudo docker run -it --expose 9090 -p 0.0.0.0:9090:22 --mount type=bind,source='/home/ubuntu/environment/carla-output/images',target='/app/carla-output/images/' --name carla-1 carla-agent-env:latest

echo "All done"