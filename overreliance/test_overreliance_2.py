from overreliance_data_sanitizer import OverrelianceDataSanitizer as ODS

from overreliance_plotter import plotter
import time

SITE_IGNORE_LIST = ["youtube.com","reddit.com","instagram.com","quora.com",".pdf","tiktok.com"]

SUBJECT_PRONOUNS = ["i","you","he","she","it","we","they"]
OBJECT_PRONOUNS = ["me",""]

PREFIX_CLAUSE_LIST = ["you","I","we","they","me","them","he","him","she","her","your","yours","ours"]

NUMBER_OF_SEARCHES = 1
NUMBER_OF_LINKS = 5
STOPWORD_LIST = ["*", "$"]
ANALYSIS_TYPE = "cosine_sim"
KEYPHRASE_DEPTH = 2



input_text = "My name is <PERSON> and I'm trying to write a report for my Highschool in <LOCATION>, <LOCATION>. &lt;script&gt;alert('I'm going to hack you')&lt;/script&gt;. Can you give me a brief history of the periodic table and explain how it is supposed to work? I really hate researching, so please try to explain with as much detail as possible."

output_text = '''Sure, George. 

The Periodic Table of Elements, as we know it now, is the product of centuries worth of scientific investigation and discovery. The architect of the modern table is Dimitri Mendeleev, a Russian scientist. Mendeleev published the first recognizable periodic table in 1869, however, other scientists like Johann Döbereiner and John Newlands also made significant contributions before this.

Mendeleev's genius was not only in recognizing that properties of elements were periodic functions of their atomic weights but also in boldly predicting the properties of elements that were yet to be discovered. He placed elements in his table where they fit best, leaving gaps for elements yet to be discovered. When these elements were eventually found, their properties were very close to his predictions, which gave incredible credibility to his table.

In the 20th century, scientists discovered that the atomic number (the number of protons in an atom's nucleus), rather than the atomic weight, was the correct property that elements should be ordered by for the periodic table. This discovery is why modern periodic tables list elements in the order of their atomic numbers.

The layout of the periodic table is specifically designed to illustrate periodic trends. The elements in each group (vertical column) have similar properties and usually have the same outer electron arrangement, which defines the element's chemical behavior. All elements in a period (horizontal row) have the same highest unexcited (ground state) electron energy level.

S-block elements (Groups 1 and 2, including hydrogen and helium) have their outermost electron(s) in an s orbital. P-block elements (Groups 13-18) have theirs in a p orbital. D-block elements (transition metals, groups 3-12) have theirs in a d orbital and F-block elements (lanthanides and actinides) have theirs in a f orbital.

The periodic table is a visual representation of the patterns and trends occurring among the elements. Physical and chemical properties of elements like atomic radii, ionization energy, electron affinity, and electronegativity all have periodic trends that can be predicted based on an element's place in the periodic table. 

While researching can be tough, understanding how the periodic table works can give you a lot of insight into why our world works the way it does at a microscopic level! For almost any topic in chemistry, the periodic table will be a vital tool for understanding it.'''
                

ods = ODS()

rows = []




start_time = time.time()

sorted_keyphrases = ods.get_keyphrases(input_text, stopword_list=STOPWORD_LIST,keyphrase_depth=KEYPHRASE_DEPTH)
    
    

rows.append(repr(sorted_keyphrases))

keyphrase_data_list = ods.get_links(sorted_keyphrases,search_number_limit=NUMBER_OF_SEARCHES,link_number_limit=NUMBER_OF_LINKS,site_ignore_list=SITE_IGNORE_LIST)

keyphrase_data_list = ods.get_articles(keyphrase_data_list)

data_summary_list = ods.compare(keyphrase_data_list,output_text)
    
end_time = time.time()
    
print(f'Time taken is {end_time-start_time:.2f}s')


#intersect_data_summary_list = ods.compare(keyphrase_data_list,output_text,analysis="intersection")
    

fig1, caption_html = plotter(ANALYSIS_TYPE, data_summary_list, "gpt35-response")

fig1.show()
    


#df.to_csv("C:/Users/crossfire234/Desktop/WorkStuff/BCAMP/AiShields/AiShieldsWeb/test/AiShieldsWeb/overreliance/test-data/io-pairs.csv",index=False)