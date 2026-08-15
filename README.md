# Dynasty Algorithm

A small Python simulation for modelling a monarch's life, succession, children, disease, and mortality over time.

The simulator is nameless by design: you provide a checklist of basic facts for the current ruler, and it advances the dynasty one year at a time. Each living person ages, may become ill, may recover or die, and eligible rulers may have children. When a monarch dies, the oldest living child inherits; if no heir remains, the dynasty ends.

## Starting ruler checklist

Choose the basic facts you already know about the current monarch:

- Current monarch age, such as `--age 32`.
- Current monarch sex, either `--sex female` or `--sex male`.
- Existing children, repeated as `--child AGE:SEX`, such as `--child 12:female --child 8:male`.
- Simulation length, such as `--years 80`.
- Optional disease risk, such as `--disease-risk 0.06`.

## Quick start

```bash
python -m dynasty_algorithm --age 32 --sex female --child 12:female --child 8:male --years 80
```

## Options

```bash
python -m dynasty_algorithm --help
```

Useful flags include:

- `--age`: current age of the ruler.
- `--sex`: current sex of the ruler.
- `--child`: existing child in `AGE:SEX` form; repeat it for multiple children.
- `--years`: maximum years to simulate.
- `--disease-risk`: base yearly chance that a person contracts a disease.




## Run it inside GitHub Actions without downloading

If you want people to use the simulator without downloading anything, have them run the **Run Dynasty Simulation** workflow in GitHub. They only fill out the ruler checklist, not developer-style tuning options.

1. Open the repository on GitHub.
2. Select the **Actions** tab.
3. Choose **Run Dynasty Simulation**.
4. Click **Run workflow**.
5. Fill in the monarch checklist fields: age, sex, existing children, years, and disease risk.
6. Open the completed workflow run and read the result in the job summary.

For existing children, use comma-separated `AGE:SEX` entries, such as `12:female,8:male`. The workflow also uploads `simulation-output.txt` as an artifact for easy sharing.

## Sharing it with other people

The simplest way to share this project is to put the repository on GitHub, GitLab, or another Git host and send people the repository link. They can then download or clone it and run the simulator locally.

### If they have Git installed

```bash
git clone <repository-url>
cd DynastyAlgorithm
python -m dynasty_algorithm --age 32 --sex female --child 12:female --years 80
```

### If they do not have Git installed

1. Open the repository page in a browser.
2. Choose **Code** and then **Download ZIP**.
3. Unzip the downloaded file.
4. Open a terminal in the unzipped folder.
5. Run:

```bash
python -m dynasty_algorithm --age 32 --sex female --child 12:female --years 80
```

### What they need installed

- Python 3.10 or newer.
- No third-party Python packages are required.

## Development

Run tests with:

```bash
python -m unittest discover -s tests
```
