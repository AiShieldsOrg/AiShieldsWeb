from rake_nltk import Rake
import nltk
import re

try:
    import key2vec.key2vec as key2vec
except:
    import overreliance.key2vec.key2vec as key2vec

nltk.download('punkt')

import asyncio
from playwright.async_api import async_playwright

import requests
from bs4 import BeautifulSoup

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import time

import os

current_path = os.getcwd()
        



class OverrelianceDataSanitizer():
    def __init__(self):
        self.headers_old = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.118 Safari/537.3'}
        self.chrome_path  = "C:/Users/crossfire234/Desktop/Win_x64_1000027_chrome-win/chrome-win/chrome.exe"
    
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
    
    async def search_and_scrape(self, link, search):
        # Launch a new browser instance
        async with async_playwright() as p:
            
            
            DELAY = 0
            #executable_path=self.chrome_path. Seems like it's not needed (maybe because of my system)
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Navigate to a website
            await page.goto(link)

            # Type the search query and press Enter
            await page.type('textarea', search, delay=DELAY)
            await page.keyboard.press('Enter', delay=DELAY)

            # Wait for navigation
            await page.wait_for_load_state('networkidle')

            # Take a screenshot
            #await page.screenshot(path='google1.png')

            # Click an element on the page. Perhaps link filtering should go here
            data = await page.evaluate('''() => {
                const search = document.querySelectorAll('a');
                const urls = Array.from(search).map(v => v.href);
                return urls;
            }''')

            # Close the browser
            await browser.close()

            # Filter the data
            filtered_data = [item for item in data if 'google' not in item and item != '']
            return filtered_data
        
    def search_and_scrape_2(self, link, search_string, delay=0, timeout=5):
        
        query_link = link + f'/search?q={search_string}'
        response = requests.get(query_link, headers=self.headers, timeout=timeout)
        
        time.sleep(delay)
        
        print("response:",response.content)
        html_content = response.content
        

        #quick and dirty, but not great
        soup = BeautifulSoup(html_content, 'html.parser')
        a_tags = soup.find_all('a')
        links = [tag['href'] for tag in a_tags]
        
        links = [link for link in links if 'google' not in link and link != '']
        
        links = [link for link in links if 'https://' in link]
        
        final_links = []
        for link in links:
            if 'url=' in link:
                index = link.find('url=')
                final_links.append(link[index+4:])
            
        return final_links
     
    def _group_and_combine(self,lst):
    # Create a dictionary to group the strings by their scores
        score_dict = {}
        for score, string in lst:
            if score in score_dict:
                score_dict[score].append(string)
            else:
                score_dict[score] = [string]

        # Create a new list with summed scores and concatenated strings
        new_lst = []
        for score, strings in score_dict.items():
            combined_string = ' '.join(strings)
            new_lst.append([sum([score]), combined_string])

        return new_lst   
    
    def _parse_sentences(self,input_text,cutoff_parameter=10):
        sentence_ends = re.finditer(r'[.!?]+(?=\s+|$)',input_text)
        
        sentence_list =[]
        
        indices = []
        indices.append(0)
        for punc_match in sentence_ends:
            print(punc_match.start())
            indices.append(punc_match.start()+1)
            
        print("indices:")
        print(indices)
                
        for i in range(len(indices)-1):
            print(input_text[indices[i]:indices[i+1]])
            
            sentence_list.append(input_text[indices[i]:indices[i+1]])
            
        if len(sentence_list) == 0:
            sentence_list.append(input_text)
        
        return sentence_list
      
      
    def get_keyphrases_key2vec(self, prompt_text,stopword_list=[],keyphrase_depth=1):
        pass
              
    def get_keyphrases(self, prompt_text, stopword_list = [],keyphrase_depth=1,method='rake',spacy_nlp = None):
        
        print("Input prompt:")
        print(prompt_text)
        print()
        
        if method == 'rake':
            rake = Rake()
            cleaned_prompt_text = self.remove_special_sentences(prompt_text)
            
            print("cleaned input text:")
            print(cleaned_prompt_text)
                
            rake.extract_keywords_from_text(cleaned_prompt_text)
            keyword_phrases = list(set(rake.get_ranked_phrases_with_scores()))
                
            ''' word score: deg(w)/feq(w)'''
            ''' deg is the number of co-occurrences of a word in a piece of text. This is the sum of the number of times the word appears in the text, plus the number times the particular word appears next to a different word, which are not stop words, appear next'''
        
        if method == 'key2vec':
            
            #I think this might be more efficient to get the embeddings that are directly
            #relevant to the key2vec algorithm, but I'm not really sure. I believe the vectors should
            #include the proper relationships to the rest of the english corpus
            glove = key2vec.glove.Glove(spacy_nlp=spacy_nlp,text = prompt_text)
            m = key2vec.key2vec.Key2Vec(prompt_text,glove)
            m.extract_candidates()
            m.set_theme_weights()
            m.build_candidate_graph()
            ranked = m.page_rank_candidates()
            keyphrases = [phrase.text for phrase in ranked]
            print("key2vec keyphrases:")
            print(keyphrases)
            keyphrases = list(set(keyphrases))
            
            keyword_phrases = [[len(keyphrases),' '.join(keyphrases)]]
            
        

        sorted_keyphrases = sorted(keyword_phrases, key = lambda x: x[0],reverse=True)
        
        
        
        sorted_keyphrases = list(map(lambda x: list(x),sorted_keyphrases))
        for i, pair in enumerate(sorted_keyphrases):
            term = self._remove_special_chars(pair[1],stopword_list)
            sorted_keyphrases[i][1] = term
        
        print("Raw Sorted Keyphrases:")
        print(sorted_keyphrases)
        
        final_sorted_keyphrases = self._group_and_combine(sorted_keyphrases)    
        
        print("Combined Sorted Keyphrases:")
        print(final_sorted_keyphrases)  
        
        if keyphrase_depth > 1 and keyphrase_depth <= len(final_sorted_keyphrases):
            summed_sorted_keyphrases = []
            for i in range(0,len(final_sorted_keyphrases),keyphrase_depth):
                if i + keyphrase_depth < len(final_sorted_keyphrases):
                    group = final_sorted_keyphrases[i:i+keyphrase_depth]        
                else:
                    group = final_sorted_keyphrases[i:len(final_sorted_keyphrases)]
                
                group_string = ' '.join(item[1] for item in group)
                summed_sorted_keyphrases.append([group[0][0],group_string])
                
                
            '''data = list(list(float,str))'''
         
            print("Depth Combined Sorted Keyphrases")
            print(summed_sorted_keyphrases)   
        
            return summed_sorted_keyphrases
        else:
             return final_sorted_keyphrases  
    
    def get_links(self,sorted_keyphrases, search_number_limit,  site_ignore_list=[],link_number_limit = None,new_search=False):
        keyphrase_data_list=[]
        for pair in sorted_keyphrases[:min(len(sorted_keyphrases), search_number_limit)]:
            
            term = pair[1]
            
            #generating a list of links from the result of the script
            if not new_search:
                link_list = asyncio.run(self.search_and_scrape('https://www.google.com',term))
            if new_search:
                link_list = self.search_and_scrape_2('https://www.google.com',term,delay=2)
               
            #this filters out any link in the site_ignore_list
            link_list = [link for link in link_list if not any(ignore_link in link for ignore_link in site_ignore_list)]
            
            #this automatically removes duplicates
            link_list = list(set(link_list))
            
            #dictionary to be converted to JSON
            data = dict()
            data["score"] = pair[0]
            data["keyphrase"] = term
            if not link_number_limit:
                data["links"] = link_list
            else:
                data["links"] = link_list[:min(len(link_list), link_number_limit)]
            
            keyphrase_data_list.append(data)
        
        ''' data = list({score: float, keyphrase: string, links: list(str)})'''
        
        return keyphrase_data_list
    
    def remove_special_sentences(self,text):
        # Split the text into sentences
        sentences = re.split(r'[.!?][\s\n]+', text)
        
        print(sentences)

        # Create a list to store the cleaned sentences
        cleaned_sentences = []

        for sentence in sentences:
            # Check if the sentence contains a string in all caps within angled brackets
            if not re.search(r'<[A-Z]+>', sentence) and not re.search(r'&lt;script&gt;.*?&lt;/script&gt;', sentence):
                # Remove text between < and >
                cleaned_sentences.append(sentence)
                print("clean sentence:")
                print()
                print(sentence)

        # Join the cleaned sentences back into a single string
        cleaned_text = ' '.join(cleaned_sentences)

        return cleaned_text
        
    def get_keyphrases_and_links(self,prompt_text, search_number_limit,link_number_limit = None, stopword_list =[]):
        
        print(search_number_limit)
    
        rake = Rake()
        
        cleaned_prompt_text = self.remove_special_sentences(prompt_text)
        #get the unique list of phrases
        rake.extract_keywords_from_text(cleaned_prompt_text)
        keyword_phrase = list(set(rake.get_ranked_phrases_with_scores()))
        
        #sort by the score (highest)
        sorted_keyphrases = sorted(keyword_phrase, key= lambda x: x[0], reverse=True)
        
        keyphrase_data_list = []
        
        #it either the length of the number of keyphrases, or the desired search list. Because of the sorting, higher scored phrases are searched first
        for pair in sorted_keyphrases[:min(len(sorted_keyphrases), search_number_limit)]:
            
            term = self._remove_special_chars(pair[1],stopword_list)
            
            print("performing search on keyword:",term)
            
            #generating a list of links from the result of the script
            link_list = asyncio.run(self.search_and_scrape('https://www.google.com',term))
            
            #dictionary to be converted to JSON
            data = dict()
            data["score"] = pair[0]
            data["keyphrase"] = term
            if not link_number_limit:
                data["links"] = link_list
            else:
                data["links"] = link_list[:link_number_limit]
            
            keyphrase_data_list.append(data)
        
        ''' data = list({score: float, keyphrase: string, links: list(str)})'''
        
        return keyphrase_data_list
    
    ''' get_articles '''
    
    def get_articles(self,keyphrase_data_list,auto_ignore_flag = True, timeout=5):
        for i, data in enumerate(keyphrase_data_list):
            print()
            print("Keyphrase:",data["keyphrase"])
            print()
            
            
            for j, link in enumerate(data["links"]):
                
                print("scraping:",link)
                    
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
                    continue
                except Exception as e:
                    keyphrase_data_list[i]["links"][j] = {"link": link, "text": None}
                    print('A different error occurred. Moving on...')
                    continue
                
                    
        ''' data = list({score: float, keyphrase: string, links: list({link: str, text: str or None})})'''
                    
        return keyphrase_data_list
    
    ''' compare '''
    def compare(self, keyphrase_data_list, response_text, analysis="cosine_sim"):
        docs = []
        links = []
        data_summary_list = []
        
        #--- THIS IS WHY IT MUST BE ITERATED LATER ---
        keyphrase = keyphrase_data_list[0]["keyphrase"]
        
        #extract links and text. ITERATE THIS LATER!!!
        for entry in keyphrase_data_list[0]["links"]:
            if entry["text"] != None and entry["link"] not in links:
                docs.append(entry["text"].strip("\n"))
                links.append(entry["link"])
                
                
        for document, link in zip(docs,links):
        
            data_summary = dict()
            
            data_summary['keyphrase'] = keyphrase
            data_summary['text'] = document
            data_summary['link'] = link
            
            if analysis == "cosine_sim":
            
                vectorizer = TfidfVectorizer()

                # Fit and transform the documents to get the vector representations
                X = vectorizer.fit_transform([response_text, document])

                # Calculate the cosine similarity between the two document vectors
                cosine_sim = (X[0] * X[1].T).toarray()[0,0] / (np.linalg.norm(X[0].toarray()) * np.linalg.norm(X[1].toarray()))

                print(f"The cosine similarity between the text and {link} is: {cosine_sim:.2f}")
                
                data_summary['score'] = cosine_sim
                
            if analysis == "intersection":
                doc_set = set(document)
                text_set = set(response_text)
                
                overlap_set = doc_set.intersection(text_set)
                
                overlap = len(overlap_set)/len(text_set)
                
                print(f"The percentage overlap between the text and {link} is: {overlap:.2f}")
                data_summary['score'] = overlap
                
            
            data_summary_list.append(data_summary)
        
        return data_summary_list
