clean:
	black src/
	isort src/
	flake8 --ignore=E501,W503,E731 src/ 
