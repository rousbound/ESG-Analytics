import pickle
import spacy
import gensim
from matplotlib import pyplot as plt
from wordcloud import WordCloud
# from sklearn.feature_extraction import text 
import nltk

def tokenize(sentence):
  gen = gensim.utils.simple_preprocess(sentence)
  return ' '.join(gen)

def lemmatize(nlp, text):
  
  # parse sentence using spacy
  doc = nlp(text) 
  
  # convert words into their simplest form (singular, present form, etc.)
  lemma = []
  for token in doc:
      if (token.lemma_ not in ['-PRON-']):
          lemma.append(token.lemma_)
          
  return tokenize(' '.join(lemma))

nlp = spacy.load("pt_core_news_sm", disable=['ner'])

with open("data/results", 'rb') as f:
    l = pickle.load( f)
    print(l)
    text = []
    for el in l:
        results = lemmatize(nlp,el)
        text.append(results)
        print(results)
    bigString = ' '.join(text)

    my_stop_words = ['ambev']
    # stop_words = text.PORTUGUESE_STOP_WORDS.union(my_stop_words)
    #nltk.download("stopwords")
    stop_words = nltk.corpus.stopwords.words("portuguese")
    word_cloud = WordCloud(
        background_color="white",
        max_words=5000, 
        width=900, 
        height=700, 
        stopwords=stop_words, 
        contour_width=3, 
        contour_color='steelblue'
    )

    plt.figure(figsize=(10,10))
    word_cloud.generate(bigString)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("output/output.png")
    
