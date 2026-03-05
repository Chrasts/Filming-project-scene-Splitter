# Film Scene Character Splitter

Python code for generating **character-specific scene breakdowns** from a czech film production scene list (scénosled).

The script processes a cleaned production spreadsheet and creates a separate Excel file for each character containing all scenes in which the character appears.

This tool was developed as part of a film production workflow, where departments such as costume design needed quick access to scenes for individual characters.

---

## Context

Film productions typically maintain a master spreadsheet called a **scene list (scénosled)**.
Each row represents a scene and includes information such as:

* scene number
* shooting day
* location
* scene description
* characters present
* costume notes
* extras

For production departments (especially **costume and make-up**), it is often necessary to quickly obtain:

> all scenes in which a specific character appears, ordered by shooting day.

Manually filtering the master spreadsheet for each character is time-consuming, especially on larger productions.

---

## Data Preparation

The input data used in this project were **cleaned and standardized beforehand**.

The original scene list contained typical real-world inconsistencies, such as:

* mixed separators in the character column (spaces / commas)
* formatting variations
* non-uniform text entries

A preprocessing step was therefore performed to produce a **cleaned Excel file (`scenosled_cleaned.xlsx`)** with consistent column names and formatting.

The script in this repository assumes that this preprocessing step has already been completed.

Because different productions may structure their scene lists differently, **the script is tailored to this specific dataset structure**.
For other projects, column names or parsing logic may need to be adjusted.

---

## Input Structure

The script expects a cleaned Excel file with columns similar to:

| Column             | Description                                 |
| ------------------ | ------------------------------------------- |
| `cislo_obrazu`     | scene number                                |
| `den`              | shooting day information (contains `DEN n`) |
| `INT/EXT`          | interior/exterior                           |
| `misto`            | location                                    |
| `dej`              | scene description                           |
| `postavy`          | characters appearing in the scene           |
| `kostymy`          | costume notes                               |
| `komparz`          | extras                                      |

Example:

| cislo_obrazu | den              | misto          | dej           | postavy         |
| ------------ | ---------------- | -------------- | ------------- | --------------- |
| 12           | DEN 3            | Police station | interrogation | ANNA, POLICISTA |

---

## What the Script Does

The script performs the following steps:

1. Load the cleaned Excel scene list
2. Extract character names from the **`postavy` column**
3. Normalize inconsistent separators (commas and spaces)
4. Identify all scenes in which each character appears
5. Extract the shooting day (`DEN n`)
6. Sort scenes by:

   * shooting day
   * scene number
7. Export a **separate Excel file for each character**

---

## Output

The script generates a directory containing one spreadsheet per character.

Example:

```
output/characters/
    ANNA.xlsx
    PETR.xlsx
    POLICISTA.xlsx
```

Each file contains:

* all scenes where the character appears
* rows ordered chronologically by shooting day and scene number

These files can be directly used by production departments for planning and preparation.

---

## Project Structure

```
film-scene-character-splitter/

data/
    scenosled_cleaned.xlsx

src/
    split_characters.py

output/
    characters/

README.md
```

---

## Technologies

* Python
* pandas
* openpyxl

---

## Usage

Run the script:

```
python src/split_characters.py
```

The script reads the Excel file defined in the code and writes output files to the `output/characters` directory.

