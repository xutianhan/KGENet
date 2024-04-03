import time
import pandas as pd
import json
from collections import OrderedDict


class RunManager:
    def __init__(self):
        self.epoch_count = 0
        self.epoch_loss = 0
        self.epoch_start_time = None

        self.run_params = None
        self.run_count = 0
        self.run_data = []
        self.run_start_time = None

        self.model = None
        self.loader = None


    def begin_run(self, hyper_params, model, loader):
        self.run_start_time = time.time()
        self.run_params = hyper_params
        self.run_count += 1
        self.model = model
        self.loader = loader


    def end_run(self):
        self.epoch_count = 0

    def begin_epoch(self, epoch_no):
        self.epoch_start_time = time.time()
        self.epoch_count += 1
        self.epoch_loss = 0
        # self.epoch_num_correct = 0
        print(f"Epoch {epoch_no} started ...", end=" ")

    def end_epoch(self):
        epoch_duration = time.time() - self.epoch_start_time
        run_duration = time.time() - self.run_start_time
        loss = self.epoch_loss / len(self.loader.dataset)
        results = OrderedDict()
        results["run"] = self.run_count
        results["epoch"] = self.epoch_count
        results["loss"] = loss
        # results["accuracy"] = accuracy
        results["epoch_duration"] = epoch_duration
        results["run duration"] = run_duration

        for k, v in self.run_params._asdict().items():
            results[k] = v

        self.run_data.append(results)

        print("Ended")

    def track_loss(self, loss):
        self.epoch_loss += loss.item() * self.loader.batch_size


    def save(self, fileName):
        pd.DataFrame.from_dict(self.run_data, orient='columns', ).to_csv(f'{fileName}.csv')
        with open(f'{fileName}.json', 'w', encoding='utf-8') as f:
            json.dump(self.run_data, f, ensure_ascii=False, indent=4)
