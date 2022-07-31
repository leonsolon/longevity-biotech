import argparse
from bs4 import BeautifulSoup
import pandas as pd
import requests


def return_biomarkers_for_disease(biomarker_list, disease, start_date, end_date, pages):
    """
    This function searches for a disease at PubMed and count the appearances of
    biomarkers related to the disease. The list of diseases where extracted from
    http://www.cirion.com/DirectDownload.aspx?nav_id=714&lang_id=E

    :param biomarker_list: list of biomarkers to search in the abstracts of PubMed
    :param disease: the disease to search for at PubMed
    :param start_date: the start date for the papers to search for (year)
    :param end_date: the end date for the papers to search for (year)
    :param pages: number of papers to search for
    :return: dictionary with keys: biomarkers and times of appearance
    """

    # URL for pub med with term, date and page size parameters
    main_url = 'https://pubmed.ncbi.nlm.nih.gov/?term={}&filter=years.{}-{}&format=abstract&size={}'

    # Terms are separated by '+' in PubMed
    search_disease = disease.replace(" ", "+")

    # Send search request
    req = requests.get(main_url.format(search_disease, str(start_date), str(end_date), pages),
                       headers={'User-Agent': 'Mozilla/5.0'})

    # Get the page content
    search_page = req.text

    # Parse content with beautiful soup
    soup = BeautifulSoup(search_page, 'html.parser')

    # Gets all abstract divs. It contains the abstract and keywords, when available
    abstracts = soup.find_all('div', {"class": "abstract"})

    # Creates a dictionary for each biomarker
    result = dict((biomarker, 0) for biomarker in biomarker_list)

    # Counts occurrences of each biomarker on each paper listed
    for biomarker in result.keys():
        for abstract in abstracts:
            abstract = str(abstract).lower().split()
            result[biomarker] += abstract.count(biomarker)

    # Returns a list of biomarkers with count > 0
    return [(biomarker, count) for biomarker, count in result.items() if count > 0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("disease",
                        nargs='?',
                        help="Type the disease to search for. If there is more than one work, enclose with quotes",
                        default='"diabetes mellitus"')

    args = parser.parse_args()

    if args.disease:
        list_biomarkers = pd.read_csv('./data/raw/biomarkers.csv')

        disease = args.disease
        biomarkers_disease = return_biomarkers_for_disease(list_biomarkers.values.flatten(), disease, 2020, 2022, 10)

        print(f'Biomarkers for {disease}: {biomarkers_disease}')
