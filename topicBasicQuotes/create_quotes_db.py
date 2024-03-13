# Create a Mongita database with movie information
import json
from mongita import MongitaClientDisk

quotes = [
    {
      "text": "The only limit to our realization of tomorrow will be our doubts of today.",
      "author": "Franklin D. Roosevelt"
    },
    {
      "text": "In three words I can sum up everything I've learned about life: it goes on.",
      "author": "Robert Frost"
    },
    {
      "text": "The only way to do great work is to love what you do.",
      "author": "Steve Jobs"
    },
    {
      "text": "Life is what happens when you're busy making other plans.",
      "author": "John Lennon"
    },
    {
      "text": "Success is not final, failure is not fatal: It is the courage to continue that counts.",
      "author": "Winston Churchill"
    },
    {
      "text": "The future belongs to those who believe in the beauty of their dreams.",
      "author": "Eleanor Roosevelt"
    },
    {
      "text": "The only impossible journey is the one you never begin.",
      "author": "Tony Robbins"
    },
    {
      "text": "You only live once, but if you do it right, once is enough.",
      "author": "Mae West"
    },
    {
      "text": "Be yourself; everyone else is already taken.",
      "author": "Oscar Wilde"
    },
    {
      "text": "The greatest glory in living lies not in never falling, but in rising every time we fall.",
      "author": "Nelson Mandela"
    },
    {
      "text": "The only way to predict the future is to create it.",
      "author": "Peter Drucker"
    },
    {
      "text": "Do not wait to strike till the iron is hot, but make it hot by striking.",
      "author": "William Butler Yeats"
    },
    {
      "text": "It is never too late to be what you might have been.",
      "author": "George Eliot"
    },
    {
      "text": "Believe you can and you're halfway there.",
      "author": "Theodore Roosevelt"
    },
    {
      "text": "Don't watch the clock; do what it does. Keep going.",
      "author": "Sam Levenson"
    },
    {
      "text": "The only person you are destined to become is the person you decide to be.",
      "author": "Ralph Waldo Emerson"
    },
    {
      "text": "The best way to predict the future is to invent it.",
      "author": "Alan Kay"
    },
    {
      "text": "Success usually comes to those who are too busy to be looking for it.",
      "author": "Henry David Thoreau"
    },
    {
      "text": "Strive not to be a success, but rather to be of value.",
      "author": "Albert Einstein"
    },
    {
      "text": "Don't cry because it's over, smile because it happened.",
      "author": "Dr. Seuss"
    }
]

# create a mongita client connection
client = MongitaClientDisk()

# create a movie database
quotes_db = client.quotes_db

# create a scifi collection
quotes_collection = quotes_db.quotes_collection

# empty the collection
quotes_collection.delete_many({})

# put the movies in the database
quotes_collection.insert_many(quotes)

# make sure the movies are there
print(quotes_collection.count_documents({}))