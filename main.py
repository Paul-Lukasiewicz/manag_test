import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

# Initialiser le client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Fonction pour extraire le texte du PDF
def extraire_texte_pdf(chemin_fichier):
    if isinstance(chemin_fichier, list):
        texte_total = ""
        for fichier in chemin_fichier:
            texte_total += extraire_texte_pdf(fichier)
        return texte_total
    else:
        with open(chemin_fichier, 'rb') as fichier:
            lecteur = PdfReader(fichier)
            texte = ""
            for page in lecteur.pages:
                texte += page.extract_text()
        return texte


# Fonction pour générer une réponse
def generate_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=900,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content


def main():
    
    if "message" not in st.session_state:
        st.session_state.message = []
    
    with st.sidebar:
        st.header("Sélection des documents")
        documents_disponibles = {}
        for fichier in os.listdir("docs"):
            if fichier.endswith(".pdf"):
                nom_fichier = os.path.splitext(fichier)[0]
                documents_disponibles[nom_fichier] = os.path.join("docs", fichier)
        
        if "documents_selectionnes" not in st.session_state:
            st.session_state.documents_selectionnes = []
        
        documents_selectionnes = st.multiselect(
            "Choisissez un ou plusieurs documents à incorporer dans le contexte",
            options=list(documents_disponibles.keys()),
            default=st.session_state.documents_selectionnes,
            key="documents_multiselect"
        )
        
        if documents_selectionnes != st.session_state.documents_selectionnes:
            st.session_state.documents_selectionnes = documents_selectionnes
            st.rerun()
        
        documents_selectionnes_chemins = [documents_disponibles[doc] for doc in documents_selectionnes]
     

    if documents_selectionnes:
        transitory_message = [{"role": "system", "content": f"Vous êtes un assistant utile. Utilisez le contexte qui vous est donné pour répondre aux questions des utilisateurs."}]
        contenu_document = extraire_texte_pdf(documents_selectionnes_chemins)
        transitory_message.append({"role": "system", "content": contenu_document})
        
        for message in st.session_state.message:
            transitory_message.append(message)
        
        st.session_state.message = transitory_message
    
    st.title("Chatbot Test Management")
    messages_container = st.container(height=500)
        
    for message in st.session_state.message:
        if message["role"] != "system":
            messages_container.chat_message(message["role"]).write(message["content"])

    if user_question := st.chat_input("Say something"):
        messages_container.chat_message("user").write(user_question)
        st.session_state.message.append({"role": "user", "content": user_question})

        response = generate_response(st.session_state.message)
        st.session_state.message.append({"role": "assistant", "content": response})
        messages_container.chat_message("assistant").write(response)
        

        
if __name__ == "__main__":
    main()