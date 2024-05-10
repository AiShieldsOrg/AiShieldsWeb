from rake_nltk import Rake
import subprocess

import requests
from bs4 import BeautifulSoup

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import time



class OverrelianceDataSanitizer():
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        
    
    ''' get_keyphrases '''
    
    ''' this function is private'''
    def _remove_special_chars(self,text,stopword_list):
        # Define the characters you want to remove
        remove_chars = ''.join(stopword_list)
        
        # Create a translation table that maps the characters to be removed to None
        translation_table = str.maketrans('', '', remove_chars)
        
        # Use the translate() method to remove the specified characters
        cleaned_text = text.translate(translation_table)
        
        return cleaned_text
    
    ''' this function is not intended for use at the moment, but it's intended purpose is for more complicated website extraction. Perhaps this should just be left to more custom methods. It also likely will be superceded by the puppeteer script because there are certain cookie fields that we have to pass to get to the real data on some websites
    
    idea for it: extract all elements which have non empty text, then store the element name and text
    '''
    def _extract_text(self,element,index):
        text = element.get_text() #setting strip=True removes the spaces created in the original text
        if element.name != 'script':
            for child in element.children:
                if hasattr(child, 'children'):
                    index +=1
                    text += self._extract_text(child,index)
        return text
    
    def get_keyphrases(self,prompt_text, search_script_path, search_number_limit,link_number_limit = None, stopword_list =[]):
    
        rake = Rake()
        
        #get the unique list of phrases
        rake.extract_keywords_from_text(prompt_text)
        keyword_phrase = list(set(rake.get_ranked_phrases_with_scores()))
        
        #sort by the score (highest)
        sorted_keyphrases = sorted(keyword_phrase, key= lambda x: x[0], reverse=True)
        
        keyphrase_data_list = []
        
        #it either the length of the number of keyphrases, or the desired search list. Because of the sorting, higher scored phrases are searched first
        for pair in sorted_keyphrases[:min(len(sorted_keyphrases), search_number_limit)]:
            
            term = self._remove_special_chars(pair[1],stopword_list)
            
            print("performing search on keyword:",term)
            result = subprocess.run(["node", "googlesearch2.js", term], cwd=search_script_path ,capture_output=True,text=True)
            
            #generating a list of links from the result of the script
            link_list = result.stdout.split()
            
            #dictionary to be converted to JSON
            data = dict()
            data["score"] = pair[0]
            data["keyphrase"] = term
            if not link_number_limit:
                data["links"] = link_list
            else:
                data["links"] = link_list[:link_number_limit]
            
            keyphrase_data_list.append(data)
        
        return keyphrase_data_list
    
    ''' get_articles '''
    
    def get_articles(self,keyphrase_data_list,auto_ignore_flag = True, site_ignore_list=[], timeout=5):
        for i, data in enumerate(keyphrase_data_list):
            print()
            print("Keyphrase:",data["keyphrase"])
            print()
            for j, link in enumerate(data["links"]):
                print()
                print(link)
                print()
                if all(ignored not in link for ignored in site_ignore_list):
                    try:
                        response = requests.get(link, headers=self.headers, timeout=timeout)
                        html_content = response.content

                        #quick and dirty, but not great
                        soup = BeautifulSoup(html_content, 'html.parser')
                    
                        full_text = soup.text
                        keyphrase_data_list[i]["links"][j] = {"link": link, "text": full_text}
                        
                    except requests.exceptions.Timeout:
                        keyphrase_data_list[i]["links"][j] = {"link": link, "text": None}
                        print("Request timed out. Moving on...")
       
                else:
                    keyphrase_data_list[i]["links"][j] = {"link": link, "text": None}
                    
        return keyphrase_data_list
    
    ''' compare '''
    def compare(self, keyphrase_data_list, response_text):
        docs = []
        links = []
        data_summary_list = []
        
        #extract links and text. ITERATE THIS LATER!!!
        for entry in keyphrase_data_list[0]["links"]:
            if entry["text"] != None and entry["link"] not in links:
                docs.append(entry["text"].strip("\n"))
                links.append(entry["link"])
                
        for document, link in zip(docs,links):
        
            data_summary = dict()
            
            vectorizer = TfidfVectorizer()

            # Fit and transform the documents to get the vector representations
            X = vectorizer.fit_transform([response_text, document])

            # Calculate the cosine similarity between the two document vectors
            cosine_sim = (X[0] * X[1].T).toarray()[0,0] / (np.linalg.norm(X[0].toarray()) * np.linalg.norm(X[1].toarray()))

            print(f"The cosine similarity between the text and {link} is: {cosine_sim:.2f}")
            
            data_summary['link'] = link
            data_summary['text'] = document
            data_summary['score'] = cosine_sim
            
            data_summary_list.append(data_summary)
        
        return data_summary_list