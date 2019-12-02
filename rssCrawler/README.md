# RSS crawler
A web crawler which crawls all rss and html docs beginning from an rss opml feeds collection and rate each doc based on its information entropy value.

word_entrophy.csv contains the entropy value p * log(p) per word. It is generated from [the word frequency data](https://www.kaggle.com/rtatman/english-word-frequency) which has counts of 333,333 words.