
import xml.etree.cElementTree as ET


class Xml(object):

    def __init__(self):
        pass

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

    def xml_form(self, files, ids):
        root = ET.Element('root')

        if len(files) > 0:
            for file, i in zip(files, ids):
                ET.SubElement(root, 'result', name=file, id=str(i))
        return ET.tostring(root)
