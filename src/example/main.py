import logging
import os

from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.metrics_settings import MetricsSettings
from conductor.client.worker.sample.simple_python_worker import SimplePythonWorker
from conductor.client.http.models.task_result_status import TaskResultStatus
from conductor.client.worker.worker_interface import WorkerInterface
from conductor.client.http.models.task import Task
from conductor.client.http.models.task_result import TaskResult
from pathlib import Path
from conductor.client.worker.task_worker import TaskWorker

logger = logging.getLogger(
    Configuration.get_logging_formatted_name(
        __name__
    )
)

class SimplePythonWorker(WorkerInterface):
    def execute(self, task: Task) -> TaskResult:
        task_result = self.get_task_result_from_task(task)
        task_result.add_output_data('key1', 'value')
        task_result.add_output_data('key2', 42)
        task_result.add_output_data('key3', False)
        task_result.status = TaskResultStatus.COMPLETED
        return task_result


def execute4(task):
    logging.info('Executing ' + str(task.task_id))
    return {'keyA': 'key1', 'keyB': 100, 'even': True}


def main():
    # Create a temp folder for metrics logs
    metrics_dir = str(Path.home()) + '/tmp/'
    if not os.path.isdir(metrics_dir):
        os.mkdir(metrics_dir)

    configuration = Configuration(
        base_url='http://localhost:8080',
        metrics_settings=MetricsSettings(
            directory=metrics_dir
        ),
        debug=False
    )

    # setup two workers task1 and task2
    # task1 worker is a functional code
    # task2 implements the worker interface and gives more control over the behavior of the task execution
    workers = [
        TaskWorker('task1', execute4),
        SimplePythonWorker('task2')
    ]

    # start the workers and wait
    with TaskHandler(workers, configuration) as task_handler:
        task_handler.start_processes()
        task_handler.join_processes()


if __name__ == '__main__':
    main()
