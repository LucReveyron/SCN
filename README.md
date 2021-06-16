# SCN
Prototype of framework to manage network of smart cameras. The server can do : human detection, tracking and recogniction. 

## Installation
Clone the project :
```bash
git clone https://github.com/LucReveyron/SCN.git

```
Uses [poetry](https://python-poetry.org/docs/) as a package manager. Only requires the standard `pyproject.toml` file.

Install poetry (if not installed)
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Then simply run in the `scn` folder:

```
poetry install
```

## Usage

Activate the poetry environement :
```bash
poetry shell
```
Launch the backend in the 'scn' folder:
```bash
poetry run python app.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
