
import xml.etree.cElementTree as ET

## Xml functions.
class Xml(object):

    ## Constructor.
    def __init__(self):
        pass

    ## Xml maker to html.
    # @param string of xml form
    # @param string of node ip:port
    # go through the xml string 
    # make a html table form
    def xml_to_html(self, st, node):
        st = str(st)
        root = ET.fromstring(st)
        html = ''
        for result in root.findall('result'):
            name = result.get('name')
            id = result.get('id')
            html += ''' <tr>
                        <td align="middle";
                        style="background-color:white">%s</td>
                        <td align="middle"; style="background-color:white">
                        <a href="/download_file?id=%s&node=%s">
                        &lt;download&gt;</a>
                        <a href="/view_file?id=%s&node=%s">&lt;view&gt;</a>
                        </td>
                        </tr>''' % (name, id, node, id, node)
        return html

    ## Xml form creator.
    # @param list of file names
    # @param list of ids
    # make an xml form with file names 
    # and their ids
    def xml_form(self, files, ids):
        root = ET.Element('root')

        if len(files) > 0:
            for file, i in zip(files, ids):
                ET.SubElement(root, 'result', name=file, id=str(i))
        return ET.tostring(root)
