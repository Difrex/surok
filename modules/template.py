import jinja2


def template(self, temp):
    try:
        template = jinja2.Template(temp)
        return template.render(my=self._my, mod=self)
    except jinja2.UndefinedError as err:
        self._logger.error('Module template. Render Jinja2 error. ', err)
    except:
        self._logger.error('Module template. Render Jinja2 error. Unknown error')
