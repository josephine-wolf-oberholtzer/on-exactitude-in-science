DATASET_YEAR ?= 2026
DATASET_MONTH ?= 11
DATASET_DAY ?= 01
DATASET_TIMESTAMP := ${DATASET_YEAR}${DATASET_MONTH}${DATASET_DAY}
LIMIT ?= 10000
WORKERS ?= 8

build:
	cd frontend && yarn install && yarn build

fetch-dataset:
	mkdir -p data/
	curl --fail https://data.discogs.com/?download=data%2F${DATASET_YEAR}%2Fdiscogs_${DATASET_TIMESTAMP}_artists.xml.gz > data/discogs_${DATASET_TIMESTAMP}_artists.xml.gz
	curl --fail https://data.discogs.com/?download=data%2F${DATASET_YEAR}%2Fdiscogs_${DATASET_TIMESTAMP}_labels.xml.gz > data/discogs_${DATASET_TIMESTAMP}_labels.xml.gz
	curl --fail https://data.discogs.com/?download=data%2F${DATASET_YEAR}%2Fdiscogs_${DATASET_TIMESTAMP}_masters.xml.gz > data/discogs_${DATASET_TIMESTAMP}_masters.xml.gz
	curl --fail https://data.discogs.com/?download=data%2F${DATASET_YEAR}%2Fdiscogs_${DATASET_TIMESTAMP}_releases.xml.gz > data/discogs_${DATASET_TIMESTAMP}_releases.xml.gz
