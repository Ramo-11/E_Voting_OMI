# E-Voting System

This project was written in Python and it demonstrates the implementation of a secure E-voting system as part of CSCI 55500 course

## Contributors
- Omar Abdelalim (oabdela.iu.edu)
- Ismail Bibers (ibibers@iu.edu)
- Max Comer (wcomer@iu.edu)

## Requirements
- Python 3.11
- install pycryptodome library
```bash
pip install pycryptodome
```

## Installation

Clone this repository

```bash
git clone https://github.com/Ramo-11/E_Voting_OMI.git
```

## Running
- open 5 different terminals
- run collectors 1 and 2, then admin, then voters 1, 2, and 3
```bash
python server/collector1.py
python server/collector2.py
python server/admin.py
python client/voters/voter1.py
python client/voters/voter2.py
python client/voters/voter3.py
```