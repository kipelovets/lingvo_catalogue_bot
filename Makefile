run:
		docker-compose run --rm app
test:
		docker-compose run --rm test pytest
build:
		docker-compose build