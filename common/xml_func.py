# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET


def xml_to_html(st,node):
    st=str(st)
    root=ET.fromstring(st)
    html=''
    for result in root.findall('result'):
        name = result.get('name')
        id=result.get('id')
        html+='  <tr> <td>%s</td> <td align="middle"> <a href="/download_file?id=%s&node=%s">&lt;download&gt;</a> <a href="/view_file?id=%s&node=%s">&lt;view&gt;</a></td>  </tr>' %(name, id, node, id, node)
    return html
    
def xml_form(files, ids):
    root = ET.Element('root')
    
    if len(files)>0:
        for file,i in zip(files,ids):
            ET.SubElement(root, 'result', name=file, id=str(i))
       
    return ET.tostring(root)

# vim: expandtab tabstop=4 shiftwidth=4 