from .data_store import data_store

# Function implementation if clear
def clear_v1():

    # Getting data from datastore
    store = data_store.get()
    # Empty out the users and channels
    store['users'] = []
    store['channels'] = []
    store['messages'] = []
    store['message_ids'] = 1
    store['dms'] = []
    store['standups'] = []
    store['stats'] = ""
    # Set data to datastore
    data_store.set(store)

    return {
    }