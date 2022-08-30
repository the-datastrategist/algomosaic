#!/bin/bash -e
# Build a new Docker image and saves it to Google Container Registry (GCR)

# GCP Project ID
# Must update this to your GCP Project ID
project=the-data-strategist

# Get the current project and use it in image directory
image_path=gcr.io/${project}
#image_path=gcr.io/${project}/images
image_name=algomosaic
image_tag=latest
full_image_name=${image_path}/${image_name}:${image_tag}

# clean up existing images
docker image prune

# Build and tag a new image
docker build -t "${full_image_name}" .
docker tag "${image_name}" "${full_image_name}"
docker push "$full_image_name"

# Output the strict image name (which contains the sha256 image digest)
docker inspect --format="{{index .RepoDigests 0}}" "${full_image_name}"
