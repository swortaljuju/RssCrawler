BATCH_SIZE = 100

class _CrawledRecord(object):
    ''' A crawled record to be saved '''

    def __init__(self, name='', url='', description='', score=0.0):
        self.name = name
        self.url = url
        self.description = description
        self.score = score

    def __str__(self):
        return 'Crawled record: name = %s; url = %s; description = %s; score = %f;' % (
            self.name, self.url, self.description, self.score)


class Store(object):
    ''' A class to save records to db.'''

    def __init__(self):
        self._to_save = []

    def save(self, name='', url='', description='', score=0.0):
        record = _CrawledRecord(
            name=name,
            url=url,
            description=description,
            score=score
        )
        self._to_save.append(record)
        if len(self._to_save) == BATCH_SIZE:
            self.flush()

    def flush(self):
        ''' Save the batch to db '''
        print(*self._to_save, sep='\n')
        self._to_save = []
