from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div',attrs={'id':'main'})
row = table.find_all('div',attrs={'class':'lister-item mode-advanced'})

row_length = len(row)

temp = [] #initiating a list 

for i in range(0, row_length):
#insert the scrapping process here
    
     # untuk mendapatkan judul film
    titles=table.select('h3.lister-item-header a')[i].text
    
    # untuk mendapatkan rating imdb

    imdbs=table.select('div.ratings-bar div strong')[i].text

    # untuk mendapatkan metascores

    try :
        metascores=table.select('div[class="ratings-bar"]')[i].text
        metascores=metascores.split('\n')[35].strip()

    except:
        metascores=0

    # untuk mendapatkan jumlah votes

    votes=table.select('p[class="sort-num_votes-visible"]')[i].text
    votes=votes.split('\n')[2]

        
    temp.append((titles,imdbs,metascores,votes))


#change into dataframe
data = pd.DataFrame(temp, columns = ('title','imdb','metascores','votes'))

#insert data wrangling here

data['imdb']=data['imdb'].astype('float64')
data['metascores']=data['metascores'].astype('int64')
data['votes']=data['votes'].str.replace(',',"")
data['votes']=data['votes'].astype('int64')

top7_movie_by_metascore=data[['title','metascores']]
top7_movie_by_metascore=top7_movie_by_metascore.sort_values(by='metascores',ascending=False).head(7)
top7_movie_by_metascore

top7_movie_by_imdb_score=data[['title','imdb']]
top7_movie_by_imdb_score=top7_movie_by_imdb_score.sort_values(by='imdb',ascending=False).head(7)
top7_movie_by_imdb_score

top7_movie_by_votes=data[['title','votes']]
top7_movie_by_votes=top7_movie_by_votes.sort_values(by='votes',ascending=False).head(7)
top7_movie_by_votes

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{data["metascores"].mean().round(2)}' #be careful with the " and ' 

	# generate plot top7_movie_by_votes

	fig,cx = plt.subplots()
	barh=cx.barh(y=top7_movie_by_votes['title'],width= top7_movie_by_votes['votes'], align='center')
	cx.invert_yaxis()  # labels read top-to-bottom
	cx.set_xlabel('Votes')
	cx.set_title('2021 - Top 7 Movie by Votes')

	# Label with specially formatted floats
	cx.bar_label(barh)
	cx.set_xlim(right=650000)  # adjust xlim to fit labels


	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)