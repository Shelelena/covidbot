#!/bin/bash

IMAGE_NAME="covidbot_covidbot"
IMAGE_FILE=$IMAGE_NAME"_`date +%F`.tar"
PROD_DOCKER_COMPOSE="docker-compose.production.yml"

LOCAL_DIR="./docker_images"
LOCAL_IMAGE_FILE=$LOCAL_DIR/$IMAGE_FILE

REMOTE_DIR="/root/shelena/covidbot"
REMOTE_IMAGE_FILE=$REMOTE_DIR/$IMAGE_FILE
REMOTE_LOGFILE=$REMOTE_DIR/logfile.log

USERNAME="shelena"
SSH_KEY_FILE="/home/$USERNAME/.ssh/id_ed25519"
SERVER="myserver"

ssh-add $SSH_KEY_FILE
sudo docker-compose build

mkdir -p $LOCAL_DIR
sudo docker save -o $LOCAL_IMAGE_FILE $IMAGE_NAME
sudo chown $USERNAME:$USERNAME $LOCAL_IMAGE_FILE
gzip -f $LOCAL_IMAGE_FILE

ssh $SERVER "mkdir -p $REMOTE_DIR"
scp $LOCAL_IMAGE_FILE.gz $SERVER:$REMOTE_DIR
scp $PROD_DOCKER_COMPOSE $SERVER:$REMOTE_DIR
ssh $SERVER "touch $REMOTE_LOGFILE"

ssh $SERVER "gunzip $REMOTE_IMAGE_FILE.gz"
ssh $SERVER "docker load -i $REMOTE_IMAGE_FILE"
ssh $SERVER "rm -f $REMOTE_IMAGE_FILE"

ssh $SERVER "docker-compose \
    -f $REMOTE_DIR/$PROD_DOCKER_COMPOSE \
    --project-directory $REMOTE_DIR \
    up -d"
