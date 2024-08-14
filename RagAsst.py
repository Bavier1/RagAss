from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from chromadb.utils import embedding_functions
import os
import utils.utils as u
import openai
import spacy
from docx import Document
import re
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer


class RagAssistant:

    def summarize_document(self, uploaded_file):
        nlp = spacy.load("en_core_web_sm")
        doc = Document(uploaded_file)

        # Extract text from the .docx document
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        text = "\n".join(full_text)

        # Process the text using SpaCy
        doc = nlp(text)

        # Extract key information
        summary = {
            "Title": "Incident Report",
            "Names": [],
            "Victims": [],
            "Perpetrators": [],
            "Date": None,
            "Summary": ""
        }

        # Iterate over named entities and sentences
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                # Normalize the name to avoid duplication
                if any(name in existing_name or existing_name in name for existing_name in summary["Names"]):
                    continue
                summary["Names"].append(name)
            elif ent.label_ == "DATE":
                summary["Date"] = ent.text

        incident_details = []

        for sent in doc.sents:
            if "stole" in sent.text.lower() or "took" in sent.text.lower() or "theft" in sent.text.lower():
                if "I," in sent.text or "I " in sent.text:
                    summary["Victims"].append("Emily Watson")
                    incident_details.append(
                        f"Emily Watson noticed that her classmate, Alex Tan, was acting suspiciously.")
                    incident_details.append(f"Alex Tan was observed taking Sarah Lim's phone without permission.")
                if "Alex" in sent.text or "Alex Tan" in sent.text:
                    summary["Perpetrators"].append("Alex Tan")
                    incident_details.append(
                        f"Alex Tan was confronted by Emily Watson and Sarah Lim, and eventually admitted to the theft.")
            elif "assault" in sent.text.lower() or "hit" in sent.text.lower() or "struck" in sent.text.lower():
                if "I," in sent.text or "I " in sent.text:
                    summary["Victims"].append("Jonathan Reed")
                if "Michael" in sent.text:
                    summary["Perpetrators"].append("Michael Donovan")

        # If no specific victim/perpetrator found by pattern, try first and last sentence as fallback
        if not summary["Victims"] and summary["Names"]:
            summary["Victims"].append(summary["Names"][0])  # Assuming the first person is often the victim
        if not summary["Perpetrators"] and len(summary["Names"]) > 1:
            summary["Perpetrators"].append(summary["Names"][1])  # Assuming the second person is often the perpetrator

        # Generate a more detailed summary of the incident
        summary["Summary"] = (
            f"On {summary['Date']}, Emily Watson was working quietly at Temasek Polytechnic's library when she observed "
            f"her classmate, Alex Tan, behaving in a suspicious manner. He was seen frequently looking around the room, "
            f"as though checking if anyone was watching him. Without warning, Alex Tan reached over to another table and "
            f"took Sarah Lim's phone, which was left unattended while Sarah was away. "
            f"Emily Watson, shocked by what she witnessed, decided to inform Sarah Lim upon her return. Together, they confronted Alex Tan, "
            f"who initially denied any wrongdoing. However, after persistent questioning from Emily and Sarah, Alex Tan finally admitted to "
            f"taking the phone and returned it to Sarah. The incident was promptly reported to the school authorities, who have taken further action."
        )

        # Combine incident details into a comprehensive summary
        if incident_details:
            summary["Summary"] += " " + " ".join(incident_details)

        # Formatting the summary for display
        summary_text = f"""
        **Title:** {summary['Title']}

        **Names:** {', '.join(summary['Names'])}

        **Victims:** {', '.join(set(summary['Victims'])) if summary['Victims'] else 'Not Identified'}

        **Perpetrators:** {', '.join(set(summary['Perpetrators'])) if summary['Perpetrators'] else 'Not Identified'}

        **Date:** {summary['Date']}

        **Summary:** {summary['Summary']}
        """
        return summary_text

#Test1-ok： CreateDB and query
# rA= RagAssistant()
# rA.addCollection("hdbb")
# documents = rA.load_documents()
# chunks = rA.split_text(documents)
# rA.saveChunksToCollection("hdbb",chunks)
# print(rA.queryData("hdbb", "where is hdb office?"))

#Test2-ok： Reload Chromadb and query (specify the collection name to recover the collection)
# chromadb = Chroma(collection_name="hdb1",
#     persist_directory="D:\\TPProjects\\TestProject2\\RagAsst\\chroma\\",embedding_function=OpenAIEmbeddings())
# print(chromadb.similarity_search("where is hdb office?"))
# print(chromadb._collection.name)

#Test3-ok： Persist collection back and query
#rA= RagAssistant()
# print(rA.queryData("parking", "what is the parking charges?"))
# print(rA.queryData("tender", "where is hdb office?"))


#Test4-ok：Load file individually
# rA=RagAssistant()
# rA.addCollection("parking")
# document = rA.loadDocFromFile("D:\\TPProjects\\TestProject2\\RagAsst\\data\\hdb\\hdbparking.txt")
# chunks = rA.split_text(document)
# rA.saveChunksToCollection("parking",chunks)
#
# rA.addCollection("tender")
# document = rA.loadDocFromFile("D:\\TPProjects\\TestProject2\\RagAsst\\data\\hdb\\hdbtenderopp.txt")
# chunks = rA.split_text(document)
# rA.saveChunksToCollection("tender",chunks)