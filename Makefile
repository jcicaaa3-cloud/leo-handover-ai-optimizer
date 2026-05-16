PYTHONPATH := src

.PHONY: setup data train eval explain report visuals test api clean

setup:
	python -m pip install -r requirements.txt

data:
	PYTHONPATH=$(PYTHONPATH) python scripts/01_generate_dataset.py --output data/leo_candidates.csv

train:
	PYTHONPATH=$(PYTHONPATH) python scripts/02_train_model.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib

eval:
	PYTHONPATH=$(PYTHONPATH) python scripts/03_evaluate_policy.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --output artifacts/evaluation_metrics.json

explain:
	PYTHONPATH=$(PYTHONPATH) python scripts/05_explain_epoch.py --input data/leo_candidates.csv --model artifacts/handover_model.joblib --output artifacts/epoch_explanation.json

report:
	PYTHONPATH=$(PYTHONPATH) python scripts/06_make_report.py --metrics docs/evaluation_metrics_example.json --training artifacts/training_metrics.json --output docs/RUN_REPORT.md

visuals:
	PYTHONPATH=$(PYTHONPATH) python scripts/04_make_visuals.py --data data/leo_candidates.csv --model artifacts/handover_model.joblib --metrics docs/evaluation_metrics_example.json

test:
	PYTHONPATH=$(PYTHONPATH) python -m pytest -q

api:
	PYTHONPATH=$(PYTHONPATH) uvicorn leo_handover.api:app --reload

clean:
	rm -f data/*.csv artifacts/*.joblib artifacts/*.json
