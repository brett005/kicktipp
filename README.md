# kicktipp
Calculates the best soccer tips based on latest betting odds.

## Dependencies
* Python 3.x
* [BeautifulSoup 4](https://pypi.python.org/pypi/beautifulsoup4/) (needed for parsing HTML)

## Precaution
This tool currently only works with the following [kicktipp.de](https://www.kicktipp.de/) rules:

|      | Tendency | Goal Difference | Exact Result |
| ---- | -------: | --------------: | -----------: |
| Win  | 2        | 3               | 4            |
| Draw | 2        | -               | 4            |

## Install
Sample installation under [Arch Linux](https://www.archlinux.org/).
```
sudo pacman -S python python-beautifulsoup4
git clone https://github.com/oompf/kicktipp.git
```

## Usage
```
cd kicktipp
./kicktipp.py
```
