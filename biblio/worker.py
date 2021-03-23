import multiprocessing


class Worker:
    def __init__(self, queue):
        self.queue = queue

    def run(self):
        while True:
            uid = self.queue.get()
            grosseFonction = lambda uid: print(uid)
            # p = multiprocessing.Process(target=grosseFonction, args=(uid,))
            grosseFonction(uid)
            self.queue.task_done()


class Queue:
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.workers = [Worker(self.queue)] * 5

        self.pool = multiprocessing.Pool(10)
        for w in self.workers:
            self.pool.apply_async(w.run)



q = Queue()
q.queue.put(2)
while True:
    pass


