import math


class _CrawledRecord(object):
    ''' A crawled record to be saved '''

    def __init__(self, name='', url='', description='', score=0.0):
        self.name = name
        self.url = url
        self.score = score

    def __str__(self):
        return 'Crawled record: name = %s; url = %s; score = %f;' % (
            self.name, self.url, self.score)


class Store(object):
    ''' A class to save records to db.

    Attributes
    ----------
    _to_save : List
        A list of records to be saved.
    batch_size : int
        The number of records to be saved in batch.
    '''

    def __init__(self):
        self._to_save = []
        self.batch_size = 100

    def save(self, name='', url='', score=0.0):
        '''Save a record either to cache or trigger batch save if there are enough cached records.'''
        if not url:
            return
        if not name:
            name = url

        record = _CrawledRecord(
            name=name,
            url=url,
            score=score
        )
        self._to_save.append(record)
        if len(self._to_save) == self.batch_size:
            self.flush()

    def flush(self):
        ''' Save the batch to db '''
        print(*self._to_save, sep='\n')
        self._to_save = []


class HtmlStore(Store):
    ''' A class to save the records to a html file to make it easy to test and verify the result. '''

    def __init__(self):
        super().__init__()
        self.batch_size = math.inf

    def flush(self):
        ''' Save the result to a html file. This overrides parent's flush method. '''
        with open('crawed_result.html', 'w') as output_file:
            self._to_save.sort(key=lambda record: record.score, reverse=True)
            printed_records = ''
            for record in self._to_save:
                printed_records += '<tr><td><a href="%s" target="_blank">%s</a></td><td>%s</td></tr>' % (
                    record.url, record.name, record.score)
            output_file.write(
                '<html>' +
                '<head>' +
                '<style>' +
                'tr:nth-child(odd) {background: #dddddd}'
                '</style>' +
                '</head>' +
                '<body>' +
                '<table>' +
                '<thead>' +
                '<tr><th>doc</th><th>score</th></tr>' +
                '</thead>' +
                '<tbody>' +
                printed_records +
                '</tbody>' +
                '</table>' +
                '</body>' +
                '</html>')
