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

pyladies_pipeline = Pipeline(emails, pre_processing, lda)
```

In the code snippet above, emails, pre_processing, and lda were instantiated and then passed in as parameters to the Pipeline class.

##### Class Parameters:
* steps: List of objects to be applied to the data. Variable length of list.  

#### apply(self, result)
Calls a step in the pipeline. 


## store_data.py 

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


3. docTopicVector.py in the Data_Aquisition... folder. 

Parameters: 

:param {str} lda_model_location:
    Filepath to the LDAModel

End result: The topic vectors for each document will be stored in a separate database. One thing to note is that the _id in this database will also be the unique ID found in the CSV files. So the _id is the same in the emails and topic vectors database. This will be important as we will use this feature when trying to access both sets of information. 

4. similarDoc.py in the Data_Aquisition... folder. 

Parameters: 

:param {str} index_filepath: 
	Location of where to load or save index from/to. 
            
:param {bool} create_index:
	Determines whether or not a new index has to be made

End result: This file finds the nearest neighbors to a particular document or topic vector. We will use this in the future when conducting semantic searches (searches related to the topic vectors of a document and the words being searched). 

5. searchFeatures.py in the Data_Aquisition... folder. 

Parameters: 

:param {boolean} keyword: 
	True if user wants to do a keyword search for the exact word in the text. 
            
:param {boolean} topic_search:
	True if user wants to do a topic search for the exact word in the text
            
:param {varies} *words:
	Words that the user wants to search by. 
            
:param {int} num:
	Number of documents the user wants returned
            
:param {str} dict_filepath: 
	Where to load dictionary from
        
:param {str} lda_filepath: 
	Where to load LDA Model from
        
:param {str} index_filepath: 
	Where to load/save index to. 
        
:param {str} create_index:
	Whether or not we need to create a new index. 

End result: If keyword (bool) is true, then num (int) number of documents that contain the words passed in will be returned. 
If topic_search is true, the num (int) number of documents that are similar to the topic vector of the words will be returned. 
