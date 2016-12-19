# Florida Poly Degree Catalog Data Scraper
A python script that scrapes the data from [Florida Polytechnic University's Degree Catalog](http://floridapolytechnic.catalog.acalog.com/index.php?catoid=7) and outputs to a JSON file.

## Usage
From the console:
`python scrape.py`


## Configuration
To configure which pages are scraped, modify [concentrations.txt](concentrations.txt).

## Output
When finished, the data is saved in `output.json`

###Format:
```
{
    "Degree": {
        "Concentration": [
            {
                id: the internal id of the course
                number: the official Florida id for the course
                name: human-readable course name
                credits: credit-hours for the course
                description: human-readable description of the course's content
                prereqs: list of prerequisites for the course. A sub-list
                         (i.e. [3890, 2003] below) means that either course can be taken
                         (below equates to "2901 AND 3904 AND (3890 OR 2003) AND 3902")
                coreq: list of length one, containing the co-requisite for the course
                electivesInGroup: the courses that can't be taken at the same time as this one
            },
            ...
        ],
        ...
    },
    ...
}
```

###Example:
```json
{
    "Computer Engineering, B.S.": {
        "Digital Logic Design": [
            {
                "id": 2490,
                "number": "MAC2032",
                "name": "Applied Cryptography",
                "credits": 3,
                "description": "This course covers...",
                "prereqs": [2901, 3904, [3890, 2003], 3902],
                "coreqs": [5223],
                "electivesInGroup": [2883, 1009]
            }
        ]
    }
}
```

## Dependencies
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [html5lib](https://pypi.python.org/pypi/html5lib)

([How to install python packages](https://packaging.python.org/installing/))
