from jinja2 import Environment, PackageLoader, Template


# Return rendered configuration 
def gen(my, jj2):
    f = open(jj2)
    temp = f.read()
    f.close()

    template = Template(temp)

    print( template.render(my=my) )
