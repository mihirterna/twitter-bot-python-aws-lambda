import os
import requests
from pathlib import Path
import tweepy

ROOT = Path(__file__).resolve().parents[0]
DICTIONARY_API_FULL_URL = "https://dictionaryapi.com/api/v3/references/thesaurus/json/"
DICTIONARY_API_COLLEGIATE_FULL_URL = "https://dictionaryapi.com/api/v3/references/collegiate/json/"
NEW_WORD_FULL_URL = "https://random-word-api.herokuapp.com/word?number=1"


def get_tweet(static_tweet_file, iterated_tweet_file):
    """Get tweet to post from CSV file"""

    """with open(tweets_file) as csvfile:
        reader = csv.DictReader(csvfile)
        possible_tweets = [row["tweet"] for row in reader]

    if excluded_tweets:
        recent_tweets = [status_object.text for status_object in excluded_tweets]
        possible_tweets = [tweet for tweet in possible_tweets if tweet not in recent_tweets]

    selected_tweet = random.choice(possible_tweets)"""
    newWordResponse = requests.get(NEW_WORD_FULL_URL)
    newWord=newWordResponse.json()[0]
    print("new word today "+ newWord)
    wordMeaning = requests.get(DICTIONARY_API_COLLEGIATE_FULL_URL+ newWord +"?key=cc02002c-d50c-461e-8f9b-c0bb547af5fa")
    wordMeaning = wordMeaning.json()
    #and wordMeaning[0]["fl"] != None
    FinalTweet=None
    if wordMeaning != None and wordMeaning[0] != None and type(wordMeaning[0]) is dict and wordMeaning[0]["fl"] != None:
        print("meaning = "+ wordMeaning[0]["fl"])
        FinalTweet=static_tweet_file.replace("$word",newWord.capitalize())
        count = 1
        for meaning in wordMeaning:
            if count==3:
                break
            count=count+1
            if meaning != None and meaning["fl"] != None:
                wordDefination = iterated_tweet_file.replace("$fl",meaning["fl"].capitalize())
                for shortDef in meaning["shortdef"]:
                    wordDefination += "\n-" + shortDef.capitalize()
                FinalTweet+=wordDefination
        #Getting Synonym and antonym
        synonyms = requests.get(DICTIONARY_API_FULL_URL+ newWord +"?key=d8d7dfa3-d0eb-4222-8eea-77c516068485")
        synonyms = synonyms.json()
        if synonyms != None and synonyms[0] != None and type(synonyms[0]) is dict and synonyms[0]["meta"] != None and synonyms[0]["meta"]["syns"] != None:
            synonymsList = synonyms[0]["meta"]["syns"]
            maxSize = min(2, len(synonymsList))
            FinalTweet+="\nSynonyms : "
            for i in range(maxSize):
                FinalTweet+="  "+synonymsList[0][i]
        else:
            print("No Synonym found for word= "+ newWord)
            FinalTweet=get_tweet(static_tweet_file, iterated_tweet_file)

    else: 
        print("wrong word= "+ newWord)
        FinalTweet=get_tweet(static_tweet_file, iterated_tweet_file)
    return FinalTweet


def lambda_handler(event, context):
    print("Get credentials")
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    print("Authenticate")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    print("Get tweet from csv file")
    #recent_tweets = api.user_timeline()[:3]
    static_tweet_file = open(ROOT / "STATIC_TWEET.txt","r").read()
    iterated_tweet_file = open(ROOT / "ITERATED_TEXT.txt","r", encoding="utf8").read()
    tweet = get_tweet(static_tweet_file, iterated_tweet_file)
    print(f"Post tweet: {tweet}")
    if tweet != None:
        api.update_status(tweet)
        return {"statusCode": 200, "tweet": tweet}
