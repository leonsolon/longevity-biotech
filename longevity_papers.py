import argparse
import pandas as pd
import re
import requests

def search_longevity_papers(page_size):
    """
    This function searches for longevity papers at PubMed. The papers are stored in a csv file with doi as index.
    The good thing about this script is that is does not need any scraper, such as beautiful soup ou selenium.
    PubMed has a format of returning searches as plain text, and we can use simple regular expression to
    retain all the data we need.

    Further work should move the storage to a database such as PostgreSQL.

    :return: dictionary with, doi, title, date and keywords of new papers
    """

    # Read the papers already stored
    try:
        df_papers = pd.read_csv('./data/processed/papers.csv', sep=';')
        doi_set = set(df_papers['doi'].values)
    except:
        print('There are no papers stored in papers.csv')
        doi_set = set()

    # URL for pub med with term, date and page size parameters
    main_url = f'https://pubmed.ncbi.nlm.nih.gov/?term=longevity&format=pubmed&sort=date&size={page_size}'

    # Send request
    req = requests.get(main_url, headers={'User-Agent': 'Mozilla/5.0'})

    # Get the page content
    search_page = req.text

    results = dict()
    results['doi'] = []
    results['title'] = []
    results['date'] = []
    results['keywords'] = []

    matches = re.finditer(pattern='.*?PMID.*?LR.*?(\d{8}).*?TI[\s-]+(.*?)\n.*?LID[\s-]+([^\n]*)\[doi\]', string=search_page, flags=re.DOTALL)

    index = 0

    for match in matches:
        date = match.group(1)
        title = match.group(2).strip()
        doi = match.group(3).strip()

        # This paper is already in the list
        if doi in doi_set:
            continue

        results['date'].append(date)
        results['title'].append(title)
        results['doi'].append(doi)

        whole_match = match.group(0)

        keywords_matches = re.finditer(pattern='.*?(OT|MH)[\s-]+(.*?)\n', string=whole_match, flags=re.DOTALL)

        results['keywords'].append([])

        for index_keywords, keyword_match in enumerate(keywords_matches):
            keyword = keyword_match.group(2).strip()
            results['keywords'][index].append(keyword)

        index += 1

    # Returns a list of biomarkers with count > 0
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("page_size",
                        nargs='?',
                        help="The number of papers to show. PubMed accepts 10,20,50,100,200...",
                        default='200')

    args = parser.parse_args()

    new_papers = search_longevity_papers(args.page_size)

    new_papers_df = pd.DataFrame(new_papers)

    if len(new_papers_df) > 0:
        print(f'New Papers: {new_papers_df}')
    else:
        print(f'There are no new papers.')
        exit(0)

    try:
        df_papers = pd.read_csv('./data/processed/papers.csv', sep=';')
        df_papers = pd.concat([df_papers, new_papers_df])
    except:
        df_papers = new_papers_df

    df_papers.to_csv('./data/processed/papers.csv', index=False, encoding='UTF-8', sep=';')


