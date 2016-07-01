'''
Pre-process texts to clean up some common problems
'''

# read files

def fix_sentence_end_without_space(text):
  return re.sub(r"(\w+)([.,…»;:])([A-Z]\w+)", r"\1\2 \3", text)

def replace_smart_quotes(text):
  return text.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2019", '"').replace(u"\u201d", '"')
