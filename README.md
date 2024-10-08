# uchchaaran

A text-to-speech (TTS) system using concatenative synthesis to generate speech for Devanagari-script (mainly Hindi and Bhojpuri) languages. It combines pre-recorded audio units for natural, clear speech output.

## Instructions

```console
# Initialize and activate a Python virtual environment (optional).

# Run the following to install the dependencies.
# Or run your system specific command to install.
$ pip install -r requirements.txt

# Generate the frequency.json and syllables.txt files in ./data
$ python main.py

# Generate the split audio units in ./data/devanagari_syllable_dataset_split
$ python audio.py

# Play the audio fragments inside `./data/devanagari_syllable_dataset_split`
```

## Dev Instructions

```
$ uv venv
$ source ./.venv/bin/activate
$ uv pip compile pyproject.toml -o requirements.txt
$ uv pip sync requirements.txt
```
