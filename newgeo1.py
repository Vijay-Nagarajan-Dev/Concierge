from flask import Flask, render_template, redirect, request, session
from flask_session import Session 
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy import distance
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests, json
import pandas as pd
import openai
# importing Flask and other modules
from flask import Flask, request, render_template
 
# Flask constructor
app = Flask(__name__)  
 

@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
      # getting input with name = fname in HTML form
       user_query= request.form.get("myInput")
       user_query = str(user_query)
       gmapk = "AIzaSyB6jfBi0r8myfeGf3gjcESW7egQhgzuIJM"
       openai.api_key = "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"
       url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
       r = requests.get(url + 'query=' + user_query + '&key=' + gmapk)
       x = r.json()
       result_array = x['results']
       name = []
       rank = []
       rating = []
       sentences = [user_query]
       res = {}
       for i in range (len(result_array)):
          y = result_array[i]['name']
          name.append(y)
          rating.append(result_array[i]['rating']) 

         
       for i in range (len(name)):
          res[name[i]] = rating[i]       
       sorted_res = sorted(res.items(), key=lambda x:x[1])
       sorted_res.reverse()
       n = []
       for q in range(len(sorted_res)):
          n.append(sorted_res[q][0])
       if len(n) > 2:
          del n[3:]
       for l in range(len(n)):
          completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Write me a sentence describing what and where the " +n[l]+" is and what would make it a good tourist spot, but do not use the name of the place in the description"}])
          gptsen = completion.choices[0].message.content
          gptsen= str(gptsen)
          sentences.append(gptsen)    
       model = SentenceTransformer('bert-base-nli-mean-tokens')
       sentence_embeddings = model.encode(sentences)
       sentence_embeddings.shape
       cosineStuff = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])
       cosineStuff = str(cosineStuff)
       cosineStuff = cosineStuff.replace("[", "").replace("]", "").split()
       for j in range(len(cosineStuff)):
          cosineStuff[j] = float(cosineStuff[j])
          
       dictionaryofanswers = {}
       for i in range (len(n)):
        dictionaryofanswers[n[i]] = cosineStuff[i]       
       dev = sorted(dictionaryofanswers.items(), key=lambda x:x[1])
       answer = dev[len(dev)-1]
       answer = answer[0]
       
       locationDescription = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content":"Write a small, yet descriptive paragraph describing what and where " + answer + " is and why it qould be great if you want to go to " + user_query}])
       description = locationDescription.choices[0].message.content 
       description = str(description)
       
       return "Your lucky location is " + str(answer) + ". " + description 
    return render_template("index.html")
 
if __name__=='__main__':
   app.run(debug=True) 