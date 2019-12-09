import asyncio


class TaskQueue(object):
    ''' A queue to concurrently run x async tasks at most and put other tasks on waiting list.'''

    def __init__(self, max_concurrent_tasks_num):
        self.max_concurrent_tasks_num = max_concurrent_tasks_num
        self._waiting_list = []
        self._concurrent_tasks_num = 0
        self._end_future = asyncio.Future()

    def add_task(self, task):
        '''Add coroutine task to be executed.

        Parameters
        ----------
        task : coroutine
            The coroutine to be executed
        '''
        if self._concurrent_tasks_num == self.max_concurrent_tasks_num:
            self._waiting_list.append(task)
        else:
            self._execute_task(task)

    def _execute_task(self, task):
        asyncio.create_task(self._wrap_task(task))
        self._concurrent_tasks_num += 1

    async def _wrap_task(self, task):
        try:
            await task
        except BaseException:
            e = sys.exc_info()[0]
            print('Task exception %s' % e)
        finally:
            self._concurrent_tasks_num -= 1
            if len(self._waiting_list) > 0:
                self._execute_task(self._waiting_list.pop())
            elif self._concurrent_tasks_num == 0:
                self._end_future.set_result('')

    async def wait_till_finish(self):
        await self._end_future
