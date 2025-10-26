"""  # moved into package reqif_app
ReqIF File Generator

This script generates a ReqIF (Requirements Interchange Format) file
similar to the testImport.reqif structure.
"""

from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from xml.dom import minidom
import uuid


class ReqIFGenerator:
    """Generator for ReqIF files following the OMG ReqIF 1.0 specification"""

    NAMESPACES = {
        'default': 'http://www.omg.org/spec/ReqIF/20110401/reqif.xsd',
        'xhtml': 'http://www.w3.org/1999/xhtml'
    }

    def __init__(self, title="System Requirements Specification"):
        self.title = title
        self.timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Data type references
        self.dt_string = "DT-STRING"
        self.dt_xhtml = "DT-XHTML"
        self.dt_integer = "DT-INTEGER"
        self.dt_status = "DT-STATUS"
        self.dt_priority = "DT-PRIORITY"

        # Enum value references
        self.status_values = {
            'draft': 'EV-STATUS-DRAFT',
            'wip': 'EV-STATUS-WIP',
            'reviewed': 'EV-STATUS-REVIEWED',
            'approved': 'EV-STATUS-APPROVED'
        }

        self.priority_values = {
            'high': 'EV-PRIO-HIGH',
            'medium': 'EV-PRIO-MEDIUM',
            'low': 'EV-PRIO-LOW'
        }

        # Storage for spec objects
        self.spec_objects = []
        self.spec_relations = []

    def _create_header(self, root):
        """Create THE-HEADER section"""
        the_header = SubElement(root, 'THE-HEADER')
        req_if_header = SubElement(the_header, 'REQ-IF-HEADER', IDENTIFIER="HDR-001")

        SubElement(req_if_header, 'CREATION-TIME').text = self.timestamp
        SubElement(req_if_header, 'REQ-IF-TOOL-ID').text = "ReqIF_Generator"
        SubElement(req_if_header, 'REQ-IF-VERSION').text = "1.0"
        SubElement(req_if_header, 'SOURCE-TOOL-ID').text = "ReqIF_Generator"
        SubElement(req_if_header, 'TITLE').text = self.title

    def _create_datatypes(self, datatypes_elem):
        """Create DATATYPES section"""
        # String datatype
        SubElement(datatypes_elem, 'DATATYPE-DEFINITION-STRING',
                   IDENTIFIER=self.dt_string, attrib={'LONG-NAME': 'String'})

        # XHTML datatype
        SubElement(datatypes_elem, 'DATATYPE-DEFINITION-XHTML',
                   IDENTIFIER=self.dt_xhtml, attrib={'LONG-NAME': 'XHTMLString'})

        # Integer datatype
        SubElement(datatypes_elem, 'DATATYPE-DEFINITION-INTEGER',
                   IDENTIFIER=self.dt_integer, attrib={'LONG-NAME': 'Integer'})

        # Status enumeration
        dt_status = SubElement(datatypes_elem, 'DATATYPE-DEFINITION-ENUMERATION',
                               IDENTIFIER=self.dt_status, attrib={'LONG-NAME': 'Status'})
        spec_values_status = SubElement(dt_status, 'SPECIFIED-VALUES')

        status_defs = [
            ('EV-STATUS-DRAFT', 'Draft', '0'),
            ('EV-STATUS-WIP', 'Work-in-progress', '1'),
            ('EV-STATUS-REVIEWED', 'Reviewed', '2'),
            ('EV-STATUS-APPROVED', 'Approved', '3')
        ]

        for identifier, long_name, key in status_defs:
            enum_val = SubElement(spec_values_status, 'ENUM-VALUE',
                                  IDENTIFIER=identifier, attrib={'LONG-NAME': long_name})
            props = SubElement(enum_val, 'PROPERTIES')
            SubElement(props, 'EMBEDDED-VALUE', KEY=key, attrib={'OTHER-CONTENT': long_name})

        # Priority enumeration
        dt_priority = SubElement(datatypes_elem, 'DATATYPE-DEFINITION-ENUMERATION',
                                 IDENTIFIER=self.dt_priority, attrib={'LONG-NAME': 'Priority'})
        spec_values_priority = SubElement(dt_priority, 'SPECIFIED-VALUES')

        priority_defs = [
            ('EV-PRIO-HIGH', 'High', '0'),
            ('EV-PRIO-MEDIUM', 'Medium', '1'),
            ('EV-PRIO-LOW', 'Low', '2')
        ]

        for identifier, long_name, key in priority_defs:
            enum_val = SubElement(spec_values_priority, 'ENUM-VALUE',
                                  IDENTIFIER=identifier, attrib={'LONG-NAME': long_name})
            props = SubElement(enum_val, 'PROPERTIES')
            SubElement(props, 'EMBEDDED-VALUE', KEY=key, attrib={'OTHER-CONTENT': long_name})

    def _create_spec_object_type(self, spec_types_elem, type_id, long_name, prefix):
        """Create a SPEC-OBJECT-TYPE with standard attributes"""
        spec_obj_type = SubElement(spec_types_elem, 'SPEC-OBJECT-TYPE',
                                   IDENTIFIER=type_id, attrib={'LONG-NAME': long_name})
        spec_attrs = SubElement(spec_obj_type, 'SPEC-ATTRIBUTES')

        # ReqIF.ForeignID (Integer)
        attr_foreignid = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-INTEGER',
                                    IDENTIFIER=f"{prefix}-AD-FOREIGNID",
                                    attrib={'LONG-NAME': 'ReqIF.ForeignID'})
        type_ref = SubElement(attr_foreignid, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-INTEGER-REF').text = self.dt_integer

        # ReqIF.Name (String)
        attr_name = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-STRING',
                               IDENTIFIER=f"{prefix}-AD-NAME",
                               attrib={'LONG-NAME': 'ReqIF.Name'})
        type_ref = SubElement(attr_name, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-STRING-REF').text = self.dt_string

        # IE PUID (External textual ID used by visualizer)
        attr_iepuid = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-STRING',
                                 IDENTIFIER=f"{prefix}-AD-IEPUID",
                                 attrib={'LONG-NAME': 'IE PUID'})
        type_ref = SubElement(attr_iepuid, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-STRING-REF').text = self.dt_string

        # ReqIF.ChapterName (String)
        attr_chap = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-STRING',
                               IDENTIFIER=f"{prefix}-AD-CHAP",
                               attrib={'LONG-NAME': 'ReqIF.ChapterName'})
        type_ref = SubElement(attr_chap, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-STRING-REF').text = self.dt_string

        # ReqIF.Description (XHTML)
        attr_desc = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-XHTML',
                               IDENTIFIER=f"{prefix}-AD-DESC",
                               attrib={'LONG-NAME': 'ReqIF.Description'})
        type_ref = SubElement(attr_desc, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-XHTML-REF').text = self.dt_xhtml

        # ReqIF.Prefix (String)
        attr_prefix = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-STRING',
                                 IDENTIFIER=f"{prefix}-AD-PREFIX",
                                 attrib={'LONG-NAME': 'ReqIF.Prefix'})
        type_ref = SubElement(attr_prefix, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-STRING-REF').text = self.dt_string

        # ReqIF.Text (XHTML)
        attr_text = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-XHTML',
                               IDENTIFIER=f"{prefix}-AD-TEXT",
                               attrib={'LONG-NAME': 'ReqIF.Text'})
        type_ref = SubElement(attr_text, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-XHTML-REF').text = self.dt_xhtml

        # Status (Enumeration)
        attr_status = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-ENUMERATION',
                                 IDENTIFIER=f"{prefix}-AD-STATUS",
                                 attrib={'LONG-NAME': 'Status', 'MULTI-VALUED': 'false'})
        type_ref = SubElement(attr_status, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-ENUMERATION-REF').text = self.dt_status

        # Priority (Enumeration)
        attr_priority = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-ENUMERATION',
                                   IDENTIFIER=f"{prefix}-AD-PRIORITY",
                                   attrib={'LONG-NAME': 'Priority', 'MULTI-VALUED': 'false'})
        type_ref = SubElement(attr_priority, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-ENUMERATION-REF').text = self.dt_priority

    def _create_spec_types(self, spec_types_elem):
        """Create SPEC-TYPES section"""
        # Specification Type (Module)
        spec_type = SubElement(spec_types_elem, 'SPECIFICATION-TYPE',
                               IDENTIFIER='T-MODULE',
                               attrib={'LONG-NAME': 'Stakeholder Requirements'})
        spec_attrs = SubElement(spec_type, 'SPEC-ATTRIBUTES')

        # Module ID attribute
        attr_id = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-STRING',
                             IDENTIFIER='AD-MOD-ID', attrib={'LONG-NAME': 'ID'})
        type_ref = SubElement(attr_id, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-STRING-REF').text = self.dt_string

        # Module Description attribute
        attr_desc = SubElement(spec_attrs, 'ATTRIBUTE-DEFINITION-XHTML',
                               IDENTIFIER='AD-MOD-DESC', attrib={'LONG-NAME': 'Description'})
        type_ref = SubElement(attr_desc, 'TYPE')
        SubElement(type_ref, 'DATATYPE-DEFINITION-XHTML-REF').text = self.dt_xhtml

        # Create spec object types
        self._create_spec_object_type(spec_types_elem, 'T-REQ-FUNCTIONAL', 'functional', 'F')
        self._create_spec_object_type(spec_types_elem, 'T-REQ-INTERFACE', 'interface', 'I')
        self._create_spec_object_type(spec_types_elem, 'T-REQ-PERFORMANCE', 'performance', 'P')

        # Relation types
        SubElement(spec_types_elem, 'SPEC-RELATION-TYPE',
                   IDENTIFIER='T-REL-SATISFY', attrib={'LONG-NAME': 'satisfy'})
        SubElement(spec_types_elem, 'SPEC-RELATION-TYPE',
                   IDENTIFIER='T-REL-DERIVE', attrib={'LONG-NAME': 'derive'})
        SubElement(spec_types_elem, 'SPEC-RELATION-TYPE',
                   IDENTIFIER='T-REL-REFINE', attrib={'LONG-NAME': 'refine'})

    def _create_xhtml_element(self, text_content, is_formatted=False):
        """Create an XHTML element for text content"""
        xhtml_div = Element('{http://www.w3.org/1999/xhtml}div')

        if is_formatted:
            # Preserve formatting
            xhtml_div.append(text_content)
        else:
            # Simple paragraph
            xhtml_p = SubElement(xhtml_div, '{http://www.w3.org/1999/xhtml}p')
            xhtml_p.text = text_content

        return xhtml_div

    def add_requirement(self, req_type, foreign_id, name, chapter, description,
                        text_content, status='approved', priority='high',
                        req_prefix='SYS', identifier=None, ie_puid=None):
        """
        Add a requirement to the ReqIF file

        Args:
            req_type: 'functional', 'interface', or 'performance'
            foreign_id: Integer ID for the requirement
            name: Name/title of the requirement
            chapter: Chapter name (e.g., "Chapter 1.1")
            description: Brief description (plain text)
            text_content: Main requirement text (can be XHTML element or plain text)
            status: 'draft', 'wip', 'reviewed', or 'approved'
            priority: 'high', 'medium', or 'low'
            req_prefix: Prefix for requirement (e.g., 'SYS-F')
            identifier: Optional custom identifier (auto-generated if not provided)
        """
        type_map = {
            'functional': ('T-REQ-FUNCTIONAL', 'F', 'F'),
            'interface': ('T-REQ-INTERFACE', 'I', 'I'),
            'performance': ('T-REQ-PERFORMANCE', 'P', 'P')
        }

        if req_type not in type_map:
            raise ValueError(f"Invalid req_type: {req_type}")

        type_ref, prefix_short, attr_prefix = type_map[req_type]

        if identifier is None:
            identifier = f"SO-{prefix_short}-{str(len(self.spec_objects) + 1).zfill(3)}"

        # External textual ID for visualization (IE PUID)
        if ie_puid is None:
            ie_puid = f"REQ-{str(len(self.spec_objects) + 1).zfill(3)}"

        req = {
            'identifier': identifier,
            'type_ref': type_ref,
            'foreign_id': foreign_id,
            'name': name,
            'chapter': chapter,
            'description': description,
            'text_content': text_content,
            'status': self.status_values.get(status.lower(), self.status_values['approved']),
            'priority': self.priority_values.get(priority.lower(), self.priority_values['medium']),
            'req_prefix': req_prefix,
            'attr_prefix': attr_prefix,
            'ie_puid': ie_puid
        }

        self.spec_objects.append(req)
        return identifier

    def add_relation(self, relation_type, source_id, target_id, identifier=None):
        """
        Add a traceability relation between requirements

        Args:
            relation_type: 'satisfy', 'derive', or 'refine'
            source_id: Source requirement identifier
            target_id: Target requirement identifier
            identifier: Optional custom identifier
        """
        type_map = {
            'satisfy': 'T-REL-SATISFY',
            'derive': 'T-REL-DERIVE',
            'refine': 'T-REL-REFINE'
        }

        if relation_type not in type_map:
            raise ValueError(f"Invalid relation_type: {relation_type}")

        if identifier is None:
            identifier = f"SR-{str(len(self.spec_relations) + 1).zfill(3)}"

        rel = {
            'identifier': identifier,
            'type_ref': type_map[relation_type],
            'source': source_id,
            'target': target_id
        }

        self.spec_relations.append(rel)

    def _create_spec_objects(self, spec_objects_elem):
        """Create SPEC-OBJECTS section from stored requirements"""
        for req in self.spec_objects:
            spec_obj = SubElement(spec_objects_elem, 'SPEC-OBJECT',
                                  IDENTIFIER=req['identifier'],
                                  attrib={'LAST-CHANGE': self.timestamp})

            # Type reference
            type_elem = SubElement(spec_obj, 'TYPE')
            SubElement(type_elem, 'SPEC-OBJECT-TYPE-REF').text = req['type_ref']

            # Values
            values = SubElement(spec_obj, 'VALUES')

            # ForeignID
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-INTEGER',
                                  attrib={'THE-VALUE': str(req['foreign_id'])})
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-INTEGER-REF').text = \
                f"{req['attr_prefix']}-AD-FOREIGNID"

            # Name
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-STRING',
                                  attrib={'THE-VALUE': req['name']})
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-STRING-REF').text = \
                f"{req['attr_prefix']}-AD-NAME"

            # ChapterName
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-STRING',
                                  attrib={'THE-VALUE': req['chapter']})
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-STRING-REF').text = \
                f"{req['attr_prefix']}-AD-CHAP"

            # IE PUID (External textual ID)
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-STRING',
                                  attrib={'THE-VALUE': req['ie_puid']})
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-STRING-REF').text = \
                f"{req['attr_prefix']}-AD-IEPUID"

            # Description (XHTML)
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-XHTML')
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-XHTML-REF').text = \
                f"{req['attr_prefix']}-AD-DESC"
            the_value = SubElement(attr_val, 'THE-VALUE')
            the_value.append(self._create_xhtml_element(req['description']))

            # Prefix
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-STRING',
                                  attrib={'THE-VALUE': req['req_prefix']})
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-STRING-REF').text = \
                f"{req['attr_prefix']}-AD-PREFIX"

            # Text (XHTML)
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-XHTML')
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-XHTML-REF').text = \
                f"{req['attr_prefix']}-AD-TEXT"
            the_value = SubElement(attr_val, 'THE-VALUE')

            if isinstance(req['text_content'], Element):
                the_value.append(req['text_content'])
            else:
                the_value.append(self._create_xhtml_element(req['text_content']))

            # Status
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-ENUMERATION')
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-ENUMERATION-REF').text = \
                f"{req['attr_prefix']}-AD-STATUS"
            vals = SubElement(attr_val, 'VALUES')
            SubElement(vals, 'ENUM-VALUE-REF').text = req['status']

            # Priority
            attr_val = SubElement(values, 'ATTRIBUTE-VALUE-ENUMERATION')
            defn = SubElement(attr_val, 'DEFINITION')
            SubElement(defn, 'ATTRIBUTE-DEFINITION-ENUMERATION-REF').text = \
                f"{req['attr_prefix']}-AD-PRIORITY"
            vals = SubElement(attr_val, 'VALUES')
            SubElement(vals, 'ENUM-VALUE-REF').text = req['priority']

    def _create_spec_relations(self, spec_relations_elem):
        """Create SPEC-RELATIONS section from stored relations"""
        for rel in self.spec_relations:
            spec_rel = SubElement(spec_relations_elem, 'SPEC-RELATION',
                                  IDENTIFIER=rel['identifier'],
                                  attrib={'LAST-CHANGE': self.timestamp})

            # Type reference
            type_elem = SubElement(spec_rel, 'TYPE')
            SubElement(type_elem, 'SPEC-RELATION-TYPE-REF').text = rel['type_ref']

            # Source and Target
            source = SubElement(spec_rel, 'SOURCE')
            SubElement(source, 'SPEC-OBJECT-REF').text = rel['source']

            target = SubElement(spec_rel, 'TARGET')
            SubElement(target, 'SPEC-OBJECT-REF').text = rel['target']

    def _create_specifications(self, specifications_elem):
        """Create SPECIFICATIONS section"""
        spec = SubElement(specifications_elem, 'SPECIFICATION',
                          IDENTIFIER='SP-001',
                          attrib={'LONG-NAME': self.title, 'LAST-CHANGE': self.timestamp})

        # Type reference
        type_elem = SubElement(spec, 'TYPE')
        SubElement(type_elem, 'SPECIFICATION-TYPE-REF').text = 'T-MODULE'

        # Values
        values = SubElement(spec, 'VALUES')

        # ID
        attr_val = SubElement(values, 'ATTRIBUTE-VALUE-STRING',
                              attrib={'THE-VALUE': 'SRS-001'})
        defn = SubElement(attr_val, 'DEFINITION')
        SubElement(defn, 'ATTRIBUTE-DEFINITION-STRING-REF').text = 'AD-MOD-ID'

        # Description
        attr_val = SubElement(values, 'ATTRIBUTE-VALUE-XHTML')
        defn = SubElement(attr_val, 'DEFINITION')
        SubElement(defn, 'ATTRIBUTE-DEFINITION-XHTML-REF').text = 'AD-MOD-DESC'
        the_value = SubElement(attr_val, 'THE-VALUE')
        desc_text = f"This module contains system-level requirements for {self.title}."
        the_value.append(self._create_xhtml_element(desc_text))

        # Children (hierarchy)
        children = SubElement(spec, 'CHILDREN')
        for idx, req in enumerate(self.spec_objects, 1):
            spec_hier = SubElement(children, 'SPEC-HIERARCHY',
                                   IDENTIFIER=f"SH-{str(idx).zfill(3)}",
                                   attrib={'LAST-CHANGE': self.timestamp})
            obj = SubElement(spec_hier, 'OBJECT')
            SubElement(obj, 'SPEC-OBJECT-REF').text = req['identifier']

    def generate(self, output_file):
        """Generate the ReqIF XML file"""
        # Ensure XHTML elements use the 'xhtml' prefix consistently for better
        # compatibility with some ReqIF consumers. We avoid registering the
        # default namespace to prevent duplicate attributes.
        from xml.etree.ElementTree import register_namespace
        register_namespace('xhtml', self.NAMESPACES['xhtml'])

        # Create root element
        root = Element('REQ-IF')
        root.set('xmlns', self.NAMESPACES['default'])
        # 'xhtml' namespace is registered above, so no need to set explicitly here

        # Create header
        self._create_header(root)

        # Create core content
        core_content = SubElement(root, 'CORE-CONTENT')
        req_if_content = SubElement(core_content, 'REQ-IF-CONTENT')

        # Data types
        datatypes = SubElement(req_if_content, 'DATATYPES')
        self._create_datatypes(datatypes)

        # Spec types
        spec_types = SubElement(req_if_content, 'SPEC-TYPES')
        self._create_spec_types(spec_types)

        # Spec objects
        spec_objects = SubElement(req_if_content, 'SPEC-OBJECTS')
        self._create_spec_objects(spec_objects)

        # Spec relations
        spec_relations = SubElement(req_if_content, 'SPEC-RELATIONS')
        self._create_spec_relations(spec_relations)

        # Specifications
        specifications = SubElement(req_if_content, 'SPECIFICATIONS')
        self._create_specifications(specifications)

        # Tool extensions (empty)
        SubElement(root, 'TOOL-EXTENSIONS')

        # Create pretty-printed XML
        xml_str = minidom.parseString(tostring(root, encoding='utf-8')).toprettyxml(
            indent="  ", encoding='UTF-8'
        )

        # Write to file
        with open(output_file, 'wb') as f:
            f.write(xml_str)

        print(f"ReqIF file generated: {output_file}")


def create_formatted_xhtml(text_paragraphs_and_lists):
    """
    Helper function to create formatted XHTML content with paragraphs and lists

    Args:
        text_paragraphs_and_lists: List of tuples where each tuple is either:
            ('p', text) for paragraph
            ('ul', [item1, item2, ...]) for unordered list
            ('p_bold', (text_before, bold_text, text_after)) for paragraph with bold

    Returns:
        Element: XHTML div element
    """
    xhtml_div = Element('{http://www.w3.org/1999/xhtml}div')

    for item_type, content in text_paragraphs_and_lists:
        if item_type == 'p':
            p = SubElement(xhtml_div, '{http://www.w3.org/1999/xhtml}p')
            p.text = content
        elif item_type == 'p_bold':
            p = SubElement(xhtml_div, '{http://www.w3.org/1999/xhtml}p')
            before, bold, after = content
            p.text = before
            b = SubElement(p, '{http://www.w3.org/1999/xhtml}b')
            b.text = bold
            b.tail = after
        elif item_type == 'ul':
            ul = SubElement(xhtml_div, '{http://www.w3.org/1999/xhtml}ul')
            for list_item in content:
                li = SubElement(ul, '{http://www.w3.org/1999/xhtml}li')
                if isinstance(list_item, str):
                    li.text = list_item
                elif isinstance(list_item, tuple) and list_item[0] == 'bold':
                    # ('bold', text_before, bold_text, text_after)
                    _, before, bold_text, after = list_item
                    li.text = before
                    b = SubElement(li, '{http://www.w3.org/1999/xhtml}b')
                    b.text = bold_text
                    b.tail = after

    return xhtml_div


# Example usage
if __name__ == "__main__":
    # Create generator
    generator = ReqIFGenerator(title="System Requirements Specification")

    # Add functional requirement 1
    text_content_f1 = create_formatted_xhtml([
        ('p_bold', ('The system ', 'shall', ' provide user authentication functionality that:')),
        ('ul', [
            'Accepts username and password credentials from users',
            'Validates credentials against the user database',
            'Creates a secure session token upon successful authentication',
            'Implements account lockout after 3 consecutive failed login attempts',
            'Logs all authentication attempts (successful and failed) for audit purposes'
        ])
    ])

    req_f1 = generator.add_requirement(
        req_type='functional',
        foreign_id=1001,
        name='User Authentication',
        chapter='Chapter 1.1',
        description='This requirement defines user authentication capabilities for system access control.',
        text_content=text_content_f1,
        status='approved',
        priority='high',
        req_prefix='SYS-F'
    )

    # Add functional requirement 2
    text_content_f2 = create_formatted_xhtml([
        ('p_bold', ('The system ', 'shall', ' enforce password complexity requirements:')),
        ('ul', [
            'Minimum length of 8 characters',
            'At least one uppercase letter (A-Z)',
            'At least one lowercase letter (a-z)',
            'At least one numeric digit (0-9)',
            'At least one special character (!@#$%^&*)',
            'Password expiration after 90 days',
            'Prevention of password reuse (last 5 passwords)'
        ])
    ])

    req_f2 = generator.add_requirement(
        req_type='functional',
        foreign_id=1002,
        name='Password Management',
        chapter='Chapter 1.2',
        description='Password security and complexity requirements to ensure system security.',
        text_content=text_content_f2,
        status='approved',
        priority='high',
        req_prefix='SYS-F'
    )

    # Add interface requirement 1
    text_content_i1 = create_formatted_xhtml([
        ('p_bold', ('The system ', 'shall', ' interface with the user database using the following specifications:')),
        ('ul', [
            ('bold', '', 'Database:', ' PostgreSQL 14.x or higher'),
            ('bold', '', 'Protocol:', ' PostgreSQL native protocol over TCP/IP'),
            ('bold', '', 'Port:', ' 5432 (default) or configurable'),
            ('bold', '', 'Encryption:', ' SSL/TLS 1.3 for all connections'),
            ('bold', '', 'Authentication:', ' Certificate-based authentication'),
            ('bold', '', 'Connection Pooling:', ' Maximum 50 concurrent connections'),
            ('bold', '', 'Timeout:', ' 30 seconds for query execution, 10 seconds for connection establishment')
        ])
    ])

    req_i1 = generator.add_requirement(
        req_type='interface',
        foreign_id=2001,
        name='Database Connection Interface',
        chapter='Chapter 2.1',
        description='Technical interface specification for database connectivity and communication protocols.',
        text_content=text_content_i1,
        status='reviewed',
        priority='high',
        req_prefix='SYS-I'
    )

    # Add interface requirement 2
    text_content_i2 = create_formatted_xhtml([
        ('p_bold', ('The system ', 'shall', ' provide a REST API with the following characteristics:')),
        ('ul', [
            ('bold', '', 'Protocol:', ' HTTPS only (TLS 1.3)'),
            ('bold', '', 'Authentication:', ' OAuth 2.0 with JWT tokens'),
            ('bold', '', 'Data Format:', ' JSON (Content-Type: application/json)'),
            ('bold', '', 'Endpoints:', ' RESTful resource-based URLs'),
            ('bold', '', 'HTTP Methods:', ' GET, POST, PUT, PATCH, DELETE'),
            ('bold', '', 'Rate Limiting:', ' 1000 requests per hour per client'),
            ('bold', '', 'Response Codes:', ' Standard HTTP status codes (200, 201, 400, 401, 403, 404, 500)'),
            ('bold', '', 'API Versioning:', ' URL path versioning (e.g., /api/v1/)')
        ])
    ])

    req_i2 = generator.add_requirement(
        req_type='interface',
        foreign_id=2002,
        name='REST API Interface',
        chapter='Chapter 2.2',
        description='RESTful API interface specification for external system integration.',
        text_content=text_content_i2,
        status='wip',
        priority='medium',
        req_prefix='SYS-I'
    )

    # Add performance requirement
    text_content_p1 = create_formatted_xhtml([
        ('p_bold', ('The system ', 'shall', ' meet the following authentication performance requirements:')),
        ('ul', [
            ('bold', '', 'Response Time:', ' Authentication request shall complete within 2 seconds (95th percentile)'),
            ('bold', '', 'Maximum Response Time:', ' No authentication request shall exceed 5 seconds'),
            ('bold', '', 'Throughput:', ' Support at least 100 concurrent authentication requests'),
            ('bold', '', 'Availability:', ' Authentication service shall have 99.9% uptime')
        ])
    ])

    req_p1 = generator.add_requirement(
        req_type='performance',
        foreign_id=3001,
        name='Authentication Response Time',
        chapter='Chapter 3.1',
        description='Performance requirement for user authentication response time.',
        text_content=text_content_p1,
        status='reviewed',
        priority='high',
        req_prefix='SYS-P'
    )

    # Add traceability relations
    generator.add_relation('satisfy', source_id=req_i1, target_id=req_f1)
    generator.add_relation('derive', source_id=req_p1, target_id=req_f1)
    generator.add_relation('refine', source_id=req_i2, target_id=req_i1)

    # Generate the ReqIF file
    generator.generate('generated_output.reqif')

    print("\nExample completed!")
    print("You can now modify the requirements and regenerate the file.")
