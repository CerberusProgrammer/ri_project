run:
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py runserver

public:
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py runserver 0.0.0.0:8000

dockerize:
	docker build -t ri_server0.1.0 .
	docker run -p 8000:8000 ri_server0.1.0

install:
	pip3 install -r requirements.txt