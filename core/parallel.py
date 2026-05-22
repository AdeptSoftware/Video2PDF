# parallel.py
# Выполнение кода в несколько процессов (распараллеливание вычислений)
from multiprocessing import Process, Queue
from tqdm            import tqdm
import time
import os

""" Пример использования:
if __name__ == "__main__":
    run(texture_reader, texture_iterator)
    # texture_iterator() -> file
    # texture_reader(file) -> result
"""

def _worker(callback, task_queue, result_queue, *args):
    t = task_queue.get()
    while t is not None:
        result_queue.put(callback(t, *args))
        t = task_queue.get()


def run(callback, iterator, *args, num_workers=os.cpu_count(), queue_size=1000, total=None,
        desc1="Queueing", desc2="Collecting"):
    tasks       = Queue(maxsize=queue_size)
    results     = Queue()
    processes   = []

    for _ in range(num_workers):
        p = Process(target=_worker, args=(callback, tasks, results, *args))
        processes += [ p ]
        p.start()

    for task in tqdm(iterator(), total=total, desc=desc1):
        tasks.put(task)

    time.sleep(0.5)
    for _ in range(num_workers):
        tasks.put(None)

    ret = []
    time.sleep(0.5)
    for _ in tqdm(range(results.qsize()), desc=desc2):
        ret.append(results.get())

    time.sleep(0.5)
    for p in processes:
        p.join()

    return ret