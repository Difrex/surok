def from_file(self, path):
    try:
        f = open(path, 'r')
        data = f.read()
        f.close()
        return data
    except OSError as err:
        self._logger.error('Module from_file. File {0} open or read error: {1}'.format(path, err))
        pass
    except:
        self._logger.error('Module from_file. File {0} open or read error. Unknown error.'.format(path))
        pass
