install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

lint:
	pylint --disable=C main.py process/

format:
	black main.py process/

test:
	python -m pytest -vv --cov=main test_main.py

run:
	python main.py

requirements:
	pip freeze > requirements.txt

demo:
	python main.py --start_date '20210101' --end_date '20220207' --rfm_date '2022-01-31' --statistics_date '2022-01-31'