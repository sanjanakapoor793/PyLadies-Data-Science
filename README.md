 # Enron Email Analysis

## Overview

This repository contains the classes to create a pipeline that creates and saves NLP models as well as the tools to use that model to analyze your corpus. The goal of the pipeline is to streamline the standard steps that are required when generating a model. 

As of right now, the pipeline is equipped to generate LDA Models. 

Latent Dirichlet Allocation (LDA) is a model that analyzes unobserved groups and is able to group them based off of their "hidden" topics. 


## NLP Primer

<b> NLP</b>: Natural Language Processing

<b> Token</b>: An individual unit of text (string format)

<b> Document</b>: A single text

<b> Corpus</b>: Collection ('body') of documents being analyzed

<b> Stop Words</b>: Common words that don't contribute to document meaning. 

<b> Bag of Words</b>: Simplifying representation that omits grammar and word order and tracks word occurrence. 

## Pipeline Process

![Screenshot](TopicModelingDataProcess.png)

In the visual, three different steps are shown: 
* Extract, Transform, Load
* Feature Reduction
* Generating Model

In the Extract, Transform, Load (ETL) step, you are preparing the data to be cleaned. This step is done in the store_data.py file. 

In the Feature Reduction step, you are removing the noisy elements or elements that make it harder to interpret your data. This step is done using the text_pipeline package. 

In the Generating Model step, you generate the LDA Model using LDA.py. 

## Using Your Model

### Document Topic Vectors

After generating your model, you need to generate the document topic vectors. These vectors can be used for finding similar documents or for doing semantic searches (amongst other things). 

```
document_corpus_value = corpus[document_counter]
document_topic_vector = lda.get_document_topics(document_corpus_value)
```

The above code snippet shows how to generate a document topic vector. First, you must get the bag of words (BoW) representation of the document. From the definition above, we know that the BoW representation of a document is a list of tuples that tracks the index of each word as well as the frequency that it occurs. 

Below is the format of a BoW representation of a document. 

![Screenshot](BagOfWords.png)

Now that we have our BoW representation of the document ready, we will call the get_document_topics method on the ldamodel and pass in our BoW as the parameter. 
This will return the document's topic vector. 

### Nearest Neighbors Search

Nearest Neighbors Search is defined as the process of finding points from a given set that are most similar to your starting point. 

![Screenshot](NearestNeighbors.png)

Looking at the image above, you can identify the starting point as the center data point and the 5 nearest neighbors as the data points closest to the starting point. This is a simple illustration of how nearest neighbors works. When doing a nearest neighbors search with your corpus, instead of comparing 2D points like in the image, you'll be comparing N-D points, where N is the number of topics you set your LDA Model to find.

This code uses NMSLib when conducting its nearest neighbors searches. NMSLib stands for Non-Metric Space Library. 

```
index = nms.init(method = 'hnsw', space = 'cosinesimil')
for vector in self.emailCol.find9 {'$query': {}, '$orderby': {'email_counter': 1} } ):
	index.addDataPoint(vector['email_counter'], vector['topic_vector'])
index.createIndex()
```

To create the index you must pass in the method and space. They are set to 'hnsw' and 'cosinesimil' respectively. These parameters have been optimized for nearest neighbors	searches and are quite good for text analysis. 

After calling .init, you must add all the data points to the index. In this case, each data point is a document topic vector. 

To conduct a nearest neighbors search, you must query the index created using NMSLib with the starting email's document topic vector. This would return a list of IDs of emails that have the closes document topic vectors to the starting document's topic vector. 


### Semantic Search

Semantic Search is useful in how it returns documents that may not contain the actual word you search for, but are heavily related to the topic of the search word. 

The way semantic search works is, first, the user must input some search words. The model will then treat those words as a new document and will generate a topic vector for it. The process for generating a topic vector is the same as stated in the Document Topic Vector section of the ReadMe where you must first generate the BoW representation of the document and then feed that into the get_document_topics method that the lda model calls. Then query the index by this new topic vector, and this will yield IDs of documents that are most similar to the topic vector of the search words. 