import os
import tkinter as tk
from tkinter import filedialog
from xml.etree import ElementTree as ET


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("500x200")
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.select_file_button = tk.Button(self)
        self.select_file_button["text"] = "Select XML File"
        self.select_file_button["command"] = self.load_file
        self.select_file_button.grid(row=0)

        self.output_entry = tk.Entry(self)
        self.output_entry.grid(row=1)
        self.output_entry.insert(0, "output.xml")

        self.process_button = tk.Button(self)
        self.process_button["text"] = "Process XML"
        self.process_button["command"] = self.process_xml
        self.process_button.grid(row=2)

    def load_file(self):
        self.filename = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=(("XML files", "*.xml"), ("All files", "*.*")))
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, os.path.basename(self.filename).rsplit(".", 1)[0] + "_wrapped.xml")

    def process_xml(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()

        for parent in root.findall(".//items/item"):
            self.wrap_elements(parent, "roll", "rolls")
            self.convert_entire_text_to_source_element(parent)
            
        for parent in root.findall(".//races/race"):
            self.wrap_elements(parent, "trait", "traits")
            self.convert_trait_to_source(parent)

        for parent in root.findall(".//classes/class"):
            self.wrap_elements(parent, "autolevel", "autolevels")
        for parent in root.findall(".//classes/class/autolevels/autolevel/feature"):
            self.wrap_autolevel_featureText_extract_source(parent)

        #Feats: text -> description, extract source
        #Backgrounds: desciption trait -> description & extract source; wrap other traits
        #Spells: wraps rolls, text -> description & extract source
        #Monsters: wrap traits and actions when multiple, description extract source
        for parent in root.findall(".//backgrounds/background"):
            self.convert_entire_text_to_source_element(parent, "feature")

        output_file = os.path.join(os.path.dirname(self.filename), self.output_entry.get())
        tree.write(output_file)

    def wrap_elements(self, parent, element_name, wrapper_name):
        elements = [child for child in parent if child.tag == element_name]
        if len(elements) > 1:
            wrapper = ET.Element(wrapper_name)
            for element in elements:
                parent.remove(element)
                wrapper.append(element)
            parent.append(wrapper)

    def convert_entire_text_to_source_element(self, parent, child_name=None):
        if child_name is None:
            children = parent
        else:
            children = parent.findall(child_name)
        source_texts = [el for el in children if el.tag == "text" and el.text and el.text.startswith("Source:")]
        for source_text in source_texts:
            source = ET.Element("source")
            source.text = source_text.text[8:]
            parent.append(source)
            parent.remove(source_text)
    
    def convert_trait_to_source(self, parent):
        sources = []
        for traits in parent.findall("traits"):
            for trait in traits.findall("trait"):
                text = trait.find("text")
                if text is not None and text.text.startswith("Source:"):
                    source = ET.Element("source")
                    source.text = text.text[8:]
                    sources.append(source)
                    traits.remove(trait)
        if len(sources) > 1:
            sources_wrapper = ET.Element("sources")
            for source in sources:
                sources_wrapper.append(source)
            parent.append(sources_wrapper)
        elif len(sources) == 1:
            parent.append(sources[0])

    def wrap_autolevel_featureText_extract_source(self, parent):
        sources = []
        texts = []
        for text in parent.findall("text"):
            if text.text and text.text.startswith("Source:"):
                source = ET.Element("source")
                source.text = text.text[8:]
                sources.append(source)
                parent.remove(text)
            else:
                texts.append(text)

        if texts:
            description = ET.Element("description")
            for text in texts:
                parent.remove(text)
                description.append(text)
            parent.append(description)

        if len(sources) > 1:
            sources_wrapper = ET.Element("sources")
            for source in sources:
                sources_wrapper.append(source)
            parent.append(sources_wrapper)
        elif len(sources) == 1:
            parent.append(sources[0])





root = tk.Tk()
app = Application(master=root)
app.mainloop()
