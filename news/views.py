from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup as BSoup
from django.http import HttpResponseServerError
from news.models import Headline

def scrape(request, name):
    try:
        # Clear existing headlines
        Headline.objects.all().delete()

        # Set up session with a user agent
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        session = requests.Session()
        session.headers = headers

        # Construct URL
        url = f"https://www.theonion.com/{name}"

        # Fetch the content
        response = session.get(url)
        response.raise_for_status()  # Raise an exception for bad responses

        # Parse the content with BeautifulSoup
        soup = BSoup(response.content, "html.parser")

        # Extract news articles
        articles = soup.find_all("div", {"class": "sc-cw4lnv-13 hHSpAQ"})

        for article in articles:
            link = article.find("a", {"class": "sc-1out364-0 dPMosf js_link"})["href"]
            title = article.find("h2", {"class": "sc-759qgu-0 cvZkKd sc-cw4lnv-6 TLSoz"}).text
            image = article.find("img")["data-src"]

            # Create and save Headline object
            new_headline = Headline(title=title, url=link, image=image)
            new_headline.save()

        return redirect("../")

    except requests.RequestException as e:
        # Handle request exceptions (e.g., network issues)
        return HttpResponseServerError(f"Error fetching data: {e}")

    except Exception as e:
        # Handle other unexpected exceptions
        return HttpResponseServerError(f"An unexpected error occurred: {e}")

def news_list(request):
    # Retrieve headlines in reverse order
    headlines = Headline.objects.all().order_by('-id')
    context = {"object_list": headlines}
    return render(request, "news/home.html", context)
