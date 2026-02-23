
init:
	git init
	git add .
	git commit -m "Initial commit"
	cp .docker.env .env
	docker compose build
	docker compose up -d db
	docker compose up -d redis
	sleep 2
	docker compose run --rm web python manage.py generate_tailwind_directories
	docker compose run --rm web npm i && npm run tailwind:build
	docker compose run --rm web python manage.py migrate
	docker compose run --rm web python manage.py makesuperuser
	
	docker compose up -d
	@echo "Run 'make dev' to start the server"
	@echo "Run 'make tw' to start tailwind watch"
	@echo "Run 'make mm' to make migrations"
	@echo "Run 'make m' to migrate"
	@echo "Open your browser at http://127.0.0.1:9000"

run:
	bash -c "docker compose run --rm web $(run)"


bash: run=bash
bash: run

manage: run=python -Wa manage.py $(command)
manage: run

dev: command=runserver
dev: manage

mm: command=makemigrations
mm: manage

m: command=migrate
m: manage

tailwind-directories: command=generate_tailwind_directories
tailwind-directories: manage

tw: run=npm run tailwind:watch
tw: run

tailwind-watch: tailwind-directories
	$(MAKE) tw

twb: run=npm run tailwind:build
twb: run

tailwind-build: tailwind-directories
	$(MAKE) twb
	

