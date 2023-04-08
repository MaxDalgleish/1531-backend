import pickle
import os
'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': [], 
    'channels': [], 
    'messages': [], 
    'dms': [], 
    'standups': [],
    'message_ids': 1,
    'stats': ""
}

## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    # When the server starts up for the first time
    def __init__(self):
        
        global initial_object

        # If the file exists
        if os.path.exists('data_store.p') is True:
        
            # Open the data and read
            with open('data_store.p', 'rb') as FILE:
                initial_object = pickle.load(FILE)
                
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        
        self.__store = store
        
        # Store the data
        with open('data_store.p', 'wb') as FILE:
            pickle.dump(store, FILE)
        
print('Loading Datastore...')

global data_store
data_store = Datastore()
