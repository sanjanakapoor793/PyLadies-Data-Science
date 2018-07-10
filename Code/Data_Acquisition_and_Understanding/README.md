 # Enron Email Analysis

## Data_Acquisition_and_Understanding

### Pipeline.py

<pre>
<i> class </i> Pipeline(<i>*steps</i>)
</pre>

```
import text_pipeline
from Pipeline import Pipeline
from store_data import EmailDataStorage
from LDA import LDAModelMaker

emails = EmailDataStorage()

tokenizer = text_pipeline.Tokenizer('spacy')
token_filter = text_pipeline.TokenFilter('spacy')
stemmer = text_pipeline.Stemmer('spacy')
pre_processing = text_pipeline.Pipeline(tokenizer, token_filter, stemmer)

lda = LDAModelMaker(create = True, 
                    texts_filepath = filepath, 
                    corpus_filepath = filepath, 
                    dictionary_filepath = filepath, 
                    lda_filepath = filepath, 
                    pyldavis_filepath = filepath, 
                    database = 'mongo', 
                    num_topics = 35, 
                    minimum_probability = 0.00, 
                    passes = 5)

topic_model_pipeline = Pipeline(emails, pre_processing, lda)
```

In the code snippet above, emails, pre_processing, and lda were instantiated and then passed in as parameters to the Pipeline class.

##### Class Parameters:
* steps: List of objects to be applied to the data. Variable length of list.  

#### apply(self, result)
Calls a step in the pipeline. 


## store_data.py 

<pre>
<i> class </i> EmailDataStorage(<i>reading_process</i> = 'csv', <i>database</i> = 'mongo')
</pre>


This file reads the data and puts it into a database. Both the type of file the code reads the data from and the database to use have to be set when creating the object. Currently, the type of file defaults to csv and the database defaults to MongoDB. 

The _id will be the unique ID each email has. 

```
store_csv_files = EmailDataStorage('csv', 'mongo')
```

##### Class Parameters: 
* reading_process (str):
	Sets the type of file we will be reading the data from. 
* database (str):
	Sets the type of database we will be moving the data to. 

#### csv(self, filepath)
This method will navigate to the folder where the CSV files are stored and will read them. As it reads a row (and that row meets the necessary requirements), the row will be passed to the add_data method to be added to the database. 

##### Parameters:
* filepath (str):
	The location of the csv files.  

#### mongo(self, row)
Here the row is being added to MongoDB. The fields that we require we pull from row and store. A few fields require cleaning, so the cleaned versions of those fields are returned from method calls such as clean_emails and clean_content. 

##### Parameters:
* :param {tuple} row: Tuple of values that contain the information about a specific email. 

The snippet of code below shows the fields in the database. 
```
email_data = {
            '_id': row[1].lstrip('<').rstrip('>'), # this is the message id
            'date': row[2],
            'sender': row[6],
            'sender_email': self.clean_emails(row, True),
            'recipient': row[7], 
            'recipient_email': self.clean_emails(row, False), 
            'subject': row[5], 
            'cc': row[8], 
            'bcc': row[9], 
            'content': self.clean_content(row[13]),
            'email_counter': eval(row[0]), 
        }
```

#### clean_emails(self, row, sender_recip)
This method cleans the sender and recipient fields in row. Different values are required depending on whether or not we are currently cleaning a sender email or a recipient email. 

##### Parameters: 
* row (tuple): Tuple of values that contain the information about a specific email. 
* sender_recip (boolean): Indicates whether or not this is the sender's email or recipient's email

#### clean_content(self, unfiltered_content)
This method removes repeated sets of characters that add no meaning to the message. Remember, these changes are occurring in the original version of the email. That way if the user wants to see the original content (before the processing) they can see a clean version that doesn't have all those useless characters. 

##### Parameters:
* unfiltered_content (str): Content of one (singular) email


## LDA.py 

<pre>
<i> class </i> LDAModelMaker(<I>create</I>, <I>texts_filepath</I>, <I>corpus_filepath</I>, <I>dictionary_filepath</I>, <I>lda_filepath</I>, 
    <I>pyldavis_filepath</I>, <I>database</I> = None, <I>**run_parameters</I>)
</pre>

This class will use a dictionary and corpus to generate a LDA Model that will be used for future analysis. 

If create is true, then at the end of the process there will be saved versions of the texts, corpus, dictionary, lda model, and pyLDAvis model. These can (and will) be used later. 

Otherwise (if create is false), there will just be a new lda model and a new pyLDAvis model. The texts, corpus, and dictionary files will be unaffected (since we are just reading from them and not changing them).

##### Class Parameters:
* create (boolean): Whether or not we must create the corpus and dictionary or simply load them from a file. 
* texts_filepath (str): Either the location of where to load texts from or where we must save texts to. 
* corpus_filepath (str): Location of where we must save or load the corpus from. 
* dictionary_filepath (str): Location of where we must save or land the dictionary from. 
* lda_filepath (str): Location of where we must save the lda model to. 
* pyldavis_filepath (str): Location of where we must save the pyldavis to.
* database (str): Which kind of database we will be using. 

#### create_corpus_dict(self, texts)
Save the filtered content returned from the pipeline, create the corpus and dictionary, save the filtered contents and corpus value of each document in the database and then generate the lda model. 

##### Parameters:
* texts (list[list[str]]): the filtered content from the preprocessing pipeline. 

#### mongo(self)
Set up MongoDB for future use. 

This method has no parameters. 

#### load_corpus_dict(self, x)
Load the corpus, dictionary, and texts and create the LDA model. 

#### save_texts(self)
Save the list of list of tokens that way we don't need to recompute them in the future. 

This method has no parameters. 

#### load_texts(self)
Load texts (list of list of tokens) from the file it was saved to earlier. 

This method has no parameters.

#### load_dictionary(self)
Load the dictionary from the file it was saved to earlier. 

This method has no parameters.

#### load_corpus(self)
Load the corpus from the file it was saved to earlier. 

This method has no parameters.

#### set_dict_corp(self)
Update the dictionary with the new documents, generate the corpus with the new dictionary and save both. 

This method has no parameters.

#### make_corpus(self)
Make the corpus from the dictionary. 

This method has no parameters. 

#### get_domain(self, list_filtered_emails, email)
Find the domain of the sender and recipient emails. 

##### Parameters: 
* :param {str} list_filtered_emails: List of filtered emails. 
* :param {line in database} email: One line in the database

#### email_database_content(self)
Here we group the tokens in one document back together that way we can see the filtered document as one long string instead of a list of tokens. 

No parameters. 

#### set_email_database(self)
Add the filtered content and corpus for each email to their row in the database.

No parameters.

#### fit_LDA(self)
Generate / fit the LDA model. Both the model generated and a pyLDAvis representation of the model will be saved. Both can (and will) be used for future analysis. 

This method has no parameters.


## docTopicVector.py

<pre>
<I> class </I> DocumentTopicVectorStorage(<I>lda_model_location</I>, <I>corpus_location</I>, <I>database</I> = 'mongo')
</pre>

##### Class Parameters: 
* lda_model_location (str): Filepath to the LDAModel.
* corpus_location (str): Filepath to the corpus.
* database (str): Type of database used. Default to MongoDB. 

End result: The topic vectors for each document will be stored in the database under field 'topic_vector'. 

#### apply(self)
Load the corpus and iterate through it. For each row in the corpus, generate the document topic vector for that document and store it in the database. 

This method has no parameters. 

#### mongo(self, email_counter, vector)
Update each document in the database with the appropriate topic vector. 

##### Parameters: 
* email_counter (int): Way of identifying a document being placed in the database. Will be used as email_counter in database
* vector (list[tuples]): List of tuples that indicate the topic distribution for that document

## similarDoc.py 

<pre>
<I> class </I> SimilarDoc(<I>index_filepath</I>, <I>create_index</I> = False)
</pre>

##### Class Parameters: 
* index_filepath (str): Location of where to load or save index from/to. 
* create_index {bool}: Determines whether or not a new index has to be made. Default is False. 

Finds the nearest neighbors to a particular document or topic vector. We will use this in the future when conducting semantic searches (searches related to the topic vectors of a document and the words being searched). 

#### set_up(self)
Add documents to index, create index, and then return to __init__

This method has no parameters. 

#### similar_from_id(self, document_id)
Runs nearest neighbors to find the closest documents given the document's id. 

##### Parameters:   
* document_id (str): _id that corresponds to a document in the DocTopicVectors database. 

#### similar_from_topic_vector(self, curr_vector)
Runs nearest neighbors to find the num closest documents given the vector. 

##### Parameters: 
* curr_vector (list[tuples]): Document topic vector for the base document (the document we start off with). 

#### save_index(self, filepath)
Save the index to a given location. 

##### Parameters:
* filepath (str): Location of where to save the index to. 

#### load_index(self, filepath)
Load the index from the given location. 

##### Parameters: 
* filepath (str): Location of where to load the index from. 


## searchFeatures.py 

<pre> 
<I> class </I>(<I>keyword</I>, <I>topic_search</I>, <I>*words</I>, <I>dict_filepath</I> = None, <I>lda_filepath</I> = None, 
                 <I>index_filepath</I> = None, <I>create_index</I> = False)
</pre>
##### Class Parameters: 
* keyword (boolean): True if user wants to do a keyword search for the exact word in the text. 
* topic_search (boolean): True if user wants to do a topic search for the exact word in the text
* *words (list[str]): Words that the user wants to search by. 
* dict_filepath (str): Where to load dictionary from
* lda_filepath (str): Where to load LDA Model from
* index_filepath (str): Where to load/save index to. 
* create_index (str): Whether or not we need to create a new index. 

If keyword (bool) is true, then 20 documents that contain the words passed in will be returned. If topic_search is true, then 20 documents that are similar to the topic vector of the words will be returned. 

#### semantic_search(self, dict_filepath, lda_filepath, index_filepath, create_index)
Generates a topic vector based off the words inputted by the user. Use this topic vector to find num nearest neighbors. 

##### Parameters: 
dict_filepath (str): Where to load dictionary from
lda_filepath (str): Where to load LDA Model from
index_filepath (str): Where to load/save index to. 
create_index (boolean): Whether or not we need to create a new index. 
