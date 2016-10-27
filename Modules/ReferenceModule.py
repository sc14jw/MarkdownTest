import sys
from datetime import datetime

sys.path.append(".")

from Modules.Module import Module
from Modules.LinksModule import LinksModule

''' Module to handle references with ref command '''
class ReferenceModule(Module):

    ''' Handles formatting of reference attributes '''
    class AttributeFormatter():
        def __init__(self):
            self.linksmodule = LinksModule()

        def formatDate(self, datestr):
            try:
                return datetime.strptime(datestr,'%d/%m/%Y').strftime('%d %b %Y')
            except ValueError:
                raise ValueError("'" + yearstr + "' did not match the format 'dd/mm/yyyy'")

        def isYear(self, yearstr):
            try:
                return datetime.strptime(yearstr,'%Y').strftime('%Y')
            except ValueError:
                raise ValueError("'" + yearstr + "' did not match the format 'yyyy'")

        def generateRefLink(self, link):
            return self.linksmodule.completeCommand("link(" + link + ")")

        def toUpper(self, string):
            return '' if len(string) == 0 else string[0].upper() if len(string) == 1 else string[0].upper() + string[1:]

        def isInt(self, num):
            try:
                return str(int(num))
            except ValueError:
                raise ValueError("'" + num + "' is not convertable to int.")

        def toUpperLetter(self, char):
            if len(char) == 1:
                return char.upper()
            else:
                raise ValueError("'" + char + "' initial is not of length 1")

    def __init__(self):
        self.attrFormat = self.AttributeFormatter()
        self.REF_PREFIX = 'ref'
        self.ATTR_TYPES = ['name', 'first name', 'last name', 'first initial', 'published', 'title', 'journal', 'volume',
                      'pages', 'url', 'accessed']
        self.REF_TYPES = {'website': {'attrs': {'last name': {'post': ', ', 'function': self.attrFormat.toUpper, 'pos': 1},
                                                'first initial': {'post': '. ', 'function': self.attrFormat.toUpperLetter, 'pos': 2},
                                                'published': {'pre': '(', 'post': '). ', 'function': self.attrFormat.isYear, 'pos': 3},
                                                'title': {'post': '. ', 'function': self.attrFormat.toUpper, 'pos': 4},
                                                'journal': {'post': ', ', 'function': self.attrFormat.toUpper, 'pos': 5},
                                                'volume': {'pre': '[online] Volume ', 'post': ', ', 'pos': 6},
                                                'pages': {'pre': 'p. ', 'post': '. ', 'function': self.attrFormat.isInt, 'pos': 7},
                                                'url': {'pre': 'Available at: ', 'post': ' ', 'function': self.attrFormat.generateRefLink, 'pos': 8},
                                                'accessed': {'pre': '[Accessed ', 'post': '].', 'function': self.attrFormat.formatDate, 'pos': 9}}
                                     }
                         }

        assert set(self.ATTR_TYPES).issuperset(set([attr for ref_type in self.REF_TYPES
                                               for attr in self.REF_TYPES[ref_type]['attrs'].keys()]))

    def parseReference(self, attr_dict, ref_type):
        attr_ordered = self.REF_TYPES[ref_type]['attrs'].keys()
        attr_ordered.sort(key=lambda attr: self.REF_TYPES[ref_type]['attrs'][attr]['pos'])

        attr_dict = {attr:self.REF_TYPES[ref_type]['attrs'][attr]['function'](attr_dict[attr])
                    if 'function' in self.REF_TYPES[ref_type]['attrs'][attr] else attr_dict[attr]
                    for attr in attr_dict}

        reference = [self.REF_TYPES[ref_type]['attrs'][attr].get('pre', '') +
                     attr_dict.get(attr, "<No '" + attr + "'>") +
                     self.REF_TYPES[ref_type]['attrs'][attr].get('post', '')
                     for attr in attr_ordered]
        return '<p>' + ''.join(reference) + "</p>"

    def getCommands(self):
        return {"link" : "add a link into the document - can be optionally paramatised with [] to alter link text"}

    def validateCommand(self, command):
        if not command[len(self.REF_PREFIX)] == ':':
            raise SyntaxError("ref commands must be followed by a colon")
        elif ' ' not in command:
            raise SyntaxError("ref:<type> must contain a space after the type")
        elif '{' not in command:
            raise SyntaxError("Missing '{' after ref:<type>")
        elif '}' not in command:
            raise SyntaxError("Missing '}' after attributes")

    def removeWhitespacePadding(self, string):
        if not (isinstance(string, str)):
            raise AttributeError("Text is not a string")
        return string.lstrip()[::-1].lstrip()[::-1]

    def completeCommand(self, command):

        if not (isinstance(command, str)):
            raise AttributeError("Text is not a string")

        html = command

        if command.startswith(self.REF_PREFIX):

            self.validateCommand(command)

            ref_type = command[command.index(':') + 1:command.index(' ')]

            if ref_type in self.REF_TYPES:
                # Get attributes, removing whitespace from the start and end of the statement
                attrs = self.removeWhitespacePadding(command[command.index(' ') + 1:])

                if not attrs.startswith('{'):
                    raise SyntaxError("Expected a '{' after ref:<type>")
                elif not attrs.endswith('}'):
                    raise SyntaxError("Expected a '}' at the end of the line")

                attrs_contents = attrs[1:len(attrs) - 1].split(',')

                attr_dict = {}
                for attr in attrs_contents:
                    if ':' not in attr:
                        raise SyntaxError("Attribute name and value pair '%s' missing colon seperator" % attr)
                    if not attr.count(':') == 1:
                        raise SyntaxError("Attribute name and value pair '%s' has more than one colon seperator" % attr)

                    attr_name, attr_val = attr.split(':')
                    attr_name = self.removeWhitespacePadding(attr_name)
                    attr_val = self.removeWhitespacePadding(attr_val)

                    if attr_name in attr_dict:
                        raise NameError("Duplicate attribute name '%s'" % attr_name)

                    attr_dict[attr_name] = attr_val

                html = self.parseReference(attr_dict, ref_type)
            else:
                raise NameError("Reference type '%s' does not exist. Reference types must be declared in the format ref:<type>" % ref_type)


        return html



if __name__ == '__main__':
    module = ReferenceModule()
    #output = module.completeCommand("ref:website {last name:Hodgson, first initial:K, published:23/07/15, \
    #                                               title:testtitle, journal:bookofsomething, volume:3, pages:24, url:www.test.com, \
    #                                               accessed:24/07/15}")
    output = module.completeCommand("ref:website {last name:esc, first initial:k, published:2015, \
                                                  title:testtitle, journal:bookofsomething, volume:3, pages:24, \
                                                  url:www.test.com, accessed:23/07/2008}")


    print("output = " + str(output))
