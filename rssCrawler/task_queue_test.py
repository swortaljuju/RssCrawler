import unittest
import asyncio
import task_queue
import random

max_concurrent_tasks_num = 5


class TaskQueueTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.executed_tasks_count = 0
        self.task_queue = task_queue.TaskQueue(max_concurrent_tasks_num)

    async def execute_async_task(self, time_ms):
        await asyncio.sleep(time_ms / 1000)
        self.executed_tasks_count += 1

    async def test_same_gap(self):
        num_tasks = max_concurrent_tasks_num * 10
        for x in range(num_tasks):
            self.task_queue.add_task(self.execute_async_task(100))

        await self.task_queue.wait_till_finish()
        self.assertEqual(self.executed_tasks_count, num_tasks)

    async def test_two_gaps(self):
        num_tasks = max_concurrent_tasks_num * 10
        for x in range(int(num_tasks / 2)):
            self.task_queue.add_task(self.execute_async_task(100))
            self.task_queue.add_task(self.execute_async_task(50))

        await self.task_queue.wait_till_finish()
        self.assertEqual(self.executed_tasks_count, num_tasks)

    async def test_small_task_amount(self):
        '''Test task number less than max concurrent tasks'''
        num_tasks = int(max_concurrent_tasks_num / 2)
        for x in range(num_tasks):
            self.task_queue.add_task(self.execute_async_task(100))

        await self.task_queue.wait_till_finish()
        self.assertEqual(self.executed_tasks_count, num_tasks)

    async def test_random_add_task(self):
        '''Test when task is added asynchronously and randomly'''
        num_tasks = max_concurrent_tasks_num * 10
        for x in range(num_tasks):
            self.task_queue.add_task(
                self.execute_async_task(
                    random.uniform(
                        0, 500)))
            await asyncio.sleep(random.uniform(0, 0.1))

        await self.task_queue.wait_till_finish()
        self.assertEqual(self.executed_tasks_count, num_tasks)


if __name__ == "__main__":
    unittest.main()
