
symbol_dict = {
    "&amp;": "&",
    " ": " ",
    "–": "-",
    "“": "\"",
    "”": "\"",
}


def process_string(string):
  if not string:
    return ""
  string = str(string)
  for key, value in symbol_dict.items():
    string = string.replace(key, value)
  return string
