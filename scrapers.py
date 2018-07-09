#get name+rating from advanced view
# http://www.imdb.com/search/title/?series=tt5296406&count=250&view=advanced&sort=release_date,asc&ref_=tt_eps_rhs_sm
# compare name and append to the dataframe 
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import OrderedDict



#FIRST ALGO// fast one and gives: name len year votes  genre series
def parse_and_get_df2(idn):
    page = requests.get(
        "http://www.imdb.com/search/title/?series={}&count=250&view=advanced&sort=release_date,asc&ref_=tt_eps_rhs_sm".format(idn))
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #parse name of the series
    series=soup.select('h3 > a')
    nams=series[0].get_text().strip()
    #parse name of each episode
    listname=[]
    for name in soup.select('h3 > a'):
        listname.append(name.get_text())
    listname2=listname[1::2]
    #parse length of each episode
    length=[]
    for name in soup.select('p > span.runtime'):
        length.append(name.get_text())
    #parse year
    year=[]
    table=soup.findAll('span', {"class": "lister-item-year text-muted unbold" })
    yearlist=table[1::2]
    for i in yearlist:
        year.append(i.get_text())
    year=[i.replace('(', '').replace(')', '') for i in year] #convert strings to int
    #print(year)
    #parse type of the tv show
    
    x=soup.find('span', {'class':'genre'})
    x=x.get_text().strip()
    #print(x)
    
   #get number of vote
    votes=[]
    z=soup.findAll('span', {'name':'nv'})
    for i in z:
        votes.append(i.get_text())
    #print(votes)
    
    
    finname=listname2[0:len(length)] #this is the shortest list one that is available
    finyear=year[0:len(length)]
    finvotes=votes[0:len(length)]
    #print(finname)
    #print(length)

    df= pd.DataFrame( OrderedDict( (('name', pd.Series(finname)), 
                                    ('len', pd.Series(length)),
                                    ('year', pd.Series(finyear)),
                                    ('votes', pd.Series(finvotes))
                                   ) ) )
    df['genre']=x
    df['series']=nams
    #df['cert']=cert
    
    return df



#Second algo// slower one as it has to go through multiple pages it gives: series name season number rating

def parse_and_get_df(idn):
    page = requests.get("http://www.imdb.com/title/{}/episodes?season=1".format(idn))
    soup = BeautifulSoup(page.content, 'html.parser')
    #get how many seasons are there
    table=soup.find(id="bySeason")
    numofseas=[]
    seasnr=table.findAll('option')
    x=1
    for i in seasnr:
        numofseas.append(x)
        x+=1
    numofseas
    #now i have list of that many seasons i will loop for every of them and create dataframe and then merge it
    name=[]
    ratings=[]
    seasonlist=[]
    epnumbers=[]
    for k in numofseas:
        page = requests.get("http://www.imdb.com/title/{}/episodes?season={}".format(idn,k))
        soup = BeautifulSoup(page.content, 'html.parser')
        
        #check if season is not released yet
        table=soup.findAll('div', {"class":"ipl-rating-star--placeholder"})
        if not table:
            
            #Below give names of episodes
            table=soup.findAll('a', {"itemprop": "name" })
            for i in table:
                #print(i.get_text())
                name.append(i.get_text())
            #Below give ratings numbers
            table=soup.findAll('span', {"class": "ipl-rating-star__rating" })
            ratinglist=table[0::23]
            for i in ratinglist:
                #print(i.get_text())
                ratings.append(i.get_text())
            #Below give season number
            table=soup.findAll('h3', {"itemprop":"name"})
            season=table[1].get_text()[-1]
            for i in range(len(ratinglist)):
                seasonlist.append(season)
            #Below give episode number
            for i in range(len(ratinglist)):
                epnumbers.append(i+1)

    #Below give name of the show
    table=soup.find('a', {"class":"subnav_heading"})
    show=table.get_text()  
    showmulti=[show for i in range(len(name))]

    #create dataframe for the series
    return pd.DataFrame( OrderedDict( (('series', pd.Series(showmulti)), 
                                   ('name', pd.Series(name)), 
                                   ('season', pd.Series(seasonlist)), 
                                   ('number', pd.Series(epnumbers)), 
                                   ('rating', pd.Series(ratings))) ) )
