# api/views.py (modify the existing view)
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render

class PubMedArticlesView(APIView):
    def get(self, request):
        keyword = request.query_params.get('q', 'adhd')
        retmax = int(request.query_params.get('retmax', 10))
        retstart = int(request.query_params.get('retstart', 0))  # new: offset

        # 1. ESearch to get IDs (pass retstart)
        esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        esearch_params = {
            "db": "pubmed",
            "term": keyword,
            "retmode": "json",
            "retmax": retmax,
            "retstart": retstart
        }
        esearch_resp = requests.get(esearch_url, params=esearch_params, timeout=10)
        if esearch_resp.status_code != 200:
            return Response({"error": "Error fetching IDs from PubMed"}, status=status.HTTP_502_BAD_GATEWAY)

        idlist = esearch_resp.json().get("esearchresult", {}).get("idlist", [])
        if not idlist:
            return Response({"articles": []})

        # 2. ESummary for details (same as before)
        esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        esummary_params = {"db": "pubmed", "id": ",".join(idlist), "retmode": "json"}
        esummary_resp = requests.get(esummary_url, params=esummary_params, timeout=10)
        if esummary_resp.status_code != 200:
            return Response({"error": "Error fetching summaries from PubMed"}, status=status.HTTP_502_BAD_GATEWAY)

        esummary = esummary_resp.json().get("result", {})
        uids = esummary.get("uids", [])

        articles = []
        for uid in uids:
            item = esummary.get(uid, {})
            articles.append({
                "pmid": uid,
                "title": item.get("title"),
                "source": item.get("source"),
                "pubdate": item.get("pubdate"),
                "authors": [a["name"] for a in item.get("authors", [])] if item.get("authors") else [],
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            })

        return render(request, "api_articles/articles.html", {"articles": articles})

# from django.shortcuts import render

# def articles_page(request):
#     return render(request, 'api/articles.html')
