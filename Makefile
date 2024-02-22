gen_req:
	poetry export --without-hashes --format=requirements.txt > requirements.txt
build:
	docker-compose -f docker/docker-compose.yml build --no-cache
up:
	docker-compose -f docker/docker-compose.yml up
go:
	docker-compose -f docker/docker-compose.yml up --build -d