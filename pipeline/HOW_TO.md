# Pipeline

This part of the code manages the data processing of files. Here

```bash
.
├── HOW_TO.md           # directory
├── bin                 # executables 
├── build_graph.py      # building the graph from the vector db
├── claude.py           # topic modelling 
├── embedding.py        # embedding the entire database
├── main.py             # build the dataframe
└── utils.py            # functions 

```

## 1. Acquiring  data

The data is acquired by running the executable provided in `bin/`. This executable is built from [sbstck-dl](https://github.com/alexferrari88/sbstck-dl). I have forked it and made changes for adding author, post_date, title to the metadata.

You can run the executable in the following manner 

```bash
sbstck-dl download --url <substack-url> -f "md" -o <output-dir>
```

## 2. Cleaning the data

The data that we get will be markdown file which has a lot of formatting characters like bolds, italics, etc. So to effectively work with it, we need to download the file and remove all formatting. This is done in the `clean_md` function in `utils.py`.

## 3. Topic Modelling

Topic modelling was the toughest. Ultimately I just used Claude 3 Haiku. You can read about my process with this on the [blog for this project](https://www.itskeane.info/blog/reader)

## 4. Embedding

This was straightforward, I just used the default `all-MiniLM-L6-v2` from SentenceTransformers for embeddings. I didn't think too much about this. Perhaps I could have gotten better results with a different model more suited for summarized texts or trained on an academic corpus. On second thought, probably an [InstructorEmbedding](https://github.com/xlang-ai/instructor-embedding) would have been better for clustering if I instructed it correctly. There's scope to improve.

## 5. Building the graphs

This was straightforward again. I borrowed most of the code from [Nexus](https://github.com/freeman-jiang/nexus). The only major changes were the recommended authors.
