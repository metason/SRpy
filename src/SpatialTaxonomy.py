from threading import Thread
from typing import List, Optional
import xml.etree.ElementTree as ET
from threading import Thread
from typing import List, Optional

class SpatialObjectConcept:
    
    
    def __init__(self, label: str, id:str =None, parentId:str=None):
        
        self.label = label
        if id is None:
            self.id = label
        else:
            self.id = id
        self.parentId = parentId
        
        self.comment = ""
        self.synonyms: List[str] = None
        self.parent:SpatialObjectConcept = None
        self.children: List[SpatialObjectConcept] = None
        self.references: List[str] = None
        
    def addChild(self, child: 'SpatialObjectConcept'):
        if self.children is None:
            self.children = []
        self.children.append(child)
        
    def addSynonym(self, synonym: str):
        if self.synonyms is None:
            self.synonyms = []
        self.synonyms.append(synonym)
    
    def addRef(self, reference: str):
        if self.references is None:
            self.references = []
        self.references.append(reference)
        
    def isa(self, type: str, precise: bool) -> 'SpatialObjectConcept':
        query = type.lower()
        if query == self.label.lower():
            return self
        
        synonyms = self.synonyms
        if synonyms is not None:
            for syn in synonyms:
                if syn.lower() == query:
                    return self
                
        if self.parent is not None:
            return self.parent.isa(type, precise)
        
        if not precise:
            if query in self.label.lower(): 
                return self
            if synonyms is not None:
                for syn in synonyms:
                    if query in syn.lower():
                        return self
        return None
    
    def asText(self, level: int = 0, prefix: str = "- ", indent: str = "  "):
        string = indent * level + prefix + self.label
        
        if self.synonyms is None:
            string = string + " ("  + ", ".join(self.synonyms) + ")" + "\n"
        else:
            string = string + "\n"
        if self.children is not None:
            for child in self.children:
                string = string + child.asText(level + 1, prefix, indent)
        return string
    
    def __eq__ (self, other: 'SpatialObjectConcept') -> bool:
        if isinstance(other, SpatialObjectConcept):
            return self.label == other.label
        return False
    
class TaxonomyParser:
    def __init__(self):
        self.label: str = ""
        self.comment: str = ""
        self.id: str = ""
        self.parentId: str = ""
        self.synonyms: List[str] = []
        self.references: List[str] = []
        self.currentAttribute: str = ""

    def addConcept(self):
        if self.label:
            concept = SpatialObjectConcept(label=self.label, id=self.id, parentId=self.parentId)
            concept.comment = self.comment
            if self.synonyms:
                concept.synonyms = self.synonyms
            if self.references:
                concept.references = self.references
            SpatialTaxonomy.concepts.append(concept)

        self.label = ""
        self.comment = ""
        self.id = ""
        self.parentId = ""
        self.synonyms = []
        self.references = []
        self.currentAttribute = ""

    def parse(self, file_path: str):
        tree = ET.parse(file_path)
        root = tree.getroot()
        self._parse_element(root)
        self.addConcept()  # In case the last element is valid

    def _parse_element(self, element):
        tag = self._strip_ns(element.tag)
        if tag == "Class":
            self.addConcept()
            rdf_about = element.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
            if rdf_about:
                self.id = rdf_about
        elif tag == "subClassOf":
            rdf_resource = element.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if rdf_resource:
                self.parentId = rdf_resource
        elif tag == "seeAlso":
            rdf_resource = element.attrib.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if rdf_resource:
                self.references.append(rdf_resource)

        self.currentAttribute = tag

        for child in element:
            self._parse_element(child)
            if child.text and child.text.strip():
                text = child.text.strip()
                if self.currentAttribute == "label":
                    self.label = text
                elif self.currentAttribute == "comment":
                    self.comment = text
                elif self.currentAttribute == "altLabel":
                    self.synonyms.append(text)

    def _strip_ns(self, tag):
        return tag.split('}')[-1] if '}' in tag else tag


class SpatialTaxonomy:
    concepts: List[SpatialObjectConcept] = []

    @classmethod
    def load(cls, file_path: str, replace_existing: bool = True):
        def parse_thread():
            parser = TaxonomyParser()
            parser.parse(file_path)
            cls.buildHierarchy()
        
        if replace_existing:
            cls.concepts.clear()

        Thread(target=parse_thread).start()

    @classmethod
    def buildHierarchy(cls):
        for concept in cls.concepts:
            if concept.parent is None and concept.parentId:
                parent = cls.getConcept(concept.parentId)
                if parent:
                    concept.parent = parent
                    parent.addChild(concept)

    @classmethod
    def getConcept(cls, concept_id: str) -> Optional[SpatialObjectConcept]:
        return next((c for c in cls.concepts if c.id == concept_id), None)

    @classmethod
    def getConceptByLabel(cls, label: str) -> Optional[SpatialObjectConcept]:
        return next((c for c in cls.concepts if c.label.lower() == label.lower()), None)

    @classmethod
    def searchConcept(cls, query: str, precise: bool = True) -> Optional[SpatialObjectConcept]:
        concept = cls.getConceptByLabel(query)
        if concept:
            return concept

        for c in reversed(cls.concepts):
            if any(s.lower() == query.lower() for s in c.synonyms or []):
                return c

        if not precise and len(query) > 2:
            q = query.lower()
            for c in reversed(cls.concepts):
                # match in the label…
                if q in c.label.lower():
                    return c
                # …or in any synonym
                if any(q in syn.lower() for syn in (c.synonyms or [])):
                    return c
        return None

    @classmethod
    def topConcepts(cls) -> List[SpatialObjectConcept]:
        return [c for c in cls.concepts if c.parent is None]

    @classmethod
    def asText(cls, prefix: str = "- ", indent: str = "  ") -> str:
        return ''.join([c.asText(prefix=prefix, indent=indent) for c in cls.topConcepts()])