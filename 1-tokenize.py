import io
import PyPDF2
import spacy
import string
import re
import pickle

PT_CHARS="áâãàçéêèíìóôõòúù"

def remove_non_ascii(text):
  printable = set(string.printable + PT_CHARS)
  return ''.join(filter(lambda x: x in printable, text))

def not_header(line):
  # as we're consolidating broken lines into paragraphs, we want to make sure not to include headers
  return not line.isupper()

def extract_statements(nlp, text):
  """
  Extracting ESG statements from raw text by removing junk, URLs, etc.
  We group consecutive lines into paragraphs and use spacy to parse sentences.
  """
  
  # remove non ASCII characters
  text = remove_non_ascii(text)
  
  lines = []
  prev = ""
  for line in text.split('\n'):
    # aggregate consecutive lines where text may be broken down
    # only if next line starts with a space or previous does not end with dot.
    if(line.startswith(' ') or not prev.endswith('.')):
        prev = prev + ' ' + line
    else:
        # new paragraph
        lines.append(prev)
        prev = line
        
  # don't forget left-over paragraph
  lines.append(prev)

  # clean paragraphs from extra space, unwanted characters, urls, etc.
  # best effort clean up, consider a more versatile cleaner
  sentences = []
  for line in lines:
    
      # removing header number
      line = re.sub(r'^\s?\d+(.*)$', r'\1', line)
      # removing trailing spaces
      line = line.strip()
      # words may be split between lines, ensure we link them back together
      line = re.sub('\s?-\s?', '-', line)
      # remove space prior to punctuation
      line = re.sub(r'\s?([,:;\.])', r'\1', line)
      # ESG contains a lot of figures that are not relevant to grammatical structure
      line = re.sub(r'\d{5,}', r' ', line)
      # remove mentions of URLs
      line = re.sub(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*', r' ', line)
      # remove multiple spaces
      line = re.sub('\s+', ' ', line)
      
      # split paragraphs into well defined sentences using spacy
      for part in list(nlp(line).sents):
        sentences.append(str(part).strip())

  return sentences

with open("ambev.pdf","rb") as arq:
    pdfbytes = arq.read()
    open_pdf_file = io.BytesIO(pdfbytes)
    pdf = PyPDF2.PdfFileReader(open_pdf_file)  
    lRaw_text = [pdf.getPage(i).extractText() for i in range(0, pdf.getNumPages())]
    sRaw_text = "\n".join(lRaw_text) 
    spacy.cli.download("pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm", disable=['ner'])
    results = extract_statements(nlp,sRaw_text)
    with open("data/results", "wb") as f:
        pickle.dump(results, f)
     # print(results)
